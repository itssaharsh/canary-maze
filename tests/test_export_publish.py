"""Publishing a bundle publishes its secrets, so the ledger has to know.

A bundle carries every mint row in full. export.py takes care to keep the secret
out of the public payload - and export_all.py then wrote the same secret, in full,
into the same data.js as part of the bundle. Anyone reading the page could fetch
that canary URL from another address and be counted as an organic sighting.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from canarymaze.ledger import Ledger

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_all.py"


def live_ledger(tmp_path: Path, origin: str = "organic") -> Path:
    db = tmp_path / "live.sqlite3"
    led = Ledger(str(db))
    rid = led.record_request(method="GET", path="/m/x", status=200, ip="198.51.100.7",
                             ua="GPTBot/1.2", ctx_id="ctx-a", origin=origin,
                             ts="2026-10-03T10:00:00Z")
    led.record_mint(secret="c" * 16, ctx_id="ctx-a", path="/m/x", salt_epoch="e",
                    request_id=rid, ts="2026-10-03T10:00:00Z")
    led.close()
    return db


def export(db: Path, out: Path, *flags: str):
    return subprocess.run([sys.executable, str(SCRIPT), "--db", str(db), "--out", str(out),
                           "--bundle", str(out / "bundle.json"), *flags],
                          capture_output=True, text=True, cwd=ROOT)


def test_a_live_ledger_cannot_be_exported_without_disclosing_its_secrets(tmp_path):
    db, out = live_ledger(tmp_path), tmp_path / "out"
    r = export(db, out)
    assert r.returncode == 2
    assert "--publish" in r.stderr
    assert not (out / "data.js").exists(), "nothing may be written before the disclosure"


def test_publishing_records_the_disclosure_and_later_fetches_are_not_organic(tmp_path):
    db, out = live_ledger(tmp_path), tmp_path / "out"
    r = export(db, out, "--publish")
    assert r.returncode == 0, r.stderr + r.stdout

    shipped = json.loads((out / "data.json").read_text(encoding="utf-8"))
    assert shipped["bundle"]["rows"]["published"][0]["secret"] == "c" * 16, \
        "the bundle that carries the secret must carry the disclosure with it"

    # a reader copies the secret out of the published file and fetches it
    led = Ledger(str(db))
    rid = led.record_request(method="GET", path="/c/" + "c" * 16 + "/x", status=200,
                             ip="203.0.113.5", ua="curl/8.5.0", ctx_id="ctx-reader")
    led.record_sighting(secret="c" * 16, mint_ctx_id="ctx-a", seen_ctx_id="ctx-reader",
                        mint_request_id=1, seen_request_id=rid, delta_s=60.0, origin="organic")
    c = led.counts()
    led.close()
    assert c["sightings_organic"] == 0, "a published secret must never yield organic evidence"
    assert c["sightings_paste"] == 1


def test_the_seeded_replay_needs_no_disclosure(tmp_path):
    """Its secrets were issued to nobody: the demo must keep working in one command."""
    db, out = live_ledger(tmp_path, origin="seeded"), tmp_path / "out"
    r = export(db, out)
    assert r.returncode == 0, r.stderr + r.stdout
    assert (out / "data.js").exists()


def test_exporting_twice_does_not_disclose_twice(tmp_path):
    db, out = live_ledger(tmp_path), tmp_path / "out"
    assert export(db, out, "--publish").returncode == 0
    assert export(db, out, "--publish").returncode == 0
    led = Ledger(str(db))
    n = len(led.rows("published"))
    led.close()
    assert n == 1
