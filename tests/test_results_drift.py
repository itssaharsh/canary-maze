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


def test_the_documented_test_count_is_the_real_one():
    """Four judge-facing documents once gave four different test counts (117, 143,
    145, 176) while the suite had 224, and syncing them by hand lasted exactly one
    commit. The suite now refuses to be wrong about itself."""
    import re
    import subprocess
    import sys
    n = len(re.findall(r"^\S+::", subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--co", "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=ROOT).stdout, re.M))
    assert n > 100, "could not collect the suite"
    wrong = []
    for name in ("README.md", "SUBMISSION.md", "SUBMIT.md",
                 "site/index.html", "docs/RESULTS.md", "docs/FORM-ANSWERS.md"):
        f = ROOT / name
        if not f.exists():
            continue
        for m in re.finditer(r"(\d{2,4})\s+tests\b|expect:\s*(\d{2,4})\s+passed", f.read_text(encoding="utf-8")):
            said = int(m.group(1) or m.group(2))
            if said != n:
                wrong.append(f"{name}: says {said}, suite has {n}")
    assert not wrong, "run python3 scripts/sync_counts.py\n  " + "\n  ".join(wrong)


def test_the_documented_review_count_does_not_disagree_with_itself():
    """The same drift, in the one number this project cannot regenerate. Four
    judge-facing documents claimed how many review findings were confirmed, and
    three still said "Twenty-five" after a later round took it to 31 - so a judge
    reading two of them saw two different answers about the review this entry
    leans on. Unlike the test count there is no command to recompute it from, so
    the only available guarantee is that the documents agree with each other."""
    import re
    WORDS = {"twenty-five": 25, "twenty five": 25, "thirty-one": 31, "thirty one": 31}
    said = {}
    for name in ("AGENTS.md", "SUBMIT.md", "SUBMISSION.md", "README.md",
                 "ARCHITECTURE.md", "docs/FORM-ANSWERS.md"):
        f = ROOT / name
        if not f.exists():
            continue
        flat = " ".join(f.read_text(encoding="utf-8").split())
        for m in re.finditer(r"([\w-]+)\s+(?:findings\s+)?(?:were\s+)?confirmed", flat, re.I):
            tok = m.group(1).lower()
            n = WORDS.get(tok, int(tok) if tok.isdigit() else None)
            if n is not None:
                said.setdefault(n, []).append(name)
    assert said, "no document states how many review findings were confirmed"
    assert len(said) == 1, "documents disagree on the review-finding count: " + "; ".join(
        f"{n} in {sorted(set(v))}" for n, v in sorted(said.items()))


def test_a_reader_told_to_run_the_suite_is_told_how_to_install_it():
    """SUBMIT.md's pre-flight said `pip install -r requirements.txt` and then
    `python3 -m pytest -q`, and claimed all of it had been run in a fresh clone.
    It cannot have been: pytest lives in requirements-dev.txt, so on a real cold
    clone the last line fails with "No module named pytest". The product's one
    dependency is the honest claim and worth keeping, which is exactly why the
    install line has to name the dev file or `make install`."""
    import re
    assert "pytest" not in (ROOT / "requirements.txt").read_text(encoding="utf-8"), \
        "requirements.txt now ships pytest; the 'one dependency' claim needs rewording"
    assert "pytest" in (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")
    bad = []
    INSTALL = r"make install|pip install|requirements-dev"
    for name in ("README.md", "SUBMIT.md", "SUBMISSION.md", "docs/FORM-ANSWERS.md"):
        f = ROOT / name
        if not f.exists():
            continue
        for block in re.findall(r"```.*?```", f.read_text(encoding="utf-8"), re.S):
            if re.search(INSTALL, block):
                continue
            # A block a judge copies whole must not die on a missing dependency.
            # README's headline "three commands" did exactly that: `make verify`
            # with no install printed FAIL on a clean machine, which was the first
            # output the project's own front page produced.
            if "pytest" in block:
                bad.append(f"{name}: a block runs pytest without installing it")
            elif re.search(r"make (verify|demo|test)\b", block):
                bad.append(f"{name}: a block runs make verify/demo without installing Flask")
    assert not bad, "\n  ".join(bad)


def test_the_corpus_tables_are_the_numbers_the_scripts_measured():
    """README.md and AGENTS.md both promise that `make verify` fails if a document
    has drifted from the generated data. Until this test existed that was only true
    of the `counts:` block: the corpus tables in docs/RESULTS.md are hand-typed, and
    nothing compared them to label_spread.json or village_reuse.json - which is
    exactly how the withdrawn 741 figure reached the product's own face. The numbers
    happened to be right; the guarantee was not."""
    import json
    results = (ROOT / "docs" / "RESULTS.md").read_text(encoding="utf-8")
    spread = json.loads((ROOT / "docs" / "label_spread.json").read_text(encoding="utf-8"))
    reuse = json.loads((ROOT / "docs" / "village_reuse.json").read_text(encoding="utf-8"))

    def pct(x):
        return f"{round(x * 100)}%"

    want = {
        "labels with 2+ revisions": f"{spread['with_two_or_more_revisions']:,}",
        "from >1 address": f"{spread['of_those_from_more_than_one_address']:,}",
        "from >1 /16": f"{spread['of_those_from_more_than_one_slash16']:,}",
        "busiest: revisions": str(spread["busiest_named_agent_label"]["revisions"]),
        "busiest: addresses": str(spread["busiest_named_agent_label"]["addresses"]),
        "busiest: /16s": str(spread["busiest_named_agent_label"]["slash16s"]),
        "turn rows parsed": f"{reuse['turn_rows_parsed']:,}",
        "unguessable urls": f"{reuse['unguessable_urls']['urls']:,}",
        "first uses by another agent": str(reuse["unguessable_urls"]["first_uses_by_another_agent"]),
    }
    for row in reuse["two_contexts_one_agent"]["by_definition"]:
        tag = "session" if row["context"] == "a session" else "client program"
        want[f"{tag}: re-uses"] = f"{row['re_uses']:,}"
        want[f"{tag}: same-agent share"] = pct(row["all"]["same_agent_share"])
        if tag == "session":
            want["session: before"] = pct(row["before"]["same_agent_share"])
            want["session: after"] = pct(row["after"]["same_agent_share"])

    missing = [f"{k} = {v!r}" for k, v in want.items() if v not in results]
    assert not missing, (
        "docs/RESULTS.md no longer shows what the scripts measured; regenerate it "
        "or re-run the script:\n  " + "\n  ".join(missing))
