"""What the viewer reads.

The viewer renders EVERY line of its copy from this payload. Nothing it says is
hardcoded in the page. That is a correctness requirement, not a style preference:
a fresh evaluator given only screenshots of an earlier hardcoded version found
three on-screen contradictions - a state whose headline said no second context had
been seen while a populated second-context card sat beside it, an error state that
asserted a sighting it had just said it could not read, and a scope paragraph that
was byte-identical across every state. A tool whose entire thesis is honesty cannot
contradict itself on screen. See docs/memory/feedback/U-0001.

So this module computes the claim, the scope line and the state, and the viewer is
left with no opportunity to invent any of them.
"""
from __future__ import annotations

from typing import Any

from .context import label
from .ledger import Ledger

#: The sentence that bounds the claim. It is attached to the payload rather than
#: written into the page so it travels with the data into the bundle, the README
#: and the write-up, and cannot drift between them.
SCOPE_LINE = (
    "A sighting establishes that the secret moved between two request contexts. "
    "It does not establish that they are two different operators - one operator "
    "can rotate addresses. In the AI Village dump, one actor label spans 741 of them."
)


def _hhmmss(ts: str) -> str:
    return ts[11:19] if len(ts) >= 19 else ts


def human_delta(seconds: float) -> str:
    s = int(round(seconds))
    if s < 1:
        # The seeded replay genuinely completes within one second. Saying "4m 35s"
        # here would be a lie in a record, so the copy reads naturally instead.
        return "within the same second"
    if s < 60:
        return f"{s}s"
    m, s = divmod(s, 60)
    if m < 60:
        return f"{m}m {s:02d}s" if s else f"{m}m"
    h, m = divmod(m, 60)
    return f"{h}h {m:02d}m"


def export(led: Ledger) -> dict[str, Any]:
    counts = led.counts()
    mints = led.rows("mint")
    sightings = led.rows("sighting")
    requests = {r["id"]: r for r in led.rows("request")}

    seen_ctx: list[str] = []
    out_sightings = []
    for s in sightings:
        mint_req = requests.get(s["mint_request_id"], {})
        seen_req = requests.get(s["seen_request_id"], {})
        a = label(s["mint_ctx_id"], seen_ctx)
        b = label(s["seen_ctx_id"], seen_ctx)
        out_sightings.append({
            "secret": s["secret"],
            "origin": s["origin"],
            "elapsed": human_delta(s["delta_s"]),
            "elapsed_s": s["delta_s"],
            "issued": {
                "label": a, "ctx_id": s["mint_ctx_id"],
                "at": _hhmmss(mint_req.get("ts", "")),
                "ua": mint_req.get("ua", ""), "net": mint_req.get("ip_net", ""),
                "raw": mint_req.get("raw_line", ""),
            },
            "requested": {
                "label": b, "ctx_id": s["seen_ctx_id"],
                "at": _hhmmss(seen_req.get("ts", "")),
                "ua": seen_req.get("ua", ""), "net": seen_req.get("ip_net", ""),
                "raw": seen_req.get("raw_line", ""),
            },
        })

    # The state, decided here so the viewer cannot choose a different one.
    if out_sightings:
        state = "sighting"
    elif mints:
        state = "awaiting"
    else:
        state = "empty"

    return {
        "state": state,
        "scope_line": SCOPE_LINE,
        "claim": _claim(state, out_sightings, mints),
        "counts": counts,
        "sightings": out_sightings,
        "mint_sample": _mint_sample(mints, requests, state),
    }


def _claim(state: str, sightings: list[dict], mints: list[dict]) -> str:
    """Derived, never hardcoded. Each state gets a sentence that is true in it."""
    if state == "sighting":
        s = sightings[0]
        when = (s["elapsed"] if s["elapsed"].startswith("within")
                else f"{s['elapsed']} later")
        # "on a different network" is DERIVED, never asserted: it is only said when
        # the two truncated networks actually differ. Asserting it unconditionally
        # is the mistake U-0001 was written about.
        where = ("" if s["issued"]["net"] == s["requested"]["net"]
                 else ", on a different network")
        claim = (f"A URL that only context {s['issued']['label']} was ever shown was "
                 f"requested {when} by context {s['requested']['label']}{where}.")
        if s["origin"] == "selftest":
            # The operator fetched their own canary. Mechanically a sighting, and
            # worth nothing as evidence. Saying so in the headline is cheaper than
            # letting a reader discover it in the raw rows.
            claim += " This was the operator's own probe, not third-party traffic."
        return claim
    if state == "awaiting":
        n = len(mints)
        return (f"{n} secret{'s' if n != 1 else ''} issued. No other context has "
                f"requested any of them yet.")
    return "No secrets issued yet. Start the surface and let a crawler reach it."


def _mint_sample(mints: list[dict], requests: dict, state: str) -> dict[str, Any] | None:
    """Shown ONLY in the awaiting state, so the page has something real to display
    without inventing a second context that does not exist. Returns None otherwise:
    an earlier version emitted it unconditionally, contradicting this docstring."""
    if state != "awaiting" or not mints:
        return None
    m = mints[-1]
    req = requests.get(m["request_id"], {})
    # The secret is NOT published. /export.json is public, and emitting the live
    # secret let any reader fetch the canary themselves and manufacture an
    # `origin='organic'` sighting with two unauthenticated GETs - which made the
    # one number this project asks to be believed on remotely writable.
    return {
        "secret_prefix": m["secret"][:4] + "\u2026",
        "at": _hhmmss(m["ts"]),
        "ua": req.get("ua", ""),
        "net": req.get("ip_net", ""),
        # the raw line embeds the canary path, so redact the secret out of it too
        "raw": req.get("raw_line", "").replace(m["secret"], m["secret"][:4] + "\u2026"),
    }
