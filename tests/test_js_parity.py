"""Run the JavaScript verifier for real, against bundles the Python side built.

The page's one differentiating claim is that it recomputes every hash itself. That
only holds if viewer/verify.js and canarymaze/bundle.py produce identical bytes
for every input - and until this file existed, the only test "pinning the two
together" grepped verify.js for marker strings. It never executed it. A divergence
between the two would have shipped as a page that says "Verification failed" on an
honest bundle, or worse, one that says "Verified" on a bundle Python rejects.

Skipped when Node is not installed; a judge without Node loses nothing else.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from canarymaze import bundle
from canarymaze.ledger import Ledger

ROOT = Path(__file__).resolve().parents[1]
VERIFY_JS = ROOT / "viewer" / "verify.js"
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="node is not installed")

HARNESS = r"""
const fs = require('fs');
globalThis.window = globalThis;                       // verify.js is an IIFE over `window`
(0, eval)(fs.readFileSync(process.argv[2], 'utf8'));
const b = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
window.CanaryVerify.verifyBundle(b).then(
  r => { console.log(JSON.stringify(r)); },
  e => { console.log(JSON.stringify({ok: false, problems: ['threw: ' + e]})); });
"""


def js_verify(b: dict, tmp_path: Path) -> dict:
    (tmp_path / "harness.js").write_text(HARNESS, encoding="utf-8")
    (tmp_path / "bundle.json").write_text(json.dumps(b), encoding="utf-8")
    out = subprocess.run([NODE, str(tmp_path / "harness.js"), str(VERIFY_JS),
                          str(tmp_path / "bundle.json")],
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


def build(tmp_path: Path, *, note: str = "", ua_b: str = "ThirdParty/2.0") -> dict:
    led = Ledger(str(tmp_path / "t.sqlite3"))
    r1 = led.record_request(method="GET", path="/m/x", status=200, ip="198.51.100.7",
                            ua="Mozilla/5.0 (compatible; GPTBot/1.2)", ctx_id="ctx-a",
                            ts="2026-10-03T10:00:00Z", via="vercel")
    led.record_mint(secret="a" * 16, ctx_id="ctx-a", path="/m/x", salt_epoch="e",
                    request_id=r1, ts="2026-10-03T10:00:00Z")
    led.record_published(secret="a" * 16, method="handed to a fetch service",
                         ts="2026-10-03T10:01:00Z")
    r2 = led.record_request(method="GET", path="/c/" + "a" * 16 + "/x", status=200,
                            ip="2001:db8::1", ua=ua_b, ctx_id="ctx-b",
                            ts="2026-10-03T10:04:35Z")
    led.record_sighting(secret="a" * 16, mint_ctx_id="ctx-a", seen_ctx_id="ctx-b",
                        mint_request_id=r1, seen_request_id=r2, delta_s=275.0,
                        origin="organic", ts="2026-10-03T10:04:35Z")
    b = bundle.build(led, note=note)
    led.close()
    return b


def test_javascript_and_python_agree_on_an_ordinary_bundle(tmp_path):
    b = build(tmp_path)
    assert bundle.verify(b) == (True, [])
    r = js_verify(b, tmp_path)
    assert r["ok"] is True, r["problems"]
    assert r["root"] == b["root"]
    assert r["rows"] == len(b["leaves"])


def test_they_agree_when_a_user_agent_is_not_ascii(tmp_path):
    """A user-agent is attacker-chosen text. Quotes, a backslash, accents, CJK and
    an astral-plane character must all hash identically on both sides."""
    b = build(tmp_path, ua_b='Bot "q" \\ back/slash über 中文 \U0001f600   end')
    assert bundle.verify(b) == (True, [])
    r = js_verify(b, tmp_path)
    assert r["ok"] is True, r["problems"]
    assert r["root"] == b["root"]


def test_they_agree_when_the_note_is_not_ascii(tmp_path):
    """The note sits INSIDE the header object, which is serialised as nested JSON
    before it is hashed - a different code path from a row's string fields, and
    the one where the two implementations escaped differently."""
    b = build(tmp_path, note="live surface — café, 日本 …")
    assert bundle.verify(b) == (True, [])
    r = js_verify(b, tmp_path)
    assert r["ok"] is True, r["problems"]
    assert r["root"] == b["root"]


def test_they_agree_on_an_empty_ledger(tmp_path):
    led = Ledger(str(tmp_path / "e.sqlite3"))
    b = bundle.build(led)
    led.close()
    assert bundle.verify(b) == (True, [])
    r = js_verify(b, tmp_path)
    assert r["ok"] is True, r["problems"]
    assert r["root"] == b["root"]


def test_javascript_catches_an_edited_row_and_names_it(tmp_path):
    b = build(tmp_path)
    b["rows"]["request"][1]["ua"] = "SomeoneElse/9.9"
    py_ok, py_problems = bundle.verify(b)
    r = js_verify(b, tmp_path)
    assert py_ok is False and r["ok"] is False
    assert any("request id=2" in p for p in r["problems"]), r["problems"]
    assert any("request id=2" in p for p in py_problems)


def test_javascript_catches_an_edited_header_count(tmp_path):
    b = build(tmp_path)
    b["counts"]["sightings_organic"] = 4127
    assert bundle.verify(b)[0] is False
    r = js_verify(b, tmp_path)
    assert r["ok"] is False and any("header" in p for p in r["problems"])


def test_javascript_catches_a_backdated_disclosure(tmp_path):
    """Editing the `published` row is how a paste-triggered sighting would be
    passed off as organic. Both verifiers must refuse it."""
    b = build(tmp_path)
    b["rows"]["published"][0]["ts"] = "2026-10-03T23:59:59Z"
    assert bundle.verify(b)[0] is False
    r = js_verify(b, tmp_path)
    assert r["ok"] is False and any("published" in p for p in r["problems"])


def test_javascript_refuses_a_published_secret_that_was_never_minted(tmp_path):
    b = build(tmp_path)
    b["rows"]["mint"] = []
    r = js_verify(b, tmp_path)
    assert r["ok"] is False


# --- four divergences an independent review found by sweeping both verifiers ---

def test_they_agree_on_a_delete_character(tmp_path):
    """U+007F. Python's ensure_ascii escapes it; the JavaScript escaped from U+0080.
    Any client can plant one with a single request - `GET /c/abc%7Fdef/x` - and the
    ledger is append-only, so every later bundle from that ledger verified in
    Python and failed in the browser, permanently."""
    b = build(tmp_path, ua_b="Bot\x7fwith-a-delete")
    assert bundle.verify(b) == (True, [])
    r = js_verify(b, tmp_path)
    assert r["ok"] is True, r["problems"]
    assert r["root"] == b["root"]


def test_both_refuse_an_unknown_format_version(tmp_path):
    """JavaScript accepted anything beginning 'canary-maze-bundle/'."""
    b = build(tmp_path)
    b["format"] = "canary-maze-bundle/99-anything"
    # re-seal the header so the ONLY thing wrong with this bundle is its version
    b["leaves"][0] = bundle.header_leaf(b["format"], b["note"], b["counts"], b.get("viewer", ""))
    b["root"] = bundle.merkle_root(b["leaves"])
    assert bundle.verify(b)[0] is False
    r = js_verify(b, tmp_path)
    assert r["ok"] is False and any("format" in p for p in r["problems"]), r["problems"]


def test_javascript_lookups_are_not_fooled_by_prototype_names(tmp_path):
    """`minted` and `reqIds` were plain objects, so a sighting citing the secret
    "constructor" and the request ids "valueOf" / "toString" found inherited
    properties and passed with no mint or request rows at all."""
    led = Ledger(str(tmp_path / "p.sqlite3"))
    b = bundle.build(led)
    led.close()
    b["rows"]["sighting"] = [{"id": 1, "secret": "constructor", "mint_ctx_id": "a",
                              "seen_ctx_id": "b", "mint_request_id": "valueOf",
                              "seen_request_id": "toString", "delta_s": 1.0,
                              "origin": "organic", "ts": "2026-10-03T10:00:00Z"}]
    b["leaves"] = [b["leaves"][0], bundle.leaf(b["rows"]["sighting"][0])]
    b["root"] = bundle.merkle_root(b["leaves"])
    py_ok, py_problems = bundle.verify(b)
    r = js_verify(b, tmp_path)
    assert py_ok is False and len(py_problems) >= 3
    assert r["ok"] is False and len(r["problems"]) >= 3, r["problems"]


def test_a_float_survives_a_round_trip_through_javascript(tmp_path):
    """JSON.stringify(JSON.parse(x)) turns `"delta_s": 275.0` into `275`. Python
    decided int-versus-float from the lexeme and then rejected its own bundle;
    JavaScript decided from the field name. Both now decide from the field name."""
    b = build(tmp_path)
    reparsed = json.loads(json.dumps(b).replace('"delta_s": 275.0', '"delta_s": 275'))
    assert isinstance(reparsed["rows"]["sighting"][0]["delta_s"], int)
    assert bundle.verify(reparsed) == (True, [])
    assert js_verify(reparsed, tmp_path)["ok"] is True


# --- the display has to be bound to the root, not just shipped beside it ------

SHOWN_HARNESS = r"""
const fs = require('fs');
globalThis.window = globalThis;
(0, eval)(fs.readFileSync(process.argv[2], 'utf8'));
const d = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
window.CanaryVerify.verifyBundle(d.bundle, d.viewer).then(
  r => { console.log(JSON.stringify(r)); },
  e => { console.log(JSON.stringify({ok: false, problems: ['threw: ' + e]})); });
