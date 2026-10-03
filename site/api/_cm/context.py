"""Derive a REQUEST CONTEXT identifier.

A context is not an actor and this module must never be read as producing one.
One operator can present as many contexts: in the AI Village collusion.wiki dump a
single actor label carries 899 revisions across 741 distinct addresses. So a
sighting across two contexts establishes that a secret moved between two request
contexts, and that is the whole of the claim. See docs/memory/decisions/ADR-0002.

The identifier is built from the parts of a request that a client does not vary
casually between two fetches a few minutes apart, hashed so that the identifier
itself carries no address and no user-agent string:

  - the user-agent verbatim
  - the network, already truncated to /24 or /48
  - Accept and Accept-Encoding
  - the ORDER of the header names, which is a property of the HTTP stack rather
    than of anything the caller typed

Deliberately NOT included: the full address (we never hold one), cookies, and any
value that would let a context be reversed back to a person.
"""
from __future__ import annotations

import hashlib
from typing import Mapping

from .netaddr import truncate_ip

#: Headers that vary per request rather than per client, so they would make the
#: identifier unstable without telling us anything about the client.
_VOLATILE = {"cookie", "authorization", "referer", "if-none-match",
             "if-modified-since", "range", "content-length", "host",
             "connection", "date", "x-request-id"}


def header_order_fingerprint(headers: Mapping[str, str]) -> str:
    """The sequence of header names, which differs between HTTP stacks."""
    names = [str(k).lower() for k in headers.keys() if str(k).lower() not in _VOLATILE]
    return ",".join(names)


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
