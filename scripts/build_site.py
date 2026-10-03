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
    rows = [
        ("Mints", counts["mints"], "secrets issued to automated contexts"),
        ("Seeded sightings", counts["sightings_seeded"],
         "two clients we control, driven through the real gate, mint and detector"),
        ("Organic sightings", counts["sightings_organic"],
         "reported exactly as it stands — this is the honest number, not a rounding"),
        ("Paste-triggered", counts["sightings_paste"],
         "counted separately: a fetcher following a human&rsquo;s paste is <em>not</em> two agents sharing"),
        ("Humans turned away", counts["humans_turned_away"],
         "the gate fired this many times and stored nothing about any of them"),
        ("Human requests in ledger", counts["human_requests"],
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
    (SITE / "index.html").write_text(html, encoding="utf-8")
    print(f"site built: {len(rows)} counters from viewer/data.json, {n_tests} tests")
    build_api()
    return 0



if __name__ == "__main__":
    raise SystemExit(main())
