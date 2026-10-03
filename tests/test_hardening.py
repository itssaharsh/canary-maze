"""Hostile input at the trust boundaries. Each case here was demonstrated by an
independent security review against a temp ledger before it was fixed."""
from __future__ import annotations

import importlib.util
import io
import sys
import time
from pathlib import Path

import pytest

from canarymaze.app import SELFTEST_HEADER, create_app
from canarymaze.ingest import SIG_HEADER, TS_HEADER, sign, verify
from canarymaze.ledger import Ledger

ROOT = Path(__file__).resolve().parents[1]
BOT = {"User-Agent": "Mozilla/5.0 (compatible; GPTBot/1.2)"}
OTHER = {"User-Agent": "Mozilla/5.0 (compatible; ClaudeBot/1.0)"}
KEY = "k" * 48
IP = "198.51.100.7"


@pytest.fixture
def surface(tmp_path, monkeypatch):
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    monkeypatch.setenv("CANARY_SELFTEST_TOKEN", "s3cr3t-probe-token")
    monkeypatch.setenv("CANARY_INGEST_KEY", KEY)
    monkeypatch.delenv("CANARY_OPERATOR_NETS", raising=False)
    monkeypatch.delenv("CANARY_TRUST_PROXY", raising=False)
    db = str(tmp_path / "t.sqlite3")
    return create_app(db_path=db).test_client(), db


def _mint(client, headers=BOT, ip="198.51.100.7"):
    body = client.get("/m/q3-supplier-review", headers=headers,
                      environ_overrides={"REMOTE_ADDR": ip}).get_data(as_text=True)
    i = body.index("/c/") + 3
    return body[i:body.index("/", i)]


# --- a header must not be able to remove a request from the ledger ------------

@pytest.mark.parametrize("value", ["é", "日本", "café-token", "\x00\xff"])
def test_a_non_ascii_selftest_header_cannot_opt_out_of_being_observed(surface, value):
    """hmac.compare_digest raises TypeError on a non-ASCII str. The header went
    straight into it, so ONE header with no knowledge of the token made the canary
    route 500 and the fetch vanish - the opt-out the docs say cannot exist."""
    client, db = surface
    secret = _mint(client)
    r = client.get(f"/c/{secret}/q3-supplier-review",
                   headers={**OTHER, SELFTEST_HEADER: value.encode("utf-8").decode("latin-1")},
                   environ_overrides={"REMOTE_ADDR": "192.0.2.50"})
    assert r.status_code == 200
    led = Ledger(db)
    c = led.counts()
    led.close()
    assert c["sightings_organic"] == 1, "the fetch must be recorded, and as organic"
    assert c["sightings_selftest"] == 0


def test_ingest_verify_never_raises_on_hostile_signature_or_timestamp():
    payload = {"kind": "mint"}
    ts = str(time.time())
    for sig, t in (("é" * 64, ts), (sign(payload, ts, KEY), "nan"),
                   (sign(payload, ts, KEY), "inf"), (sign(payload, ts, KEY), "é"),
                   ("", ts), (sign(payload, ts, KEY), "")):
        ok, why = verify(payload, t, sig, KEY)
        assert ok is False and why


def test_a_nan_timestamp_with_a_valid_signature_is_still_refused():
    """`abs(now - nan) > 300` is False, so a NaN timestamp passed the freshness
    check forever: a captured request could be replayed at any time."""
    payload = {"kind": "mint"}
    assert verify(payload, "nan", sign(payload, "nan", KEY), KEY)[0] is False


def test_a_signed_report_cannot_be_replayed(surface):
    client, db = surface
    payload = {"kind": "gate", "via": "vercel"}
    ts = str(time.time())
    h = {TS_HEADER: ts, SIG_HEADER: sign(payload, ts, KEY)}
    assert client.post("/ingest", json=payload, headers=h).status_code == 200
    for _ in range(4):
        assert client.post("/ingest", json=payload, headers=h).status_code == 409
    led = Ledger(db)
    n = led.counts()["humans_turned_away"]
    led.close()
    assert n == 1, "one signed report must move the counter once, however often it is delivered"


def test_an_oversized_ingest_body_is_refused_before_it_is_parsed(surface):
    client, _ = surface
    r = client.post("/ingest", data=b"x" * (300 * 1024), content_type="application/json")
    assert r.status_code == 413


# --- what a request may append to an append-only ledger ----------------------

def test_a_fetch_of_a_secret_that_was_never_issued_stores_nothing(surface):
    """The route still answers 200 for everyone. But the ledger is append-only, so
    300 requests for /c/never-minted-N/ with a 12 kB user-agent used to write 300
    permanent rows that travel in every later bundle."""
    client, db = surface
    r = client.get("/c/never-minted-0000/q3-supplier-review", headers=BOT,
                   environ_overrides={"REMOTE_ADDR": "192.0.2.50"})
    assert r.status_code == 200
    led = Ledger(db)
    c = led.counts()
    led.close()
    assert c["requests"] == 0 and c["sightings_organic"] == 0


