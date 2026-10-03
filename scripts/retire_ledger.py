#!/usr/bin/env python3
"""Copy a retired ledger into ledgers/archive/ - completely - and prove it.

A ledger that turns out to be unpublishable is retired, never edited. Retiring it
means keeping it, and the first three were "kept" with `cp`. These are WAL-mode
databases: most of their rows live in the `-wal` file until a checkpoint, and `cp`
of the main file alone copies whatever happened to have been checkpointed. One
archive came out with 1 of its 7 requests, one was a 4096-byte file with no tables
at all, and one was missing the very sighting it had been retired for. A review
opened them and found it; nobody had opened them since they were written.

So this uses SQLite's backup API, which reads through the WAL, and then counts the
rows on both sides and refuses to report success unless they match.

Usage
-----
    python3 scripts/retire_ledger.py <source.sqlite3> <label>
    python3 scripts/retire_ledger.py --verify        # recount every archive
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "ledgers" / "archive"
TABLES = ("request", "mint", "sighting", "published", "gate_rejection")


def counts(path: Path) -> dict[str, int]:
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        have = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        out = {}
        for t in TABLES:
            if t not in have:
                continue
            if t == "gate_rejection":
                out[t] = int(con.execute("SELECT COALESCE(MAX(n), 0) FROM gate_rejection").fetchone()[0])
            else:
                out[t] = int(con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
        return out
    finally:
        con.close()


def retire(source: Path, label: str, dest: Path | None = None) -> Path:
    if not source.exists():
        raise SystemExit(f"no such ledger: {source}")
    want = counts(source)
    if dest is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        dest = ARCHIVE / f"{source.stem}-{stamp}-{label}.sqlite3"
    dest.parent.mkdir(parents=True, exist_ok=True)
    src = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
    dst = sqlite3.connect(dest)
    try:
        src.backup(dst)            # reads through the WAL; a consistent, complete copy
        dst.execute("PRAGMA journal_mode=DELETE")   # one self-contained file, no sidecars
        dst.commit()
    finally:
        dst.close()
        src.close()
    got = counts(dest)
    if got != want:
        raise SystemExit(f"archive does NOT match its source:\n  source  {want}\n  archive {got}")
    shown = dest.resolve()
    shown = shown.relative_to(ROOT) if shown.is_relative_to(ROOT) else shown
    print(f"{shown}\n  {got}  (matches the source)")
    return dest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", nargs="?")
    ap.add_argument("label", nargs="?", default="retired")
    ap.add_argument("--dest", default=None, help="write to this exact archive file")
    ap.add_argument("--verify", action="store_true", help="recount every archive and print it")
    args = ap.parse_args()
    if args.verify:
        for p in sorted(ARCHIVE.glob("*.sqlite3")):
            print(f"{p.name}\n  {counts(p)}")
        return 0
    if not args.source:
        ap.error("give the ledger to retire, or --verify")
    retire(Path(args.source), args.label, Path(args.dest) if args.dest else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
