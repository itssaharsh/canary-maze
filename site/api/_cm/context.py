"""Derive a REQUEST CONTEXT identifier.

A context is not an actor and this module must never be read as producing one.
One operator can present as many contexts: in the organizers' collusion.wiki dump
the busiest named agent label wrote 317 revisions from 308 distinct addresses,
and 1740 of the 1768 named agent labels with two or more revisions wrote
from more than one /16 network (scripts/label_spread.py). So a
sighting across two contexts establishes that a secret moved between two request
contexts, and that is the whole of the claim. See docs/memory/decisions/ADR-0002.

The identifier is built from the parts of a request that a client does not vary
casually between two fetches a few minutes apart, hashed so that the identifier
itself carries no address and no user-agent string:

  - the user-agent verbatim
  - the network, already truncated to /24 or /48
  - Accept and Accept-Encoding
  - WHICH of the standard request headers the client sends at all, which is a
    property of its HTTP stack rather than of anything the caller typed

Deliberately NOT included: the full address (we never hold one), cookies, and any
value that would let a context be reversed back to a person.

Also deliberately not included, and this one was learned the hard way (F-0006):
any header that is not on the CLIENT_HEADERS allowlist, and the ORDER of the ones
that are. An earlier version fingerprinted the order of every header name it saw.
Behind a hosting platform that injects its own headers - a different set on
different routes - one client fetching a page and then following its own link came
out as two contexts, and the commonest harmless event there is was recorded as a
sighting. A context that is too easy to split manufactures evidence; one that is
too coarse only loses some. The gate chooses to lose sightings rather than ledger
a human, and this module makes the same choice in the same direction.
"""
from __future__ import annotations

import hashlib
from typing import Mapping

from .netaddr import truncate_ip

#: Request headers that a CLIENT's HTTP stack chooses to send. Only these take part
#: in the fingerprint. It is an allowlist on purpose: a denylist of "volatile"
#: headers has to anticipate every header every proxy, CDN and platform will ever
#: inject, and the one it misses splits a client in two. Anything not named here -
#: x-forwarded-*, x-vercel-*, cf-*, cookies, a made-up X-Trace - is invisible.
CLIENT_HEADERS: frozenset[str] = frozenset({
    "user-agent", "accept", "accept-encoding", "accept-language", "accept-charset",
    "cache-control", "pragma", "upgrade-insecure-requests", "dnt", "te", "priority",
    "from", "purpose", "sec-purpose", "sec-gpc",
    "sec-ch-ua", "sec-ch-ua-mobile", "sec-ch-ua-platform",
    "sec-fetch-site", "sec-fetch-mode", "sec-fetch-dest", "sec-fetch-user",
})


def header_order_fingerprint(headers: Mapping[str, str]) -> str:
    """Which standard client headers are present - sorted, so order is ignored.

    The name is historical: it used to be the order. It is kept because the
    Vercel function imports a copy of this module and a rename would have to land
    in both places at once.
    """
    present = {str(k).lower() for k in headers.keys()} & CLIENT_HEADERS
    return ",".join(sorted(present))


def derive(headers: Mapping[str, str], ip: str) -> str:
    """Return a stable 12-hex-character context id."""
    h = {str(k).lower(): v for k, v in headers.items()}
    material = "\x1f".join([
        h.get("user-agent", ""),
        truncate_ip(ip),
        h.get("accept", ""),
        h.get("accept-encoding", ""),
        header_order_fingerprint(headers),
    ])
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:12]


def label(ctx_id: str, known: list[str] | None = None) -> str:
    """A short human label ("A", "B", "C"...) for display only.

    Order of first appearance, so the viewer can say "context A" without implying
    that A is a person. Never persisted, never part of the proof.
    """
    if known is None:          # `known or []` would silently discard an
        known = []             # empty list the caller passed in to accumulate
    if ctx_id not in known:
        known.append(ctx_id)
    i = known.index(ctx_id)
    out = ""
    while True:
        out = chr(ord("A") + i % 26) + out
        i = i // 26 - 1
        if i < 0:
            return out
