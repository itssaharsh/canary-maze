#!/usr/bin/env python3
"""How many addresses does one named label write from, in the collusion.wiki dump?

Why this exists
---------------
Canary Maze reports that a secret moved between two request CONTEXTS and refuses
to say two contexts are two actors. A context includes the client's network. So
the restraint is only worth stating if one actor really does appear from many
networks - and that is a measurable thing.

The organizers' collusion.wiki dump is public and ungated, and its labels table
gives, per label, the number of stored revisions and the number of distinct
addresses and distinct /16 networks they were written from. This script reads
that table and reports it. Anyone can run it; it needs no credentials.

A correction this script exists to make permanent
-------------------------------------------------
An earlier version of this project said, on the viewer's own face and in every
document, that "one actor label carries 899 revisions across 741 addresses". That
row is real, and its label is the EMPTY STRING: it is the pool of every edit that
carried no label at all, across 568 pages. It is not one actor, and it was never
the right number. An independent review opened the file and found it. The figure
came from the research notes this project started from and was repeated without
anyone opening the row.

What is reported instead is only what the table supports:
  - the blank row is reported AS the blank row;
  - the statistic is taken over named agent labels;
  - a label is a self-chosen name, not an identity: several agents can share one
    and one agent can use several. "One named label" is exactly what is claimed.

Two addresses in different /16 networks are necessarily in different /24 networks,
and this tool's context includes the /24. So "wrote from N distinct /16s" is a
LOWER BOUND on how many contexts this tool would have derived for that label.

No label flagged `is_human_handle` is ever printed or written.

Usage
-----
    python3 scripts/label_spread.py                 # download, verify, report
    python3 scripts/label_spread.py --file labels.jsonl.gz
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import statistics
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://collusion.wiki/explorer/download/labels.jsonl.gz"
#: SHA-256 of the EXPANDED file as downloaded 2026-10-03. The dump may be
#: republished; a different hash is reported, not hidden, and the numbers printed
#: are then the numbers of the file actually read.
PINNED_SHA256 = "d94aecd84baecda46344f5b8726a95a9c81e7e41a1c0969fc89a90c8906f0388"
OUT = ROOT / "docs" / "label_spread.json"
CACHE = Path.home() / ".cache" / "canary-maze" / "labels.jsonl.gz"


def fetch() -> Path:
    if CACHE.exists():
        return CACHE
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(SOURCE, headers={"User-Agent": "canary-maze-label-spread/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        CACHE.write_bytes(r.read())
    return CACHE


def measure(path: Path) -> dict:
    raw = gzip.open(path, "rb").read()
    rows = [json.loads(l) for l in raw.decode("utf-8").splitlines() if l.strip()]
    n = lambda r, k: int(r.get(k) or 0)

    blank = [r for r in rows if not (r.get("label") or "").strip()]
    agent = [r for r in rows if (r.get("label") or "").strip() and not r.get("is_human_handle")]
    repeat = [r for r in agent if n(r, "stored_revisions") >= 2]
    top = max(agent, key=lambda r: n(r, "stored_revision_ips"))

    return {
        "source": SOURCE,
        "sha256_expanded": hashlib.sha256(raw).hexdigest(),
        "matches_pinned_file": hashlib.sha256(raw).hexdigest() == PINNED_SHA256,
        "label_rows": len(rows),
        "human_handle_rows_excluded": sum(1 for r in rows if r.get("is_human_handle")),
        "blank_label": {
            "what_it_is": "the pool of every stored revision that carried no label; not an actor",
            "rows": len(blank),
            "revisions": sum(n(r, "stored_revisions") for r in blank),
            "addresses": sum(n(r, "stored_revision_ips") for r in blank),
        },
        "named_agent_labels": len(agent),
        "with_two_or_more_revisions": len(repeat),
        "of_those_from_more_than_one_address": sum(1 for r in repeat if n(r, "stored_revision_ips") > 1),
        "of_those_from_more_than_one_slash16": sum(1 for r in repeat if n(r, "stored_revision_ip16") > 1),
        "median_addresses": statistics.median(n(r, "stored_revision_ips") for r in repeat),
        "median_slash16s": statistics.median(n(r, "stored_revision_ip16") for r in repeat),
        "busiest_named_agent_label": {
            "label": top["label"],
            "revisions": n(top, "stored_revisions"),
            "addresses": n(top, "stored_revision_ips"),
            "slash16s": n(top, "stored_revision_ip16"),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=None, help="a local labels.jsonl.gz instead of downloading")
    ap.add_argument("--json", default=str(OUT))
    args = ap.parse_args()

    m = measure(Path(args.file) if args.file else fetch())
    b, t = m["blank_label"], m["busiest_named_agent_label"]
    r2 = m["with_two_or_more_revisions"]
    print(f"source: {m['source']}")
    print(f"file  : sha256 {m['sha256_expanded'][:16]}…  "
          f"{'matches the pinned file' if m['matches_pinned_file'] else 'DIFFERS from the pinned file - the dump was republished'}")
    print()
    print(f"blank label        {b['revisions']} revisions, {b['addresses']} addresses "
          f"- the pool of unlabelled edits, NOT one actor")
    print(f"named agent labels {m['named_agent_labels']}  "
          f"({m['human_handle_rows_excluded']} human handles excluded and never printed)")
    print(f"  with >= 2 revisions            {r2}")
    print(f"  of those, > 1 address          {m['of_those_from_more_than_one_address']}  "
          f"({100 * m['of_those_from_more_than_one_address'] / r2:.1f}%)")
    print(f"  of those, > 1 /16 network      {m['of_those_from_more_than_one_slash16']}  "
          f"({100 * m['of_those_from_more_than_one_slash16'] / r2:.1f}%)  "
          f"<- each would be > 1 context here")
    print(f"  median                         {m['median_addresses']:g} addresses, "
          f"{m['median_slash16s']:g} /16 networks")
    print(f"busiest named agent label        {t['revisions']} revisions from {t['addresses']} "
          f"addresses in {t['slash16s']} /16 networks")
    Path(args.json).write_text(json.dumps(m, indent=1), encoding="utf-8")
    print(f"\nwritten: {Path(args.json).name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
