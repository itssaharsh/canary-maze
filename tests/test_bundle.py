"""The bundle is the whole wedge: a reader who does not trust the operator must be
able to check it. These tests attack that property."""
import json
from pathlib import Path

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
    b["leaves"] = [bundle.header_leaf(b["format"], b["note"], b["counts"])] + \
                  [bundle.leaf(r) for t in bundle.PROOF_TABLES for r in b["rows"][t]]
    b["root"] = bundle.merkle_root(b["leaves"])
    ok, problems = bundle.verify(b)
    # leaves and root were recomputed honestly, so only the semantic check catches it
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


# --- regression tests for the three tamperings a fresh review got past verify ---

def test_editing_counts_is_caught(populated):
    """counts and note were outside the hash: setting sightings_organic to 4127 on
    a shipped bundle returned clean. They are the two fields a reader reads."""
    b = bundle.build(populated)
    b["counts"]["sightings_organic"] = 4127
    ok, problems = bundle.verify(b)
    assert not ok
    assert any("header" in p for p in problems), problems


def test_editing_the_note_is_caught(populated):
    b = bundle.build(populated)
    b["note"] = "independently audited"
    ok, problems = bundle.verify(b)
    assert not ok
    assert any("header" in p for p in problems), problems


def test_duplicating_the_trailing_row_cannot_preserve_the_root(populated):
    """CVE-2012-2459. Appending a copy of the last row and its leaf used to re-root
    to a byte-identical value, so a published root did not pin the row count."""
    b = bundle.build(populated)
    before = b["root"]
    b["rows"]["sighting"].append(dict(b["rows"]["sighting"][-1]))
    b["leaves"].append(b["leaves"][-1])
    assert bundle.merkle_root(b["leaves"]) != before, \
        "a duplicated trailing leaf must change the root"
    ok, problems = bundle.verify(b)
    assert not ok, problems


def test_merkle_root_binds_the_leaf_count():
    three = ["aa" * 32, "bb" * 32, "cc" * 32]
    four = three + [three[-1]]
    assert bundle.merkle_root(three) != bundle.merkle_root(four)


def test_leaf_and_node_hashes_live_in_different_domains():
    """Without separation a leaf hash can masquerade as an internal node."""
    assert bundle.LEAF_TAG != bundle.NODE_TAG


def test_a_sighting_with_no_mint_row_is_caught(populated):
    """A bundle asserting a secret moved A to B, with nothing showing it was ever
    issued to A, used to verify clean."""
    b = bundle.build(populated)
    b["rows"]["mint"] = []
    b["leaves"] = [bundle.header_leaf(b["format"], b["note"], b["counts"])] + \
                  [bundle.leaf(r) for t in bundle.PROOF_TABLES for r in b["rows"][t]]
    b["root"] = bundle.merkle_root(b["leaves"])
    ok, problems = bundle.verify(b)
    assert not ok
    assert any("no mint row" in p for p in problems), problems


def test_a_sighting_dated_before_its_mint_is_caught(populated):
    b = bundle.build(populated)
    b["rows"]["sighting"][0]["ts"] = "2020-01-01T00:00:00Z"
    b["leaves"] = [bundle.header_leaf(b["format"], b["note"], b["counts"])] + \
                  [bundle.leaf(r) for t in bundle.PROOF_TABLES for r in b["rows"][t]]
    b["root"] = bundle.merkle_root(b["leaves"])
    ok, problems = bundle.verify(b)
    assert not ok
    assert any("before its mint" in p for p in problems), problems


def test_the_canonical_form_is_portable_between_python_and_javascript():
    """bundle.py and viewer/verify.js must produce identical bytes, or the page's
    verification fails on a valid bundle. The specific hazard: json.dumps(275.0)
    is '275.0' in Python and JSON.stringify(275.0) is '275' in JavaScript, so
    every value is normalised to a tagged string first."""
    from canarymaze.bundle import _norm, canonical
    assert _norm(275.0) == "f:275.000000"      # JS: (275.0).toFixed(6)
    assert _norm(0.0) == "f:0.000000"
    assert _norm(3) == "i:3"
    assert _norm(None) == "n:"
    assert _norm(True) == "b:1"
    assert _norm("x") == "s:x"
    # keys sorted, no whitespace, every value a tagged string
    assert canonical({"b": 2, "a": 1.5}) == b'{"a":"f:1.500000","b":"i:2"}'
    # non-ASCII escaped, as Python's ensure_ascii=True and the JS escape both do
    assert canonical({"k": "café"}) == b'{"k":"s:caf\\u00e9"}'


def test_the_javascript_verifier_names_every_check_the_python_one_makes():
    """A cheap guard that runs without Node: the wording of each check exists on
    both sides. It proves nothing about behaviour - a review rightly pointed out
    that this was the ONLY thing "pinning the two together" and that it never
    executed the JavaScript. tests/test_js_parity.py now runs verify.js for real;
    this stays for the reader who has no Node installed."""
    js = (Path(__file__).resolve().parents[1] / "viewer" / "verify.js").read_text(encoding="utf-8")
    for marker in ("does not match its leaf", "the root does not match the leaves",
                   "names one context on both sides", "no mint row in this bundle",
                   "with no matching request row", "before its mint",
                   "header (format, note, counts, viewer)", "plus one header leaf",
                   "does not commit to what the page displays",
                   "is not the request rows under the root",
                   "a secret that was never issued cannot be published"):
        assert marker in js, f"viewer/verify.js is missing the {marker!r} check"
    assert "crypto.subtle.digest" in js, "the page must actually hash, not read a verdict"


def test_the_two_verifiers_declare_the_same_format():
    """The JavaScript compares the format exactly, so the constant has to move in
    both files at once or every bundle fails in the browser."""
    import re
    from canarymaze.bundle import FORMAT
    js = (Path(__file__).resolve().parents[1] / "viewer" / "verify.js").read_text(encoding="utf-8")
    assert re.search(r'var FORMAT = "([^"]+)"', js).group(1) == FORMAT