def test_user_agent_and_path_are_capped_at_the_write_boundary(tmp_path):
    led = Ledger(str(tmp_path / "t.sqlite3"))
    led.record_request(method="GET", path="/m/" + "p" * 5000, status=200, ip="198.51.100.7",
                       ua="Bot/" + "u" * 20000, ctx_id="c")
    row = led.rows("request")[0]
    led.close()
    assert len(row["ua"]) <= 600 and row["ua"].endswith("[truncated]")
    assert len(row["path"]) <= 600 and row["path"].endswith("[truncated]")
    assert len(row["raw_line"]) < 2000


def test_a_user_agent_cannot_forge_a_second_log_line(tmp_path):
    """The access-log line is what the viewer shows as 'the record'. A quote or a
    newline in the user-agent used to render as a second entry on the same line."""
    led = Ledger(str(tmp_path / "t.sqlite3"))
    led.record_request(method="GET", path="/m/x\n203.0.113.9 - - \"GET /forged\" 200",
                       status=200, ip="198.51.100.7",
                       ua='x" 200 5 "-" "Forged/1.0\r\ninjected', ctx_id="c")
    line = led.rows("request")[0]["raw_line"]
    led.close()
    assert "\n" not in line and "\r" not in line
    assert line.count('"') == 6, "exactly the three quoted fields the format has"


# --- the address the ledger believes -----------------------------------------

def test_cf_connecting_ip_is_ignored_unless_the_peer_is_cloudflared(tmp_path, monkeypatch):
    """With CANARY_TRUST_PROXY=cloudflare the app believed CF-Connecting-IP from
    ANY peer, while listening on every interface - so anyone who could reach the
    port chose the network the ledger recorded for them, the operator's included."""
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    monkeypatch.setenv("CANARY_TRUST_PROXY", "cloudflare")
    monkeypatch.setenv("CANARY_OPERATOR_NETS", "203.0.113.0/24")
    db = str(tmp_path / "t.sqlite3")
    client = create_app(db_path=db).test_client()

    # a LAN peer claiming to be the operator's network
    client.get("/m/q3-supplier-review", headers={**BOT, "CF-Connecting-IP": "203.0.113.5"},
               environ_overrides={"REMOTE_ADDR": "192.168.0.57"})
    # cloudflared itself, on loopback, reporting a real client
    client.get("/m/vendor-risk-register", headers={**OTHER, "CF-Connecting-IP": "198.51.100.9"},
               environ_overrides={"REMOTE_ADDR": "127.0.0.1"})
    led = Ledger(db)
    rows = led.rows("request")
    led.close()
    assert rows[0]["ip_net"] == "192.168.0.0/24" and rows[0]["origin"] == "organic", \
        "a header from a non-loopback peer must not choose the recorded network"
    assert rows[1]["ip_net"] == "198.51.100.0/24"


def test_the_server_binds_loopback_unless_told_otherwise():
    src = (ROOT / "canarymaze" / "app.py").read_text(encoding="utf-8")
    assert 'host="0.0.0.0"' not in src, "the tunnel dials 127.0.0.1; nothing else needs the port"


# --- the edge answers HEAD ----------------------------------------------------

