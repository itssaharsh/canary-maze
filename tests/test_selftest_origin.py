"""The operator's own probes must never be published as third-party evidence.

Before this existed, `origin` was a single process-wide config value, so a
verification curl against the live surface was written to the ledger as
'organic' and shown to a reader as traffic from someone else. That is the exact
overclaim the product exists to refuse, so it gets its own test file.
"""
from __future__ import annotations

import os

import pytest

from canarymaze.app import SELFTEST_HEADER, create_app
from canarymaze.export import export
from canarymaze.ledger import Ledger

BOT = {"User-Agent": "Mozilla/5.0 (compatible; GPTBot/1.2)"}
OTHER_BOT = {"User-Agent": "Mozilla/5.0 (compatible; ClaudeBot/1.0)"}
TOKEN = "s3cr3t-probe-token"


@pytest.fixture
def surface(tmp_path, monkeypatch):
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    monkeypatch.setenv("CANARY_SELFTEST_TOKEN", TOKEN)
    db = str(tmp_path / "t.sqlite3")
    app = create_app(db_path=db)
    return app.test_client(), db


def _mint(client, headers):
    """Issue a secret to one context and return it."""
    r = client.get("/m/q3-supplier-review", headers=headers)
    body = r.get_data(as_text=True)
    i = body.index("/c/") + 3
    return body[i:body.index("/", i)]


def test_probe_with_token_is_recorded_as_selftest(surface):
    client, db = surface
    secret = _mint(client, BOT)
    client.get(f"/c/{secret}/q3-supplier-review",
               headers={**OTHER_BOT, SELFTEST_HEADER: TOKEN})

    led = Ledger(db)
    counts = led.counts()
    assert counts["sightings_selftest"] == 1
    assert counts["sightings_organic"] == 0, "a self-test must never inflate organic"
    led.close()


def test_claim_discloses_a_selftest_sighting(surface):
    client, db = surface
    secret = _mint(client, BOT)
    client.get(f"/c/{secret}/q3-supplier-review",
               headers={**OTHER_BOT, SELFTEST_HEADER: TOKEN})

    led = Ledger(db)
    payload = export(led)
    led.close()
    assert payload["state"] == "sighting"
    assert "operator's own probe" in payload["claim"], payload["claim"]


def test_header_without_the_token_cannot_opt_out_of_being_observed(surface):
    """The threat runs this way round: a fetcher that could mark ITSELF a
    self-test would stay out of the organic count, letting the observed party
    opt out of observation. Only the operator's secret token may do that."""
    client, db = surface
    secret = _mint(client, BOT)
    client.get(f"/c/{secret}/q3-supplier-review",
               headers={**OTHER_BOT, SELFTEST_HEADER: "guessed-wrong"})

    led = Ledger(db)
    counts = led.counts()
    assert counts["sightings_selftest"] == 0
    assert counts["sightings_organic"] == 1, "a forged header must not downgrade evidence"
    led.close()


def test_unconfigured_token_fails_closed_to_organic(tmp_path, monkeypatch):
    """With no token set, the header is inert. Failing open would mean anyone
    who guessed the header name could erase themselves from the evidence."""
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    monkeypatch.delenv("CANARY_SELFTEST_TOKEN", raising=False)
    db = str(tmp_path / "t.sqlite3")
    client = create_app(db_path=db).test_client()
    secret = _mint(client, BOT)
    client.get(f"/c/{secret}/q3-supplier-review",
               headers={**OTHER_BOT, SELFTEST_HEADER: "anything"})

    led = Ledger(db)
    assert led.counts()["sightings_organic"] == 1
    assert led.counts()["sightings_selftest"] == 0
    led.close()
