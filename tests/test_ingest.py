"""The signed edge hand-off: the only write path not driven by a real connection.

An unauthenticated version would let anyone post invented rows into an
append-only ledger, where they could never be removed - a far worse hole than the
edge-blocking it exists to work around. So the attacks come first here.
"""
from __future__ import annotations

import time

import pytest

from canarymaze.app import create_app
from canarymaze.ingest import SIG_HEADER, TS_HEADER, sign
from canarymaze.ledger import Ledger

KEY = "i" * 48
BOT = {"User-Agent": "Mozilla/5.0 (compatible; GPTBot/1.2)"}
BROWSER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0) Chrome/129.0",
           "Accept-Language": "en-GB,en;q=0.9", "Sec-Fetch-Mode": "navigate"}


@pytest.fixture
def surface(tmp_path, monkeypatch):
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    monkeypatch.setenv("CANARY_INGEST_KEY", KEY)
    monkeypatch.delenv("CANARY_OPERATOR_NETS", raising=False)
    monkeypatch.delenv("CANARY_SELFTEST_TOKEN", raising=False)
    db = str(tmp_path / "t.sqlite3")
    return create_app(db_path=db).test_client(), db


def post(client, payload, *, key=KEY, ts=None, sig=None):
    ts = ts if ts is not None else str(time.time())
    sig = sig if sig is not None else sign(payload, ts, key)
    return client.post("/ingest", json=payload,
                       headers={TS_HEADER: ts, SIG_HEADER: sig})


PATH = "/m/q3-supplier-review"


def owed(headers=BOT, ip="198.51.100.7", path=PATH) -> str:
    """The secret this context really is owed - what an honest edge would report.
    The ledger holds the salt and checks, so an invented one is refused."""
    from canarymaze import mint
    from canarymaze.context import derive
    return mint.secret_for(path, derive(headers, ip), epoch=mint.salt_epoch())


def mint_payload(**over):
    p = {"kind": "mint", "method": "GET", "path": PATH,
         "ip": "198.51.100.7", "headers": dict(BOT), "via": "vercel", "size": 500}
    p.update(over)
    p.setdefault("secret", owed(p["headers"], p["ip"], p["path"]) if p["kind"] == "mint"
                 else owed())
    return p


# --- the attacks ------------------------------------------------------------

def test_unsigned_request_is_refused(surface):
    client, db = surface
    r = client.post("/ingest", json=mint_payload())
    assert r.status_code == 403
    assert Ledger(db).counts()["requests"] == 0


def test_wrong_key_is_refused(surface):
    client, db = surface
    r = post(client, mint_payload(), key="w" * 48)
    assert r.status_code == 403
    assert Ledger(db).counts()["requests"] == 0


def test_tampering_with_the_body_after_signing_is_refused(surface):
    """The classic: sign something harmless, send something else."""
    client, db = surface
    honest = mint_payload()
    ts = str(time.time())
    sig = sign(honest, ts, KEY)
    forged = mint_payload(ip="203.0.113.9", headers={"User-Agent": "SomeoneElse/1.0"})
    r = client.post("/ingest", json=forged, headers={TS_HEADER: ts, SIG_HEADER: sig})
    assert r.status_code == 403
    assert Ledger(db).counts()["requests"] == 0


def test_a_captured_request_cannot_be_replayed_later(surface):
    client, db = surface
    old = str(time.time() - 4000)
    p = mint_payload()
    r = post(client, p, ts=old, sig=sign(p, old, KEY))
    assert r.status_code == 403
    assert Ledger(db).counts()["requests"] == 0


def test_ingest_is_disabled_when_no_key_is_configured(tmp_path, monkeypatch):
    """Fail closed. A surface that never configured a key must not accept rows."""
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    monkeypatch.delenv("CANARY_INGEST_KEY", raising=False)
    db = str(tmp_path / "t.sqlite3")
    client = create_app(db_path=db).test_client()
    r = client.post("/ingest", json=mint_payload())
    assert r.status_code == 404
    assert Ledger(db).counts()["requests"] == 0