def test_the_edge_answers_head_on_a_canary_url(monkeypatch):
    """The Flask surface returned 200 to HEAD and the edge returned 501, so a
    fetcher that probes before it reads was refused on the public surface only."""
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    api = ROOT / "site" / "api"
    sys.path.insert(0, str(api))
    try:
        spec = importlib.util.spec_from_file_location("canary_surface_head", api / "surface.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(str(api))
    assert hasattr(mod.handler, "do_HEAD")

    class Fake(mod.handler):
        def __init__(self):            # no socket: drive the method directly
            self.path = "/c/deadbeefdeadbeef/q3-supplier-review"
            self.headers = {"User-Agent": "curl/8.5.0"}
            self.wfile = io.BytesIO()
            self.sent = []
        def send_response(self, code): self.sent.append(code)
        def send_header(self, *a): pass
        def end_headers(self): pass

    monkeypatch.setattr(mod, "report", lambda payload: True)
    f = Fake()
    f.do_HEAD()
    assert f.sent == [200] and f.wfile.getvalue() == b"", "HEAD: 200 and no body"


# --- scripts that delete things ------------------------------------------------

def test_make_demo_cannot_be_pointed_at_another_ledger(tmp_path):
    """demo.sh removes its database before it starts. It took the path from
    $CANARY_DB, which every operator shell that sources .env exports - so `make
    demo` deleted the live ledger and wrote the seeded replay in its place."""
    import os
    import shutil
    import subprocess
    work = tmp_path / "repo"
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(
        ".git", "ledgers", "demo", "graphify-out", "*.sqlite3*", "bundles", "__pycache__",
        ".pytest_cache", "hackathon-idea", "site"))
    precious = work / "precious.sqlite3"
    led = Ledger(str(precious))
    led.record_request(method="GET", path="/m/x", status=200, ip="198.51.100.7",
                       ua="GPTBot/1.2", ctx_id="c")
    led.close()
    env = {**os.environ, "CANARY_DB": str(precious), "CANARY_ALLOW_DEV_SALT": "1"}
    r = subprocess.run(["bash", "scripts/demo.sh"], cwd=work, env=env,
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
    led = Ledger(str(precious))
    n = led.counts()["requests"]
    led.close()
    assert precious.exists() and n == 1, "the ledger named by CANARY_DB must be untouched"
    assert (work / "demo.sqlite3").exists()


# --- a missing salt must not mint silently ------------------------------------

def test_the_edge_refuses_to_mint_on_the_committed_development_salt(monkeypatch):
    """The dev salt is PUBLIC - it is in this repository. The Flask surface refuses
    to start without CANARY_SALT; the edge function had no such guard, so a Vercel
    environment missing the variable would serve every visitor a canary link
    computed from the committed salt. The ledger (which has the real salt) then
    answers every report 409, report() discards it, and the surface collects
    nothing while raising nothing. Anyone could also compute the canary owed to a
    guessable context and fetch it without ever seeing the page."""
    import importlib.util
    api = ROOT / "site" / "api"
    sys.path.insert(0, str(api))
    try:
        spec = importlib.util.spec_from_file_location("canary_surface_salt", api / "surface.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(str(api))

    monkeypatch.delenv("CANARY_SALT", raising=False)
    monkeypatch.delenv("CANARY_ALLOW_DEV_SALT", raising=False)
    status, _, body, payload = mod.respond("/m/q3-supplier-review", dict(BOT), IP, "https://h")
    assert "/c/" not in body, "no canary link may be issued under the committed salt"
    assert payload is None, "and nothing may be reported"
    assert status == 200, "the page itself is still served"

    monkeypatch.setenv("CANARY_SALT", "f" * 64)
    _, _, body, payload = mod.respond("/m/q3-supplier-review", dict(BOT), IP, "https://h")
    assert "/c/" in body and payload is not None, "with a real salt it mints as usual"


def test_creating_the_app_without_a_salt_refuses_to_start(monkeypatch):
    """The guard was only ever called directly by a test, so deleting its call in
    create_app left every test green."""
    monkeypatch.delenv("CANARY_SALT", raising=False)
    monkeypatch.delenv("CANARY_ALLOW_DEV_SALT", raising=False)
    with pytest.raises(SystemExit):
        create_app()


def test_a_real_salt_actually_changes_the_secret(monkeypatch):
    """load_salt returning the dev salt unconditionally left every test passing."""
    from canarymaze import mint
    monkeypatch.setenv("CANARY_SALT", "a" * 64)
    with_salt = mint.secret_for("/m/x", "ctx", epoch="2026-10-03")
    monkeypatch.delenv("CANARY_SALT")
    assert with_salt != mint.secret_for("/m/x", "ctx", epoch="2026-10-03")


# --- a record must say what happened ------------------------------------------

def test_a_head_request_is_recorded_as_head_with_no_body(surface):
    """Flask serves HEAD through the GET view, and the route hard-coded
    method='GET' and size=len(body). A link checker probing with HEAD - W3C
    checklink does, and it is in our own census - produced a record saying the
    client downloaded 606 bytes by GET. The viewer presents that line as 'the full
    record, unedited'."""
    client, db = surface
    secret = _mint(client)
    r = client.head(f"/c/{secret}/q3-supplier-review", headers=OTHER,
                    environ_overrides={"REMOTE_ADDR": "192.0.2.50"})
    assert r.status_code == 200 and r.get_data() == b""
    led = Ledger(db)
    row = led.rows("request")[-1]
    led.close()
    assert row["method"] == "HEAD", f"recorded as {row['method']}"
    assert ' 200 0 ' in row["raw_line"], f"body size must be 0: {row['raw_line']}"


def test_the_viewer_and_export_routes_answer(surface):
    """Neither was covered: making /export.json raise, or GET / return 404, left
    all tests passing."""
    client, _ = surface
    assert client.get("/").status_code == 200
    r = client.get("/export.json")
    assert r.status_code == 200 and "counts" in r.get_json()
