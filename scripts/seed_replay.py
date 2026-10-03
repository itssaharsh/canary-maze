#!/usr/bin/env python3
"""The seeded two-client replay - the PRIMARY deliverable, not a fallback.

Why this is primary
-------------------
The published experiment closest to this one (arXiv:2605.13706, Duke, revised
2026-09-03) waited TWO MONTHS for its tokens to surface. This build has about 31
hours. Waiting for an organic sighting and hoping is not a plan, and "deployed,
nothing yet" is not a result for a project whose whole thesis is that you should
manufacture evidence rather than infer it.

So the replay drives two clients we control through the REAL code path - the real
gate, the real context derivation, the real mint, the real detector - and the rows
it produces are marked origin='seeded' everywhere they appear. The organic counter
is never touched by this script. A reader always sees which is which.

What it does NOT do: fabricate rows, write to the ledger directly, or bypass any
check. If the gate rejected these clients, or the detector refused the pairing,
this script would produce nothing, and that is the point.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from canarymaze.app import create_app            # noqa: E402
from canarymaze.paths import ledger_path, load_env  # noqa: E402
from canarymaze.ledger import Ledger             # noqa: E402

# Two clients that differ in every way the detector looks at: declared purpose,
# user-agent family, and network. Shaped after the pattern Cloudflare documented
# in August 2025 - a crawler and a desktop-Chrome fetcher from a different ASN.
CRAWLER = {
    "User-Agent": ("Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; "
                   "GPTBot/1.2; +https://openai.com/gptbot)"),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Encoding": "gzip, deflate",
}
CRAWLER_IP = "20.171.207.14"

FETCHER = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}
FETCHER_IP = "104.28.52.9"

SLUG = "q3-supplier-review"


def canary_url_from(html: str) -> str:
    m = re.search(r'href="(/c/[^"]+)"', html)
    if not m:
        raise SystemExit("the maze page carried no canary link - the gate rejected "
                         "the crawler, which is a real failure, not a seeding problem")
    return m.group(1)


def run(db_path: str) -> int:
    # origin="seeded" marks every row this run writes, at write time.
    app = create_app(db_path=db_path, origin="seeded")
    with app.test_client() as c:
        page = c.get(f"/m/{SLUG}", headers=CRAWLER,
                     environ_overrides={"REMOTE_ADDR": CRAWLER_IP})
        if page.status_code != 200:
            raise SystemExit(f"maze page returned {page.status_code}")
        url = canary_url_from(page.get_data(as_text=True))

        hit = c.get(url, headers=FETCHER, environ_overrides={"REMOTE_ADDR": FETCHER_IP})
        if hit.status_code != 200:
            raise SystemExit(f"canary returned {hit.status_code}; it must be 200 for "
                             "every context or a sighting is impossible")

    led = Ledger(db_path)
    counts = led.counts()
    led.close()
    return counts


load_env()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=None,
                    help="ledger to use (default: $CANARY_DB, else the live one)")
    args = ap.parse_args()
    args.db = ledger_path(args.db)

    counts = run(args.db)
    print(f"seeded replay complete against {args.db}")
    print(f"  mints              {counts['mints']}")
    print(f"  sightings seeded   {counts['sightings_seeded']}")
    print(f"  sightings organic  {counts['sightings_organic']}")
    print(f"  human requests     {counts['human_requests']}  (must be 0)")
    if counts["human_requests"] != 0:
        raise SystemExit("a human request reached the ledger - the gate is broken")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