"""


def js_verify_page(viewer: dict, b: dict, tmp_path: Path) -> dict:
    (tmp_path / "h2.js").write_text(SHOWN_HARNESS, encoding="utf-8")
    (tmp_path / "page.json").write_text(json.dumps({"viewer": viewer, "bundle": b}),
                                        encoding="utf-8")
    out = subprocess.run([NODE, str(tmp_path / "h2.js"), str(VERIFY_JS),
                          str(tmp_path / "page.json")], capture_output=True, text=True,
                         timeout=60)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


def page(tmp_path: Path):
    """What export_all.py ships: the payload the page shows, and the bundle."""
    from canarymaze.export import export
    led = Ledger(str(tmp_path / "page.sqlite3"))
    r1 = led.record_request(method="GET", path="/m/x", status=200, ip="198.51.100.7",
                            ua="Mozilla/5.0 (compatible; GPTBot/1.2)", ctx_id="ctx-a",
                            ts="2026-10-03T10:00:00Z", origin="seeded")
    led.record_mint(secret="a" * 16, ctx_id="ctx-a", path="/m/x", salt_epoch="e",
                    request_id=r1, ts="2026-10-03T10:00:00Z")
    r2 = led.record_request(method="GET", path="/c/" + "a" * 16 + "/x", status=200,
                            ip="192.0.2.9", ua="Chrome/124 café", ctx_id="ctx-b",
                            ts="2026-10-03T10:04:35Z", origin="seeded")
    led.record_sighting(secret="a" * 16, mint_ctx_id="ctx-a", seen_ctx_id="ctx-b",
                        mint_request_id=r1, seen_request_id=r2, delta_s=275.0,
                        origin="seeded", ts="2026-10-03T10:04:35Z")
    with led.snapshot():
        viewer = export(led)
        b = bundle.build(led, viewer=bundle.payload_digest(viewer))
    led.close()
    return viewer, b


def test_an_honest_page_verifies_with_its_display_bound(tmp_path):
    viewer, b = page(tmp_path)
    assert bundle.verify(b) == (True, [])
    assert bundle.verify_display(b, viewer) == []
    r = js_verify_page(viewer, b, tmp_path)
    assert r["ok"] is True, r["problems"]


@pytest.mark.parametrize("edit", [
    lambda v: v["counts"].__setitem__("sightings_organic", 4127),
    lambda v: v["sightings"][0].__setitem__("origin", "organic"),
    lambda v: v.__setitem__("claim", "requested 4m 35s later by a different operator"),
    lambda v: v["sightings"][0]["requested"].__setitem__("ua", "SomeoneElse/9.9"),
    lambda v: v["sightings"][0]["requested"].__setitem__(
        "raw", v["sightings"][0]["requested"]["raw"].replace("192.0.2", "203.0.113")),
    lambda v: v.__setitem__("scope_line", "A sighting proves two operators colluded."),
])
def test_editing_what_the_page_displays_is_caught(tmp_path, edit):
    """THE finding: the page displayed CANARY_DATA and verified CANARY_BUNDLE, and
    nothing compared the two. Changing the organic counter to 4127 and the label
    from 'seeded' to 'organic' in the half of data.js the reader actually sees
    still printed 'Verified' - the verification theatre of F-0003, one level up."""
    viewer, b = page(tmp_path)
    edit(viewer)
    assert bundle.verify_display(b, viewer), "Python must refuse the edited display"
    r = js_verify_page(viewer, b, tmp_path)
    assert r["ok"] is False
    assert any("display" in p for p in r["problems"]), r["problems"]


def test_a_displayed_record_must_be_one_of_the_hashed_rows(tmp_path):
    """Even with a digest that matches, what is on screen has to BE the rows under
    the root: a payload built from a different snapshot than its bundle would
    otherwise verify while showing records the root never covered."""
    viewer, b = page(tmp_path)
    viewer["sightings"][0]["requested"]["raw"] = "192.0.2.0/24 - - [x] \"GET /other\" 200 1"
    b["viewer"] = bundle.payload_digest(viewer)                 # the operator re-commits
    b["leaves"][0] = bundle.header_leaf(b["format"], b["note"], b["counts"], b["viewer"])
    b["root"] = bundle.merkle_root(b["leaves"])
    assert bundle.verify(b) == (True, [])                       # internally consistent...
    assert any("record" in p for p in bundle.verify_display(b, viewer))   # ...and still refused
    r = js_verify_page(viewer, b, tmp_path)
    assert r["ok"] is False and any("record" in p for p in r["problems"]), r["problems"]


# --- the shipped file itself, as a reader would attack it ---------------------

FILE_HARNESS = r"""
const fs = require('fs');
globalThis.window = globalThis;
(0, eval)(fs.readFileSync(process.argv[2], 'utf8'));      // verify.js
(0, eval)(fs.readFileSync(process.argv[3], 'utf8'));      // data.js, exactly as shipped
const edit = process.argv[4] || '';
if (edit) (0, eval)(edit);
window.CanaryVerify.verifyBundle(window.CANARY_BUNDLE, window.CANARY_DATA).then(
  r => { console.log(JSON.stringify(r)); },
  e => { console.log(JSON.stringify({ok: false, problems: ['threw: ' + e]})); });
