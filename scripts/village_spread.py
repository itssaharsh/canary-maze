#!/usr/bin/env python3
"""Measure context spread per agent in the AI Village corpus.

Why this exists
---------------
Canary Maze's central honest claim is "a sighting shows a secret moved between two
request CONTEXTS, not that there are two operators". That claim currently rests on
one measurement, from the collusion.wiki dump: a single actor label carrying 899
revisions across 741 distinct addresses.

This script looks for the same shape in a SECOND, independent corpus. If agents in
the AI Village also present as many contexts, the claim is supported twice, from two
unrelated datasets, and that goes in docs/RESULTS.md.

The build does not depend on this. It is evidence for the write-up.

Usage
-----
    export HF_TOKEN=...            # from huggingface.co/settings/tokens, never pasted anywhere
    .venv/bin/python scripts/village_spread.py

Only small files are fetched. computer_use_turns.jsonl.gz (~1.14M rows) and the
daily screenshot tars are where the 177 GB lives; this never touches them.

Terms you agreed to when you requested access: research and analysis only, no
training or fine-tuning without written permission, no attempt to re-identify
anyone, cite AI Digest / AI Village, and tell them about resulting publications.
"""
from __future__ import annotations

import gzip
import json
import os
import sys
from collections import defaultdict

REPO = "aidigestorg/ai-village"
SMALL_FILES = ["agents.jsonl.gz", "computer_use_sessions.jsonl.gz"]

#: Fields that could plausibly carry a per-session identity or location. We do not
#: know the schema in advance, so the script reports what it finds rather than
#: assuming, and never prints a raw address.
CANDIDATE_KEYS = ("ip", "ip_address", "client_ip", "host", "machine", "container",
                  "instance", "vm", "session_id", "sandbox", "node", "worker")


def need_token() -> str:
    tok = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if not tok:
        sys.exit("set HF_TOKEN first (huggingface.co/settings/tokens). "
                 "Do not paste it into a chat window.")
    return tok


def fetch(name: str, token: str) -> str:
    from huggingface_hub import hf_hub_download
    return hf_hub_download(REPO, name, repo_type="dataset", token=token)


def read_jsonl_gz(path: str, limit: int | None = None):
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if limit is not None and i >= limit:
                return
            line = line.strip()
            if line:
                yield json.loads(line)


def main() -> int:
    token = need_token()
    print(f"repo: {REPO}\n")

    for name in SMALL_FILES:
        try:
            path = fetch(name, token)
        except Exception as exc:                       # noqa: BLE001
            print(f"!! {name}: {type(exc).__name__}: {exc}")
            print("   (if this is a 401/403, access may still be pending review)")
            continue

        rows = list(read_jsonl_gz(path, limit=5000))
        print(f"== {name}: {len(rows)} row(s) read")
        if not rows:
            continue

        keys = sorted(rows[0].keys())
        print(f"   schema: {', '.join(keys)}")

        interesting = [k for k in keys
                       if any(c in k.lower() for c in CANDIDATE_KEYS)]
        print(f"   identity-ish fields present: {interesting or 'none found'}")

        # the measurement: how many distinct values of each identity-ish field
        # does a single agent present?
        agent_key = next((k for k in ("agent", "agent_id", "agent_name", "name")
                          if k in keys), None)
        if agent_key and interesting:
            for field in interesting:
                spread: dict[str, set] = defaultdict(set)
                for r in rows:
                    a, v = r.get(agent_key), r.get(field)
                    if a is not None and v is not None:
                        spread[str(a)].add(str(v))
                if not spread:
                    continue
                top = sorted(spread.items(), key=lambda kv: -len(kv[1]))[:5]
                print(f"   distinct {field!r} per {agent_key!r} (top 5, values not printed):")
                for a, vals in top:
                    print(f"      {a[:40]:<40} {len(vals)}")
        elif agent_key:
            print(f"   found {agent_key!r} but no identity-ish field to spread over")
        print()

    print("If any agent shows a count well above 1, that is the second corpus "
          "supporting 'a context is not an actor'. Put the number in docs/RESULTS.md "
          "and cite AI Digest / AI Village.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
