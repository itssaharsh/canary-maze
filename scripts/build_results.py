#!/usr/bin/env python3
"""Regenerate the counts in docs/RESULTS.md from the ledgers themselves.

RESULTS.md has always said "nothing here is hand-typed". Until this script
existed that sentence was false: the numbers were typed by hand from a terminal,
and they had already drifted once - build_site.py's docstring records a version
that said 2 while the ledger held 3. A file whose whole claim is that it reports
numbers exactly as they stand cannot be maintained by retyping them.

The counts come from two ledgers and are reported separately, because they
answer different questions:

  the live public ledger   what third-party traffic has actually been observed
  the seeded demo ledger   that the mechanism works end to end

Merging them would produce a single impressive number that means nothing.
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "docs" / "RESULTS.md"

START = "<!-- counts:start -->"
END = "<!-- counts:end -->"


def counts(db: Path) -> dict[str, int] | None:
    """Read the honesty counters straight from a ledger, or None if absent."""
    if not db.exists():
        return None
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        one = lambda q: int(con.execute(q).fetchone()[0])
        return {
            "mints": one("SELECT COUNT(*) FROM mint"),
            "requests": one("SELECT COUNT(*) FROM request"),
            "organic": one("SELECT COUNT(*) FROM sighting WHERE origin='organic'"),
            "seeded": one("SELECT COUNT(*) FROM sighting WHERE origin='seeded'"),
            "paste": one("SELECT COUNT(*) FROM sighting WHERE origin='paste'"),
            "selftest": one("SELECT COUNT(*) FROM sighting WHERE origin='selftest'"),
            "humans_turned_away": one("SELECT COALESCE(MAX(n),0) FROM gate_rejection"),
            "human_requests": one("SELECT COUNT(*) FROM request WHERE is_automated=0"),
        }
    except sqlite3.Error:
        return None
    finally:
        con.close()


def table(live: dict[str, int] | None, demo: dict[str, int] | None) -> str:
    g = lambda d, k: "-" if d is None else str(d[k])
    rows = [
        ("Secrets minted", "mints"),
        ("**Organic sightings**", "organic"),
        ("Paste-triggered sightings", "paste"),
        ("Seeded sightings", "seeded"),
        ("Operator self-test sightings", "selftest"),
        ("Humans turned away by the gate", "humans_turned_away"),
        ("Human requests in the ledger", "human_requests"),
        ("Requests recorded", "requests"),
    ]
    out = [
        "| Category | Live public surface | Seeded replay |",
        "|---|---|---|",
    ]
    for label, key in rows:
        out.append(f"| {label} | {g(live, key)} | {g(demo, key)} |")
    out.append("")
    out.append("The two columns are never added together. The left one answers "
               "\"what has been observed in the wild\"; the right one answers "
               "\"does the mechanism work\". Only the left column is evidence "
               "about anyone else's behaviour.")
    if live is not None and live["organic"] == 0:
        out.append("")
        out.append("**Organic sightings stand at 0.** That is reported as-is. "
                   "The operator's own probes are recorded separately as "
                   "self-tests (see F-0004) precisely so this number cannot be "
                   "quietly inflated by our own traffic.")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", default="ledgers/canary-public.sqlite3")
    ap.add_argument("--demo", default="demo.sqlite3")
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if RESULTS.md is out of date, writing nothing")
    args = ap.parse_args()

    live, demo = counts(ROOT / args.live), counts(ROOT / args.demo)
    if live is None and demo is None:
        print("no ledger found; run make demo or start the surface first", file=sys.stderr)
        return 1

    text = RESULTS.read_text(encoding="utf-8")
    block = f"{START}\n{table(live, demo)}\n{END}"
    if START in text and END in text:
        new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block,
                     text, flags=re.S)
    else:
        print(f"{RESULTS} has no {START} / {END} markers", file=sys.stderr)
        return 1

    if args.check:
        if new != text:
            print("docs/RESULTS.md is out of date; run: python3 scripts/build_results.py",
                  file=sys.stderr)
            return 1
        print("docs/RESULTS.md matches the ledgers")
        return 0

    RESULTS.write_text(new, encoding="utf-8")
    print(f"docs/RESULTS.md counts regenerated "
          f"(live organic {('-' if live is None else live['organic'])}, "
          f"seeded {('-' if demo is None else demo['seeded'])})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
