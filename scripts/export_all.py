#!/usr/bin/env python3
"""Write the bundle and everything the viewer needs, from a ledger.

Produces:
  <bundle>             the evidence bundle (rows + leaves + Merkle root)
  <out>/data.js        the viewer payload and the bundle as plain globals, so the
                       page works from file:// with no server and no network
  <out>/data.json      the same two objects for machine readers

Two rules this script enforces, because each was broken once:

1. The payload and the bundle come from ONE snapshot, and the bundle commits to
   the payload. The page displays the payload and verifies the bundle; before the
   bundle carried a digest of the payload, a reader could edit what was displayed
   and still be told "Verified".

2. Publishing a bundle publishes its secrets. A bundle holds every mint row in
   full, so anyone who can read data.js can fetch a canary URL and - before this
   rule - have that counted as an organic sighting. A ledger that holds anything
   other than the seeded replay can therefore only be exported with --publish,
   which first records every one of its secrets in the `published` table. From
   that moment a fetch of them is reported as paste-triggered, and the bundle
   itself carries the disclosure.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from canarymaze import bundle                     # noqa: E402
from canarymaze.export import export              # noqa: E402
from canarymaze.ledger import Ledger              # noqa: E402
from canarymaze.paths import ledger_path, load_env  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PUBLISH_METHOD = "included in a published bundle"


def unpublished_live_secrets(led: Ledger) -> list[str]:
    """Secrets issued to anything but the seeded replay that are not yet disclosed."""
    origin = {r["id"]: r["origin"] for r in led.rows("request")}
    disclosed = {p["secret"] for p in led.rows("published")}
    return [m["secret"] for m in led.rows("mint")
            if origin.get(m["request_id"]) != "seeded" and m["secret"] not in disclosed]


def build(led: Ledger, note: str) -> tuple[dict, dict]:
    """(payload, bundle) from a single read snapshot, the bundle bound to the payload."""
    with led.snapshot():
        payload = export(led)
        b = bundle.build(led, note=note, viewer=bundle.payload_digest(payload))
    return payload, b


load_env()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=None,
                    help="ledger to use (default: $CANARY_DB, else the live one)")
    ap.add_argument("--bundle", default="bundles/bundle.json")
    ap.add_argument("--out", default="viewer", help="directory for data.js and data.json")
    ap.add_argument("--note", default="")
    ap.add_argument("--publish", action="store_true",
                    help="record every secret in this ledger as published, then export")
    args = ap.parse_args()
    args.db = ledger_path(args.db)

    led = Ledger(args.db)
    pending = unpublished_live_secrets(led)
    if pending and not args.publish:
        led.close()
        print(f"refusing to export: this ledger holds {len(pending)} secret(s) issued to "
              "real clients that have not been disclosed.\n"
              "  A bundle carries every secret in full, so publishing it lets any reader "
              "fetch a canary URL.\n"
              "  Re-run with --publish to record them as published first; from then on a "
              "fetch of them is\n  reported as paste-triggered, never organic.",
              file=sys.stderr)
        return 2
    for secret in pending:
        led.record_published(secret=secret, method=PUBLISH_METHOD)
    payload, b = build(led, args.note)
    led.close()

    bundle_path = bundle.write(b, ROOT / args.bundle)
    ok, problems = bundle.verify(b)
    problems = problems + bundle.verify_display(b, payload)

    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    (out / "data.js").write_text(
        "window.CANARY_DATA = " + json.dumps(payload, indent=1) + ";\n"
        "window.CANARY_BUNDLE = " + json.dumps(b, indent=1) + ";\n",
        encoding="utf-8")
    (out / "data.json").write_text(
        json.dumps({"viewer": payload, "bundle": b}, indent=1), encoding="utf-8")

    shown = bundle_path.relative_to(ROOT) if bundle_path.is_relative_to(ROOT) else bundle_path
    print(f"bundle   {shown}  "
          f"({len(b['leaves'])} rows, root {b['root'][:12]}…)")
    print(f"viewer   {args.out}/data.js, {args.out}/data.json")
    print(f"state    {payload['state']}")
    if pending:
        print(f"published {len(pending)} secret(s) recorded as disclosed before export")
    for prob in problems:
        print(f"PROBLEM  {prob}", file=sys.stderr)
    return 0 if ok and not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
