"""Sighting detection.

The single branching function in the product, and the one a reviewer should attack
first. It answers exactly one question:

    did a secret issued to one request context get fetched by a DIFFERENT one?

It deliberately does not answer "are these two operators?", because it cannot and
neither can anything else here. See docs/memory/decisions/ADR-0002.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from .ledger import Ledger


def _parse(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def on_canary_request(led: Ledger, *, secret: str, seen_ctx_id: str,
                      seen_request_id: int, origin: str = "organic") -> int | None:
    """Return the new sighting id, or None when this is not a sighting.

    Not a sighting, in order:
      - the secret was never issued by us (someone guessed, or a stale epoch);
      - the context fetching it is the one it was issued to (a crawler re-reading
        its own page is the common case, and it proves nothing);
      - this context has already been recorded against this secret.
    """
    m = led.mint_for_secret(secret)
    if m is None:
        return None
    if m["ctx_id"] == seen_ctx_id:
        return None

    seen = led.request(seen_request_id)
    if seen is None:
        return None
    try:
        delta = (_parse(seen["ts"]) - _parse(m["ts"])).total_seconds()
    except ValueError:
        # an unparseable timestamp is not a sighting we can date, and raising here
        # would 500 the canary route and lose the observation entirely
        return None
    if delta < 0:
        # A fetch cannot precede the mint that issued the secret. The earlier
        # version clamped this to 0.0 and wrote the row anyway, so a sighting dated
        # 30 minutes BEFORE its mint was published as "requested within the same
        # second". Clock skew is a reason to refuse the record, not to round it.
        return None

    try:
        return led.record_sighting(
            secret=secret, mint_ctx_id=m["ctx_id"], seen_ctx_id=seen_ctx_id,
            mint_request_id=int(m["request_id"]), seen_request_id=seen_request_id,
            delta_s=delta, origin=origin, ts=seen["ts"])
    except sqlite3.IntegrityError:
        # UNIQUE(secret, seen_ctx_id): already recorded. One sighting per pair.
        return None
