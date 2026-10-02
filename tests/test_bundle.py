"""The bundle is the whole wedge: a reader who does not trust the operator must be
able to check it. These tests attack that property."""
import json

import pytest

from canarymaze import bundle
from canarymaze.detect import on_canary_request


@pytest.fixture()
def populated(ledger):
    mint_req = ledger.record_request(method="GET", path="/m/x", status=200,
                                     ip="20.171.207.14", ua="GPTBot/1.2",
                                     ctx_id="ctxA", ts="2026-10-03T11:04:12Z")
    ledger.record_mint(secret="s" * 16, ctx_id="ctxA", path="/m/x",
                       salt_epoch="2026-10-03", request_id=mint_req,
                       ts="2026-10-03T11:04:12Z")
    seen = ledger.record_request(method="GET", path="/c/s/x", status=200,
                                 ip="104.28.52.9", ua="Chrome/124", ctx_id="ctxB",
                                 ts="2026-10-03T11:08:47Z")
    on_canary_request(ledger, secret="s" * 16, seen_ctx_id="ctxB",
                      seen_request_id=seen, origin="seeded")
    return ledger


def test_a_clean_bundle_verifies(populated):
    b = bundle.build(populated)
    ok, problems = bundle.verify(b)
    assert ok and problems == []


def test_verification_needs_no_server_and_no_network(populated, tmp_path, monkeypatch):
    p = bundle.write(bundle.build(populated), tmp_path / "b.json")
    populated.close()                      # the server and its database are gone

    import socket
    def no_network(*a, **k):               # any socket use fails the test loudly
        raise AssertionError("verification must not touch the network")
    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)

    ok, problems = bundle.verify_file(p)
    assert ok, problems


def test_editing_a_row_is_caught_and_the_row_is_named(populated):
    b = bundle.build(populated)
    b["rows"]["request"][1]["ua"] = "Something Else/1.0"
    ok, problems = bundle.verify(b)
    assert not ok
    assert any("request id=2" in p for p in problems), problems


def test_editing_a_leaf_is_caught_by_the_root(populated):
    b = bundle.build(populated)
    b["leaves"][0] = "0" * 64
    ok, problems = bundle.verify(b)
    assert not ok
    assert any("root does not match" in p for p in problems), problems


def test_adding_a_row_without_a_leaf_is_caught(populated):
    b = bundle.build(populated)
    b["rows"]["sighting"].append(dict(b["rows"]["sighting"][0], id=999))
    ok, problems = bundle.verify(b)
    assert not ok
    assert any("leaves for" in p for p in problems), problems


def test_a_sighting_naming_one_context_twice_is_rejected(populated):
    b = bundle.build(populated)
    s = b["rows"]["sighting"][0]
    s["seen_ctx_id"] = s["mint_ctx_id"]
    b["leaves"] = [bundle.leaf(r) for t in bundle.PROOF_TABLES for r in b["rows"][t]]
    b["root"] = bundle.merkle_root(b["leaves"])
    ok, problems = bundle.verify(b)
    # leaves and root were recomputed, so only the semantic check can catch this
    assert not ok
    assert any("names one context on both sides" in p for p in problems), problems


def test_the_laundered_table_never_reaches_the_bundle(populated):
    populated.db.execute(
        "INSERT INTO laundered (secret, candidate_text, score, ts) VALUES (?,?,?,?)",
        ("s" * 16, "a paraphrase a model liked", 0.91, "2026-10-03T12:00:00Z"))
    populated.db.commit()
    b = bundle.build(populated)
    assert "laundered" not in b["rows"]
    assert "paraphrase" not in json.dumps(b)


def test_an_empty_ledger_still_produces_a_verifiable_bundle(ledger):
    b = bundle.build(ledger)
    ok, problems = bundle.verify(b)
    assert ok and b["counts"]["sightings_organic"] == 0


def test_canonical_form_is_order_independent():
    assert bundle.canonical({"b": 2, "a": 1}) == bundle.canonical({"a": 1, "b": 2})


def test_an_unknown_format_is_refused():
    ok, problems = bundle.verify({"format": "something-else/9"})
    assert not ok and "unknown bundle format" in problems[0]


def test_merkle_root_changes_when_any_leaf_changes():
    a = bundle.merkle_root(["aa" * 32, "bb" * 32, "cc" * 32])
    b = bundle.merkle_root(["aa" * 32, "bb" * 32, "cd" * 32])
    assert a != b
