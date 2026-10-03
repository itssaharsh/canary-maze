"""The drift gate must catch a stale number without failing a fresh clone.

`make verify` is the first command a judge runs. An earlier version of this check
compared the committed table against ledgers that a clone does not have, so the
repo failed its own headline command on arrival - a worse outcome than a stale
number, and exactly the kind of thing nobody notices because the author always
has the ledgers.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_results.py"


def run(*args, cwd=None):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, cwd=cwd or ROOT)


def test_absent_ledgers_do_not_count_as_drift(tmp_path):
    """The fresh-clone case: neither ledger exists, so nothing can disagree."""
    r = run("--check", "--live", "nope-live.sqlite3", "--demo", "nope-demo.sqlite3")
    assert r.returncode == 0, r.stderr


def test_a_present_ledger_that_disagrees_is_still_caught(tmp_path, monkeypatch):
    """The gate must not have been defanged: a real ledger with different
    numbers still fails, which is the whole reason it exists."""
    import sqlite3
    sys.path.insert(0, str(ROOT))
    from canarymaze.ledger import Ledger

    db = tmp_path / "other.sqlite3"
    led = Ledger(str(db))
    rid = led.record_request(method="GET", path="/m/x", status=200,
                             ip="198.51.100.9", ua="GPTBot/1.1", ctx_id="ctx0001")
    led.record_mint(secret="f" * 16, ctx_id="ctx0001", path="/m/x",
                    salt_epoch="e", request_id=rid)
    led.close()

    r = run("--check", "--demo", str(db))
    assert r.returncode == 1, "a present ledger with different counts must fail the gate"
    assert "out of date" in (r.stderr + r.stdout)


def test_regenerating_then_checking_is_consistent(tmp_path):
    """Generate, then check: the two must agree, or the gate is meaningless.

    Against a COPY. This used to regenerate the tracked docs/RESULTS.md, so running
    the test suite edited a judge-facing document - and on the operator's machine
    rewrote the live column on every run."""
    copy = tmp_path / "RESULTS.md"
    copy.write_text((ROOT / "docs" / "RESULTS.md").read_text(encoding="utf-8"),
                    encoding="utf-8")
    assert run("--results", str(copy)).returncode == 0
    assert run("--check", "--results", str(copy)).returncode == 0


def test_a_clone_that_has_run_make_demo_still_passes(tmp_path):
    """Demo ledger present, live ledger absent: the state of any clone after
    `make demo`, which is the README's own quickstart order. The live column and
    the sentence that restates it are kept, so the committed file must still pass."""
    db = tmp_path / "demo.sqlite3"
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "seed_replay.py"),
                        "--db", str(db)], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr
    committed = tmp_path / "RESULTS.md"
    committed.write_text((ROOT / "docs" / "RESULTS.md").read_text(encoding="utf-8"),
                         encoding="utf-8")
    before = committed.read_text(encoding="utf-8")
    absent = str(tmp_path / "absent.sqlite3")
    r = run("--check", "--live", absent, "--demo", str(db), "--results", str(committed))
    assert r.returncode == 0, r.stderr + r.stdout
    # and regenerating in that state must not rewrite the live column either
    assert run("--live", absent, "--demo", str(db), "--results", str(committed)).returncode == 0
    assert committed.read_text(encoding="utf-8") == before


def test_the_suite_never_writes_the_tracked_results_file():
    """Every invocation in this file that can write must name a --results copy."""
    src = Path(__file__).read_text(encoding="utf-8")
    writers = [l for l in src.splitlines()
               if l.strip().startswith(("assert run(", "r = run(")) and "--check" not in l]
    assert all("--results" in l or '"--live", "canary.sqlite3"' in l for l in writers), writers


def test_the_generator_refuses_a_retired_ledger():
    """It hardcoded the retired path once and published four 'organic' sightings
    out of a quarantined ledger. A guard only guards the callers that consult it,
    so this asserts that this caller does."""
    r = run("--live", "canary.sqlite3")
    assert r.returncode != 0
    assert "retired" in (r.stderr + r.stdout).lower()


def test_the_generator_defaults_to_the_live_ledger():
    from canarymaze.paths import DEFAULT_LEDGER
    src = SCRIPT.read_text(encoding="utf-8")
    assert 'default="ledgers/canary-public.sqlite3"' not in src, \
        "a hardcoded ledger path here bypasses the retirement registry"
    assert "ledger_path(" in src, "the path must be resolved through the guard"
    assert DEFAULT_LEDGER
