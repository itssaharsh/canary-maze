"""Signed hand-off of one request's metadata from a public edge to this ledger.

Why this exists
---------------
The surface has to be reachable by the clients it exists to observe. Measured on
2026-10-03, the Cloudflare quick tunnel refuses GPTBot, ClaudeBot, PerplexityBot,
CCBot and Bytespider at its edge, and replaces our robots.txt with its own
(F-0005). Vercel refuses none of them. So the public surface moves to Vercel while
the ledger stays here, which keeps ADR-0005: the bundle a third party verifies is
built from the same file that collected the evidence.

What this costs, stated plainly
-------------------------------
The ledger no longer sees the client. It records what an edge *reported* about the
client. That is one more hop of the same kind we already accept by trusting
Cloudflare's CF-Connecting-IP, but it is not free, so:

  * every forwarded row carries `via`, naming the edge that reported it, and the
    viewer and bundle show it. A reader can tell a directly observed row from a
    reported one rather than having to take the whole ledger on trust;
  * the hand-off is signed with a shared key and timestamped, so an outsider
    cannot post invented rows into the ledger - which would otherwise be a far
    worse hole than the one we are fixing, since the ledger is append-only and a
    forged row could never be removed.

The signature authenticates the EDGE, not the client. Nothing here can tell you
the edge reported honestly. See docs/memory/decisions/ADR-0006.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time

#: How far apart the edge's clock and ours may be before we refuse the row. Long
#: enough for a cold serverless start, short enough that a captured request body
#: cannot be replayed into the ledger later.
MAX_SKEW_S = 300

SIG_HEADER = "X-Canary-Ingest-Sig"
TS_HEADER = "X-Canary-Ingest-Ts"


def canonical(payload: dict) -> bytes:
    """One byte-for-byte spelling of a payload, so both sides sign the same thing."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("utf-8")


def sign(payload: dict, ts: str, key: str) -> str:
    return hmac.new(key.encode("utf-8"),
                    ts.encode("ascii") + b"." + canonical(payload),
                    hashlib.sha256).hexdigest()


def verify(payload: dict, ts: str, sig: str, key: str,
           *, now: float | None = None) -> tuple[bool, str]:
    """Return (ok, reason). Never raises: a bad hand-off is refused, not a 500."""
    if not key:
        return False, "no ingest key configured; the endpoint is disabled"
    if not sig or not ts:
        return False, "missing signature or timestamp"
    try:
        sent = float(ts)
    except ValueError:
        return False, "unparseable timestamp"
    drift = abs((now if now is not None else time.time()) - sent)
    if drift > MAX_SKEW_S:
        return False, f"timestamp {drift:.0f}s out of range (max {MAX_SKEW_S}s)"
    if not hmac.compare_digest(sign(payload, ts, key), sig):
        return False, "signature does not match"
    return True, "ok"


def ingest_key() -> str:
    return os.environ.get("CANARY_INGEST_KEY", "").strip()
