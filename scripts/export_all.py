#!/usr/bin/env python3
"""Write the bundle and everything the viewer needs, from a ledger.

Produces:
  bundles/bundle.json  the evidence bundle (rows + leaves + Merkle root)
  viewer/data.js       the viewer payload as a plain global, so the page works
                       from file:// with no server and no network
  viewer/data.json     the same payload for machine readers
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

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="canary.sqlite3")
    ap.add_argument("--bundle", default="bundles/bundle.json")
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    led = Ledger(args.db)
    payload = export(led)
    b = bundle.build(led, note=args.note)
    led.close()

    bundle_path = bundle.write(b, ROOT / args.bundle)
    ok, problems = bundle.verify(b)

    # What the viewer shows for its verification block. Computed here from the real
    # bundle so the page cannot claim a result the bundle does not support.
    verify_payload = {
        "ok": ok,
        "rows": len(b["leaves"]),
        "root_short": b["root"][:4] + "…" + b["root"][-2:],
        "problems": problems,
    }

    (ROOT / "viewer").mkdir(exist_ok=True)
    (ROOT / "viewer" / "data.js").write_text(
        "window.CANARY_DATA = " + json.dumps(payload, indent=1) + ";\n"
        "window.CANARY_VERIFY = " + json.dumps(verify_payload, indent=1) + ";\n",
        encoding="utf-8")
    (ROOT / "viewer" / "data.json").write_text(
        json.dumps({"viewer": payload, "verification": verify_payload}, indent=1),
        encoding="utf-8")

    print(f"bundle   {bundle_path.relative_to(ROOT)}  "
          f"({len(b['leaves'])} rows, root {b['root'][:12]}…)")
    print(f"viewer   viewer/data.js, viewer/data.json")
    print(f"state    {payload['state']}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