# --- the behaviour ----------------------------------------------------------

def test_a_valid_handoff_is_recorded_and_names_its_edge(surface):
    client, db = surface
    r = post(client, mint_payload())
    assert r.status_code == 200 and r.get_json()["recorded"] is True

    led = Ledger(db)
    c = led.counts()
    assert c["requests"] == 1 and c["mints"] == 1
    assert c["requests_reported"] == 1, "a forwarded row must not look directly observed"
    assert c["requests_direct"] == 0
    row = led.rows("request")[0]
    assert row["via"] == "vercel"
    assert row["ip_net"] == "198.51.100.0/24", "the CLIENT's network, not the edge's"
    led.close()


def test_the_gate_runs_here_not_at_the_edge(surface):
    """A human forwarded by the edge is still excluded, and still stores nothing.
    Moving that decision outward would put the privacy guarantee on a machine we
    do not control."""
    client, db = surface
    r = post(client, mint_payload(headers=dict(BROWSER)))
    assert r.status_code == 200
    assert r.get_json()["recorded"] is False

    led = Ledger(db)
    c = led.counts()
    assert c["requests"] == 0, "a human must never reach storage, forwarded or not"
    assert c["humans_turned_away"] == 1
    led.close()


def test_a_forwarded_canary_fetch_by_another_context_is_a_sighting(surface):
    client, db = surface
    post(client, mint_payload())
    other = {"User-Agent": "Mozilla/5.0 (compatible; ClaudeBot/1.0)"}
    r = post(client, mint_payload(kind="canary", secret=owed(),
                                  path=f"/c/{owed()}/q3-supplier-review",
                                  headers=other, ip="192.0.2.50"))
    assert r.status_code == 200

    led = Ledger(db)
    assert led.counts()["sightings_organic"] == 1
    led.close()


def test_the_same_context_refetching_is_not_a_sighting(surface):
    client, db = surface
    post(client, mint_payload())
    r = post(client, mint_payload(kind="canary", secret=owed(),
                                  path=f"/c/{owed()}/q3-supplier-review"))
    assert r.status_code == 200
    led = Ledger(db)
    assert led.counts()["sightings_organic"] == 0
    led.close()


# --- the ledger does not take the edge's word for it --------------------------

def test_a_mint_report_with_an_invented_secret_is_refused(surface):
    """The edge is signed, not trusted. The ledger holds the salt, so it checks
    that the reported secret is the one this context is owed for this path; a
    compromised or buggy edge cannot bind arbitrary strings to contexts."""
    client, db = surface
    r = post(client, mint_payload(secret="abc123abc123abc1"))
    assert r.status_code == 409
    led = Ledger(db)
    c = led.counts()
    led.close()
    assert c["requests"] == 0 and c["mints"] == 0, "refused BEFORE anything is written"


def test_a_report_whose_context_the_ledger_derives_differently_is_refused(surface):
    """If the edge and the ledger ever disagree about a context again (F-0006),
    the row is refused loudly instead of quietly binding a secret to a context
    that nothing can ever match."""
    client, db = surface
    r = post(client, mint_payload(ctx="0123456789ab"))
    assert r.status_code == 409 and "context" in r.get_json()["error"]
    assert Ledger(db).counts()["requests"] == 0


def test_a_report_of_an_unknown_kind_is_refused(surface):
    client, db = surface
    assert post(client, mint_payload(kind="something-else")).status_code == 400
    assert Ledger(db).counts()["requests"] == 0


def test_a_forwarded_fetch_of_a_secret_never_issued_stores_nothing(surface):
    client, db = surface
    r = post(client, mint_payload(kind="canary", secret="f" * 16,
                                  path="/c/" + "f" * 16 + "/q3-supplier-review"))
    assert r.status_code == 200 and r.get_json()["recorded"] is False
    assert Ledger(db).counts()["requests"] == 0
