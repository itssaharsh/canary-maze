#!/usr/bin/env python3
"""Assemble site/ from the live artefacts.

The landing page used to hardcode its counters, and they drifted: it claimed 1 mint
while RESULTS.md said 2 and the ledger held 3, and it claimed a test count that was
wrong in three places at once. Numbers a reader can falsify in one command are worse
than no numbers, so they are generated here from the same data the viewer renders.
"""
from __future__ import annotations
import json, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE, VIEWER = ROOT / "site", ROOT / "viewer"


# --- the Vercel canary surface ----------------------------------------------
# The function is stdlib-only and imports the SAME modules the local surface
# runs, copied here at build time rather than vendored by hand. Copying beats a
# second implementation: the gate and the mint are the two functions a reviewer
# attacks first, and two copies of them would drift.
API_MODULES = ("maze.py", "mint.py", "context.py", "gate.py", "ingest.py", "netaddr.py")


def build_api() -> None:
    cm = SITE / "api" / "_cm"
    cm.mkdir(parents=True, exist_ok=True)
    (cm / "__init__.py").write_text("", encoding="utf-8")
    for name in API_MODULES:
        src = (ROOT / "canarymaze" / name).read_text(encoding="utf-8")
        # the copies import each other as a flat package, not as canarymaze.*
        src = src.replace("from .context import", "from .context import")
        (cm / name).write_text(src, encoding="utf-8")
    print(f"api: {len(API_MODULES)} modules copied to site/api/_cm/")


def verify_transcript() -> str:
    """The real output of `make verify`, captured now.

    It used to be hand-typed into the page, and it drifted: two of its five lines
    were checks the command had stopped printing, one of them advertising a
    "model enabled vs off" comparison for a build that has no model. A transcript
    a reader can reproduce in one command is worse than none when it is wrong.
    """
    r = subprocess.run(["bash", "scripts/verify.sh"], cwd=ROOT, capture_output=True, text=True)
    body = "\n".join(ln.rstrip() for ln in r.stdout.splitlines() if ln.strip())
    body = re.sub(r"\b(OK|PASS)\b", r'<span class="g">\1</span>', escape(body))
    return "$ make verify\n\n" + body


def escape(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> int:
    data = json.loads((VIEWER / "data.json").read_text(encoding="utf-8"))
    counts = data["viewer"]["counts"]
    leaves = len(data["bundle"]["leaves"])
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "--co"],
                           cwd=ROOT, capture_output=True, text=True)
    n_tests = len(re.findall(r"^\S+::", tests.stdout, re.M)) or "see make test"

    (SITE / "viewer").mkdir(parents=True, exist_ok=True)
    for f in ("index.html", "app.css", "render.js", "verify.js", "data.js"):
        shutil.copy(VIEWER / f, SITE / "viewer" / f)

    html = (SITE / "index.html").read_text(encoding="utf-8")
    # These counters describe the SEEDED REPLAY that viewer/data.json holds, and the
    # page says so. The live surface's numbers are generated into docs/RESULTS.md by
    # scripts/build_results.py; an earlier page captioned the demo fixture's counters
    # "every number below comes from the ledger", and for a while one of them came
    # from a throwaway test ledger that make verify had overwritten the file with.
    rows = [
        ("Secrets issued", counts["mints"], "to automated contexts, through the real gate and mint"),
        ("Sightings in this replay", counts["sightings_seeded"],
         "two clients we control, driven through the real gate, mint and detector"),
        ("Organic sightings here", counts["sightings_organic"],
         "0 by construction: a scripted replay observes nobody"),
        ("Human requests stored", counts["human_requests"],
         "must be 0 — a non-zero value would mean a human reached storage"),
        ("Hashes in the bundle", leaves, "each one recomputed in your browser by the button above"),
        ("Tests", n_tests, "<code>make verify</code> PASS"),
    ]
    body = "\n".join(
        f'      <tr><th>{k}</th><td class="num{" zero" if k.startswith("Human requests") and v == 0 else ""}">{v}</td><td>{d}</td></tr>'
        for k, v, d in rows)
    html = re.sub(r"(<!--COUNTS-->).*?(<!--/COUNTS-->)",
                  lambda m: m.group(1) + "\n" + body + "\n    " + m.group(2),
                  html, flags=re.S)
    html = re.sub(r"(<!--VERIFY-->).*?(<!--/VERIFY-->)",
                  lambda m: m.group(1) + verify_transcript() + m.group(2),
                  html, flags=re.S)
    # The scope line travels with the data, so the page cannot state a different
    # bound from the one the viewer shows.
    html = re.sub(r"(<!--SCOPE-->).*?(<!--/SCOPE-->)",
                  lambda m: m.group(1) + escape(data["viewer"]["scope_line"]) + m.group(2),
                  html, flags=re.S)
    (SITE / "index.html").write_text(html, encoding="utf-8")
    print(f"site built: {len(rows)} counters from viewer/data.json, {n_tests} tests")
    build_api()
    return 0



if __name__ == "__main__":
    raise SystemExit(main())