"""


def shipped(tmp_path: Path, *, sight: bool = True, mint: bool = True) -> Path:
    """Run the real export script against a temp ledger; return its data.js."""
    import sys
    db = tmp_path / "s.sqlite3"
    led = Ledger(str(db))
    if mint:
        r1 = led.record_request(method="GET", path="/m/x", status=200, ip="198.51.100.7",
                                ua="GPTBot/1.2", ctx_id="ctx-a", origin="seeded",
                                ts="2026-10-03T10:00:00Z")
        led.record_mint(secret="a" * 16, ctx_id="ctx-a", path="/m/x", salt_epoch="e",
                        request_id=r1, ts="2026-10-03T10:00:00Z")
        if sight:
            r2 = led.record_request(method="GET", path="/c/" + "a" * 16 + "/x", status=200,
                                    ip="192.0.2.9", ua="undefined Chrome/124", ctx_id="ctx-b",
                                    origin="seeded", ts="2026-10-03T10:04:35Z")
            led.record_sighting(secret="a" * 16, mint_ctx_id="ctx-a", seen_ctx_id="ctx-b",
                                mint_request_id=r1, seen_request_id=r2, delta_s=275.0,
                                origin="seeded", ts="2026-10-03T10:04:35Z")
    led.close()
    out = tmp_path / "out"
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "export_all.py"),
                        "--db", str(db), "--out", str(out),
                        "--bundle", str(out / "bundle.json")],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr + r.stdout
    return out / "data.js"


def run_file(data_js: Path, tmp_path: Path, edit: str = "") -> dict:
    (tmp_path / "h3.js").write_text(FILE_HARNESS, encoding="utf-8")
    out = subprocess.run([NODE, str(tmp_path / "h3.js"), str(VERIFY_JS), str(data_js), edit],
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


@pytest.mark.parametrize("state,kw", [("sighting", {}), ("awaiting", {"sight": False}),
                                      ("empty", {"mint": False})])
def test_the_shipped_page_verifies_in_every_state(tmp_path, state, kw):
    data_js = shipped(tmp_path, **kw)
    assert f'"state": "{state}"' in data_js.read_text(encoding="utf-8")
    r = run_file(data_js, tmp_path)
    assert r["ok"] is True, r["problems"]


@pytest.mark.parametrize("edit", [
    "window.CANARY_DATA.counts.sightings_organic = 4127",
    "window.CANARY_DATA.sightings[0].origin = 'organic'",
    "window.CANARY_DATA.claim = 'requested 4m 35s later'",
    "window.CANARY_DATA.sightings[0].requested.ua = 'SomeoneElse/9.9'",
])
def test_editing_the_display_half_of_the_shipped_file_is_refused(tmp_path, edit):
    """The reviewer's exact attack, on the exact file: change what the reader sees,
    leave the bundle alone, press the button."""
    r = run_file(shipped(tmp_path), tmp_path, edit)
    assert r["ok"] is False and r["problems"], r


def test_editing_the_bundle_half_is_still_caught_and_named(tmp_path):
    r = run_file(shipped(tmp_path), tmp_path,
                 "window.CANARY_BUNDLE.rows.request[1].ua = 'SomeoneElse/9.9'")
    assert r["ok"] is False
    assert any("request id=2" in p for p in r["problems"]), r["problems"]
