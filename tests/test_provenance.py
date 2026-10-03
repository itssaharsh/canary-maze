"""A secret the operator handed out by hand is no longer evidence of sharing.

The server cannot tell a crawler that found a canary URL on its own from a
fetcher that was given the URL by the operator: both are real third-party
requests with no operator marker, so both are recorded as `origin='organic'`.
Before this existed, the only thing separating them was a JSON file that one
script read and the viewer did not - so a fetcher following a link the operator
had pasted into a chat product would have been published as an organic sighting.

The operator's act of publishing is now a row in the ledger, and classification
only ever moves in the conservative direction: organic -> paste, never back.
"""
from __future__ import annotations

import sqlite3

import pytest

from canarymaze import bundle
from canarymaze.export import export
from canarymaze.ledger import Ledger


@pytest.fixture
def led(tmp_path):
    l = Ledger(str(tmp_path / "t.sqlite3"))
    yield l
    l.close()


def _mint(led, secret="a" * 16, ts="2026-10-03T10:00:00Z"):
    rid = led.record_request(method="GET", path="/m/x", status=200, ip="198.51.100.7",
                             ua="operator-probe/1.0", ctx_id="ctx-mint", ts=ts)
    led.record_mint(secret=secret, ctx_id="ctx-mint", path="/m/x", salt_epoch="e",
                    request_id=rid, ts=ts)
    return rid


def _sight(led, mint_rid, secret="a" * 16, ts="2026-10-03T10:05:00Z", ctx="ctx-seen",
           origin="organic", ip="192.0.2.50"):
    rid = led.record_request(method="GET", path=f"/c/{secret}/x", status=200, ip=ip,
                             ua="ThirdPartyFetcher/2.0", ctx_id=ctx, origin=origin, ts=ts)
    return led.record_sighting(secret=secret, mint_ctx_id="ctx-mint", seen_ctx_id=ctx,
                               mint_request_id=mint_rid, seen_request_id=rid,
                               delta_s=300.0, origin=origin, ts=ts)


def test_an_unpublished_secret_stays_organic(led):
    _sight(led, _mint(led))
    c = led.counts()
    assert (c["sightings_organic"], c["sightings_paste"]) == (1, 0)


def test_a_fetch_after_the_operator_published_the_secret_is_paste_not_organic(led):
    rid = _mint(led)
    led.record_published(secret="a" * 16, method="handed to a public fetch service",
                         ts="2026-10-03T10:01:00Z")
    _sight(led, rid, ts="2026-10-03T10:05:00Z")
    c = led.counts()
    assert (c["sightings_organic"], c["sightings_paste"]) == (0, 1), \
        "a fetcher following a link the operator published must never count as organic"


def test_publishing_after_the_fact_does_not_rewrite_what_was_organic(led):
    """The rule is about what was true when the fetch happened. Publishing a secret
    later cannot retroactively downgrade - or launder - an earlier sighting."""
    rid = _mint(led)
    _sight(led, rid, ts="2026-10-03T10:05:00Z")
    led.record_published(secret="a" * 16, method="included in a published bundle",
                         ts="2026-10-03T12:00:00Z")
    c = led.counts()
    assert (c["sightings_organic"], c["sightings_paste"]) == (1, 0)


def test_a_selftest_sighting_on_a_published_secret_stays_selftest(led):
    rid = _mint(led)
    led.record_published(secret="a" * 16, method="m", ts="2026-10-03T10:01:00Z")
    _sight(led, rid, origin="selftest")
    c = led.counts()
    assert (c["sightings_selftest"], c["sightings_paste"], c["sightings_organic"]) == (1, 0, 0)


def test_published_is_append_only(led):
    _mint(led)
    led.record_published(secret="a" * 16, method="m")
    for sql in ("UPDATE published SET method='edited'", "DELETE FROM published"):
        with pytest.raises(sqlite3.IntegrityError):
            led.db.execute(sql)


def test_a_secret_that_was_never_issued_cannot_be_published(led):
    with pytest.raises(ValueError):
        led.record_published(secret="f" * 16, method="m")


def test_the_viewer_payload_says_paste_and_keeps_what_was_recorded(led):
    rid = _mint(led)
    led.record_published(secret="a" * 16, method="handed to a public fetch service",
                         ts="2026-10-03T10:01:00Z")
    _sight(led, rid)
    payload = export(led)
    s = payload["sightings"][0]
    assert s["origin"] == "paste"
    assert s["recorded_origin"] == "organic"
    assert "published" in payload["claim"].lower(), payload["claim"]
    assert payload["counts"]["sightings_organic"] == 0


def test_the_headline_sighting_is_the_strongest_class_present(led):
    """With several sightings, the page must lead with the strongest evidence it
    has - and must not lead with an organic one that does not exist."""
    rid = _mint(led)
    _sight(led, rid, ctx="ctx-self", origin="selftest", ts="2026-10-03T10:02:00Z")
    rid2 = _mint(led, secret="b" * 16, ts="2026-10-03T10:10:00Z")
    _sight(led, rid2, secret="b" * 16, ctx="ctx-org", ts="2026-10-03T10:20:00Z")
    payload = export(led)
    assert [s["origin"] for s in payload["sightings"]] == ["organic", "selftest"]
    assert "operator's own probe" not in payload["claim"]


def test_published_rows_travel_in_the_bundle_and_are_tamper_evident(led):
    rid = _mint(led)
    led.record_published(secret="a" * 16, method="handed to a public fetch service",
                         ts="2026-10-03T10:01:00Z")
    _sight(led, rid)
    b = bundle.build(led)
    assert b["rows"]["published"][0]["secret"] == "a" * 16
    assert bundle.verify(b) == (True, [])

    b["rows"]["published"][0]["ts"] = "2026-10-03T23:59:00Z"      # try to make it organic
    ok, problems = bundle.verify(b)
    assert not ok and any("published" in p for p in problems)


def test_removing_the_published_row_from_a_bundle_is_caught(led):
    """The obvious attack on a disclosure: delete it. The header binds the counts
    and the leaf list binds the row count, so the bundle no longer verifies."""
    rid = _mint(led)
    led.record_published(secret="a" * 16, method="m", ts="2026-10-03T10:01:00Z")
    _sight(led, rid)
    b = bundle.build(led)
    b["rows"]["published"] = []
    ok, _ = bundle.verify(b)
    assert not ok
