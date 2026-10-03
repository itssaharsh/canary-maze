#!/usr/bin/env python3
"""Hand a canary URL to someone by hand, and record that you did.

Why this exists
---------------
Waiting for an organic sighting is slow: the published experiment closest to this
one waited two months. Handing a URL to something that fetches - pasting it into a
chat product, giving it to a fetch service - gets a real third-party request in
seconds.

What it honestly shows, and what it does not
--------------------------------------------
It shows that **a fetcher followed a link the operator published**. It is NOT two
clients sharing information with each other, and nothing here lets the write-up
pretend otherwise.

The server cannot tell the two apart: both arrive as real third-party requests
with no operator marker, so both are recorded with `origin='organic'`. What
separates them is that the operator knows which secrets they handed out. So this
script writes that fact into the ledger - a row in the append-only `published`
table, at the moment of publishing - and every count, the viewer and the bundle
then report a fetch that comes AFTER it as paste-triggered. The reclassification
only runs in that direction: publishing can never turn something into organic
evidence, and publishing later cannot rewrite what was organic when it happened.

An earlier version kept this in docs/paste_log.json, which this script read and
nothing else did. The viewer would have shown a pasted link's fetch as organic.

Usage
-----
    python3 scripts/trigger_paste.py --to "pasted into ChatGPT"     # mint, record, print
    python3 scripts/trigger_paste.py --report                        # what came back
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from canarymaze.ledger import Ledger            # noqa: E402
from canarymaze.paths import ledger_path, load_env  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = "https://site-nine-hazel-35.vercel.app"
SLUG = "q3-supplier-review"


def user_agent(tag: str) -> str:
    """Honest about what it is. The tag exists because a secret is a pure function
    of (path, context): one context gets ONE secret per page per day. A distinct
    tag is a distinct context, which is how each recipient gets a URL of its own
    and a fetch can be attributed to the place the URL was handed to."""
    return f"canary-maze-paste-trigger/1.0 (+https://github.com/itssaharsh/canary-maze; tag={tag})"


def mint_one(base: str, *, slug: str = SLUG, tag: str = "default") -> tuple[str, str]:
    """Fetch a maze page so a secret is issued to THIS context, and return it.

    The request is the OPERATOR's. It carries the self-test token (and, from the
    operator's own network, is recognised without it), so it is recorded as
    `origin='selftest'` and can never be counted as evidence.
    """
    url = base.rstrip("/") + f"/m/{slug}"
    headers = {"User-Agent": user_agent(tag), "Accept": "text/html"}
    token = os.environ.get("CANARY_SELFTEST_TOKEN", "").strip()
    if token:
        headers["X-Canary-Selftest"] = token
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8", "replace")
    m = re.search(r'href="(/c/([a-f0-9]+)/[^"]+)"', html)
    if not m:
        raise SystemExit("no canary link on the page - the gate did not treat this "
                         "client as automated, which is a real finding, not a bug")
    return base.rstrip("/") + m.group(1), m.group(2)


def publish(db: str, base: str, method: str, *, slug: str = SLUG, tag: str = "default",
            wait_s: float = 12.0) -> str:
    """Mint a URL, confirm the ledger saw the mint, record the disclosure, return it.

    The order is the point. If the ledger never records the mint, the collection
    path is down and a fetch of this URL would be served and never written - so
    the URL is not handed out at all. And the `published` row is written BEFORE
    the URL is returned, so no fetch can ever precede its own disclosure.
    """
    canary, secret = mint_one(base, slug=slug, tag=tag)
    led = Ledger(db)
    try:
        deadline = time.time() + wait_s
        while led.mint_for_secret(secret) is None:
            if time.time() > deadline:
                raise SystemExit(
                    "the ledger did not record this mint, so the collection path is "
                    "down and a fetch of this URL would be lost.\n"
                    "  bring it up:  nohup bash scripts/keep_alive.sh > .keepalive.log 2>&1 &\n"
                    "The URL was NOT published.")
            time.sleep(0.5)
        led.record_published(secret=secret, method=method)
    finally:
        led.close()
    return canary


def cmd_trigger(db: str, base: str, method: str, slug: str, tag: str) -> int:
    canary = publish(db, base, method, slug=slug, tag=tag)
    print("A secret has been issued to THIS script's request context, and the ledger")
    print(f"now records that it was published: {method!r}.\n")
    print(f"  {canary}\n")
    print("Hand that URL over. Any fetch of it by a different context is a sighting,")
    print("reported as PASTE-TRIGGERED: a fetcher following a link you published.\n")
    print("Then:  python3 scripts/trigger_paste.py --report")
    return 0


def report_rows(db: str) -> list[dict]:
    """One entry per published secret, with every context that fetched it after."""
    led = Ledger(db)
    try:
        published = led.rows("published")
        requests = {r["id"]: r for r in led.rows("request")}
        sightings = led.rows("sighting")
    finally:
        led.close()
    out, seen = [], set()
    for p in published:
        if p["secret"] in seen:
            continue
        seen.add(p["secret"])
        fetches = []
        for s in sightings:
            if s["secret"] != p["secret"] or s["ts"] < p["ts"]:
                continue
            r = requests.get(s["seen_request_id"], {})
            fetches.append({"ctx": s["seen_ctx_id"], "ua": r.get("ua", ""),
                            "net": r.get("ip_net", ""), "via": r.get("via", ""),
                            "origin": s["origin"], "after_s": s["delta_s"]})
        out.append({"secret": p["secret"], "method": p["method"], "ts": p["ts"],
                    "fetches": fetches})
    return out


def cmd_report(db: str) -> int:
    rows = report_rows(db)
    print(f"reading ledger: {db}")
    if not rows:
        print("no secrets have been published by hand yet.")
        return 0
    hit = sum(1 for r in rows if any(f["origin"] != "selftest" for f in r["fetches"]))
    print(f"published by hand: {len(rows)}   fetched by a third party afterwards: {hit}\n")
    for r in rows:
        print(f"  {r['secret'][:6]}…  {r['ts']}  {r['method']}")
        if not r["fetches"]:
            print("      no fetch recorded")
        for f in r["fetches"]:
            who = "operator's own probe" if f["origin"] == "selftest" else "third party"
            print(f"      +{f['after_s']:.0f}s  {who}  {f['net']:<18} via {f['via']:<7} {f['ua'][:60]}")
    led = Ledger(db)
    c = led.counts()
    led.close()
    print()
    for k in ("sightings_organic", "sightings_paste", "sightings_seeded",
              "sightings_selftest", "humans_turned_away"):
        print(f"  {k:<20} {c[k]}")
    print("\nReporting rule: a paste-triggered fetch shows a fetcher following a link the")
    print("operator published. It is its own category, never agent-to-agent propagation.")
    return 0


load_env()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base", nargs="?", default=os.environ.get("CANARY_PUBLIC_URL", DEFAULT_BASE),
                    help=f"public base URL of the surface (default: {DEFAULT_BASE})")
    ap.add_argument("--to", default="pasted into a public model product by hand",
                    help="where the URL is going, in your own words; recorded in the ledger")
    ap.add_argument("--slug", default=SLUG)
    ap.add_argument("--tag", default=None,
                    help="a distinct tag gives a distinct URL (default: derived from --to)")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--db", default=None,
                    help="ledger to use (default: $CANARY_DB, else the live one)")
    args = ap.parse_args()
    args.db = ledger_path(args.db)

    if args.report:
        return cmd_report(args.db)
    tag = args.tag or re.sub(r"[^a-z0-9]+", "-", args.to.lower()).strip("-")[:40] or "default"
    return cmd_trigger(args.db, args.base, args.to, args.slug, tag)


if __name__ == "__main__":
    raise SystemExit(main())
