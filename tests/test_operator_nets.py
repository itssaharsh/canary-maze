"""The operator's own network is self-test traffic, whatever it sends.

The secret token was not enough on its own. It is opt-in, and opt-in controls get
forgotten: they were forgotten three separate times here, the third time while
diagnosing the second, which left four sightings in a live ledger that were all
the operator's own curl. Recognising the operator's network needs nothing of the
client and so cannot be forgotten mid-command.
"""
from __future__ import annotations

import pytest

from canarymaze.app import SELFTEST_HEADER, create_app
from canarymaze.ledger import Ledger

BOT = {"User-Agent": "Mozilla/5.0 (compatible; GPTBot/1.2)"}
OTHER = {"User-Agent": "Mozilla/5.0 (compatible; ClaudeBot/1.0)"}
TOKEN = "s3cr3t-probe-token"


@pytest.fixture
def surface(tmp_path, monkeypatch):
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    monkeypatch.setenv("CANARY_SELFTEST_TOKEN", TOKEN)
    monkeypatch.setenv("CANARY_OPERATOR_NETS", "203.0.113.0/24")
    db = str(tmp_path / "t.sqlite3")
    return create_app(db_path=db).test_client(), db


def _mint(client, headers, ip):
    r = client.get("/m/q3-supplier-review", headers=headers,
                   environ_overrides={"REMOTE_ADDR": ip})
    body = r.get_data(as_text=True)
    i = body.index("/c/") + 3
    return body[i:body.index("/", i)]


def test_operator_network_is_selftest_without_any_header(surface):
    """The whole point: a bare curl from the operator's own machine, with no
    token and nothing special about it, must not become evidence."""
    client, db = surface
    secret = _mint(client, BOT, "198.51.100.7")
    client.get(f"/c/{secret}/q3-supplier-review", headers=OTHER,
               environ_overrides={"REMOTE_ADDR": "203.0.113.42"})

    led = Ledger(db)
    c = led.counts()
    assert c["sightings_selftest"] == 1
    assert c["sightings_organic"] == 0, "the operator's own curl is not evidence"
    led.close()


def test_a_stranger_is_still_organic(surface):
    client, db = surface
    secret = _mint(client, BOT, "198.51.100.7")
    client.get(f"/c/{secret}/q3-supplier-review", headers=OTHER,
               environ_overrides={"REMOTE_ADDR": "192.0.2.99"})

    led = Ledger(db)
    assert led.counts()["sightings_organic"] == 1
    assert led.counts()["sightings_selftest"] == 0
    led.close()


def test_a_stranger_cannot_claim_the_operator_network(surface):
    """The network is read from the connection, never from a header, so a
    fetcher cannot assert its way out of the organic count."""
    client, db = surface
    secret = _mint(client, BOT, "198.51.100.7")
    client.get(f"/c/{secret}/q3-supplier-review",
               headers={**OTHER, "X-Forwarded-For": "203.0.113.42"},
               environ_overrides={"REMOTE_ADDR": "192.0.2.99"})

    led = Ledger(db)
    assert led.counts()["sightings_organic"] == 1, "XFF must not grant operator status"
    led.close()


def test_unset_operator_nets_changes_nothing(tmp_path, monkeypatch):
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    monkeypatch.setenv("CANARY_SELFTEST_TOKEN", TOKEN)
    monkeypatch.delenv("CANARY_OPERATOR_NETS", raising=False)
    db = str(tmp_path / "t.sqlite3")
    client = create_app(db_path=db).test_client()
    secret = _mint(client, BOT, "198.51.100.7")
    client.get(f"/c/{secret}/q3-supplier-review", headers=OTHER,
               environ_overrides={"REMOTE_ADDR": "203.0.113.42"})

    led = Ledger(db)
    assert led.counts()["sightings_organic"] == 1
    led.close()


def test_the_token_still_works_from_elsewhere(surface):
    """Operator networks do not replace the token; they cover the case where it
    was forgotten. Probing from a cafe still needs the header."""
    client, db = surface
    secret = _mint(client, BOT, "198.51.100.7")
    client.get(f"/c/{secret}/q3-supplier-review",
               headers={**OTHER, SELFTEST_HEADER: TOKEN},
               environ_overrides={"REMOTE_ADDR": "192.0.2.99"})

    led = Ledger(db)
    assert led.counts()["sightings_selftest"] == 1
    led.close()
