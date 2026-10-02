#!/usr/bin/env python3
"""Trigger a fetch by pasting a canary URL into a public model product, and record
which fetchers come back.

Why this exists
---------------
Waiting for an organic sighting is slow: the published experiment closest to this
one waited two months. Pasting a URL into a chat product is the fast path - the
fetcher that goes and reads it arrives in seconds.

What it honestly shows, and what it does not
--------------------------------------------
A paste-triggered fetch demonstrates that **a fetcher followed a human's paste**.
It is NOT two agents sharing information with each other, and this script will not
let the write-up pretend otherwise. That is why the attribution lives in a separate
file rather than in the ledger: from the server's point of view those requests ARE
organic - a real external client really did fetch a real URL - so relabelling them
inside an append-only ledger would be falsifying a record. Instead we keep a list
of which secrets we published by hand, and the report cross-references it.

Usage
-----
    python3 scripts/trigger_paste.py https://<your-public-host>        # mint + print
    python3 scripts/trigger_paste.py --report                          # what came back
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from canarymaze.ledger import Ledger            # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PASTE_LOG = ROOT / "docs" / "paste_log.json"
SLUG = "q3-supplier-review"

#: A user-agent that is honest about what it is. We are not pretending to be a
#: crawler to get ourselves minted for; the gate treats any client with no browser
#: headers as automated, which this is.
UA = "canary-maze-paste-trigger/1.0 (+https://github.com/)"


def load_log() -> list[dict]:
    if PASTE_LOG.exists():
        return json.loads(PASTE_LOG.read_text(encoding="utf-8"))
    return []


def save_log(entries: list[dict]) -> None:
    PASTE_LOG.parent.mkdir(parents=True, exist_ok=True)
    PASTE_LOG.write_text(json.dumps(entries, indent=1), encoding="utf-8")


def mint_one(base: str) -> tuple[str, str]:
    """Fetch a maze page so a secret is issued to THIS context, and return it."""
    url = base.rstrip("/") + f"/m/{SLUG}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read().decode("utf-8", "replace")
    m = re.search(r'href="(/c/([a-f0-9]+)/[^"]+)"', html)
    if not m:
        raise SystemExit("no canary link on the page - the gate did not treat this "
                         "client as automated, which is a real finding, not a bug")
    return base.rstrip("/") + m.group(1), m.group(2)


def cmd_trigger(base: str) -> int:
    canary, secret = mint_one(base)
    entries = load_log()
    entries.append({
        "secret": secret,
        "canary_url": canary,
        "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "method": "pasted into a public model product by hand",
    })
    save_log(entries)

    print("A secret has been issued to THIS script's request context.\n")
    print(f"  {canary}\n")
    print("Now paste that URL into a public model product and ask it to read the page.")
    print("Any fetch of it by a DIFFERENT context is a sighting.\n")
    print("Then run:  python3 scripts/trigger_paste.py --report\n")
    print("State it in the write-up as paste-triggered. A fetcher following a human's")
    print("paste is not two agents sharing, and claiming otherwise would be the exact")
    print("overclaim this project exists to avoid.")
    return 0


def cmd_report(db: str) -> int:
    entries = load_log()
    if not entries:
        print("no secrets have been published by paste yet.")
        return 0
    published = {e["secret"]: e for e in entries}

    led = Ledger(db)
    sightings = led.rows("sighting")
    counts = led.counts()
    led.close()

    triggered = [s for s in sightings if s["secret"] in published]
    other = [s for s in sightings if s["secret"] not in published]

    print(f"published by paste : {len(published)}")
    print(f"  of those, fetched by another context : {len(triggered)}")
    for s in triggered:
        print(f"    secret {s['secret'][:12]}… after {s['delta_s']:.0f}s")
    print(f"sightings on secrets we did NOT paste : {len(other)}")
    print()
    print("ledger totals (organic / seeded / paste columns are independent):")
    for k in ("sightings_organic", "sightings_seeded", "sightings_paste",
              "mints", "human_requests"):
        print(f"  {k:<20} {counts[k]}")
    print()
    print("Reporting rule: a paste-triggered fetch shows a fetcher following a")
    print("human's paste. Report it as its own category, never as agent-to-agent")
    print("propagation.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base", nargs="?", help="public base URL of the surface")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--db", default="canary.sqlite3")
    args = ap.parse_args()

    if args.report:
        return cmd_report(args.db)
    if not args.base:
        ap.error("give the public base URL, or --report")
    return cmd_trigger(args.base)


if __name__ == "__main__":
    raise SystemExit(main())
