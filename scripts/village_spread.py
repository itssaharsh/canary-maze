#!/usr/bin/env python3
"""Measure how many distinct session contexts one agent presents, in the AI
Village corpus.

Why this exists
---------------
Canary Maze's central honest claim is "a sighting shows a secret moved between
two request CONTEXTS, not that there are two operators". Until this ran, that
claim rested on ONE measurement, from the collusion.wiki dump: a single actor
label carrying 899 revisions across 741 distinct addresses.

This looks for the same shape in a second, independent corpus - the organizers'
own. If one agent presents many session contexts there too, the claim is
supported twice, from unrelated datasets.

An earlier version of this script reported nothing, and the null was an artefact:
it read `agents.jsonl.gz`, which is a CURRENT-STATE table, so
`current_computer_use_session_id` is 1 per agent by construction. The history is
in `computer_use_sessions.jsonl.gz`. A field named `id` is also not "identity-ish"
by name, which is how the earlier key-matching heuristic walked past the only
column that answers the question. Measure the join you mean, not the one whose
name looks right.

The build does not depend on this. It is evidence for the write-up.

Usage
-----
    export HF_TOKEN=...            # huggingface.co/settings/tokens
    python3 scripts/village_spread.py [--json docs/village_spread.json]

Terms agreed to when access was requested: research and analysis only, no
training or fine-tuning without written permission, no attempt to re-identify
anyone, cite AI Digest / AI Village, and tell them about resulting publications.
No identifier, goal or message content is printed or stored by this script - only
counts and model names that the dataset itself publishes.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "aidigestorg/ai-village"

#: Each is (file, the column holding the SESSION identity). Both are histories,
#: one row per session, joined to an agent by agent_id.
SESSION_TABLES = (
    ("computer_use_sessions.jsonl.gz", "id"),
    ("claude_code_sessions.jsonl.gz", "id"),
)


def need_token() -> str:
    tok = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if not tok:
        sys.exit("set HF_TOKEN first (huggingface.co/settings/tokens).")
    return tok


def rows(name: str, token: str):
    from huggingface_hub import hf_hub_download
    path = hf_hub_download(REPO, name, repo_type="dataset", token=token)
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def measure(token: str) -> dict:
    names = {r["id"]: r.get("name", "unknown") for r in rows("agents.jsonl.gz", token)}
    out: dict = {"repo": REPO, "agents_in_corpus": len(names), "tables": {}}

    for fname, idfield in SESSION_TABLES:
        spread: dict[str, set] = defaultdict(set)
        total = 0
        try:
            for r in rows(fname, token):
                a, s = r.get("agent_id"), r.get(idfield)
                if a and s:
                    spread[a].add(s)
                    total += 1
        except Exception as exc:                      # noqa: BLE001
            out["tables"][fname] = {"error": f"{type(exc).__name__}: {exc}"}
            continue
        if not spread:
            out["tables"][fname] = {"error": f"no agent_id/{idfield} pairs"}
            continue

        counts = sorted((len(v) for v in spread.values()), reverse=True)
        ranked = sorted(spread.items(), key=lambda kv: -len(kv[1]))
        out["tables"][fname] = {
            "rows": total,
            "agents": len(spread),
            "max_sessions_for_one_agent": counts[0],
            "median_sessions_per_agent": int(statistics.median(counts)),
            "agents_with_more_than_one_session": sum(1 for c in counts if c > 1),
            # model names are published by the dataset itself; no identifiers here
            "top": [{"agent": names.get(a, "unknown"), "sessions": len(v)}
                    for a, v in ranked[:10]],
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", default="docs/village_spread.json")
    args = ap.parse_args()

    result = measure(need_token())
    print(f"repo: {result['repo']}")
    print(f"agents in corpus: {result['agents_in_corpus']}\n")
    for fname, t in result["tables"].items():
        if "error" in t:
            print(f"== {fname}: {t['error']}\n")
            continue
        print(f"== {fname}: {t['rows']} sessions across {t['agents']} agents")
        for row in t["top"][:8]:
            print(f"      {row['agent'][:38]:<38} {row['sessions']:>6}")
        print(f"   max {t['max_sessions_for_one_agent']}  "
              f"median {t['median_sessions_per_agent']}  "
              f"agents with >1 session: "
              f"{t['agents_with_more_than_one_session']}/{t['agents']}\n")

    path = ROOT / args.json
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(f"written: {args.json}")
    print("\nEvery agent presenting more than one session is the second corpus "
          "supporting 'a context is not an actor'. Cite AI Digest / AI Village.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
