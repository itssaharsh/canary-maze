"""The public canary surface, served from Vercel.

It lives here and not on the tunnel because the tunnel's edge refuses the clients
this product exists to observe: measured 2026-10-03, Cloudflare quick tunnels
return 403 to GPTBot, ClaudeBot, PerplexityBot, CCBot and Bytespider, and replace
our robots.txt with their own (F-0005). Vercel refuses none of them.

The ledger stays on the operator's machine (ADR-0005), so this function computes
everything it needs without a database - the secret is a pure HMAC of the salt,
the path and the request context - and then REPORTS the request to the ledger
over a signed hand-off (ADR-0006). If that report fails, the page is still served:
a blocked crawler is a lost observation, which is strictly worse than a missing
row, and the contract has said so from the start.

Stdlib only, deliberately: no requirements.txt means no build step to break on
the day of a deadline.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _cm import maze, mint                      # noqa: E402
from _cm.context import CLIENT_HEADERS, derive  # noqa: E402
from _cm.gate import is_automated               # noqa: E402
from _cm.ingest import SIG_HEADER, TS_HEADER, sign  # noqa: E402

EDGE_NAME = "vercel"
INGEST_TIMEOUT_S = 3.0

#: The only request headers that ever leave this function. The ledger needs the
#: client's own headers to run the gate and derive the context, plus the operator's
#: self-test marker - and nothing else. An earlier version forwarded every header
#: it received, which sent cookies and authorization values of automated clients
#: across a tunnel to a machine that had no use for them, and (F-0006) let the
#: platform's own injected headers reach the context fingerprint.
FORWARD = CLIENT_HEADERS | {"x-canary-selftest"}


#: What the ledger is told when a browser is turned away: that it happened. No
#: address, no user-agent, no header, no path - the gate exists so that nothing
#: about a human is kept, and that has to hold for what leaves the edge too. The
#: one thing that must still move is the counter, or "humans are excluded" stops
#: being a claim anyone could check on the only surface the public can reach.
GATE_REPORT = {"kind": "gate", "via": EDGE_NAME}


def forwardable(headers: dict) -> dict:
    """The client's own headers, lower-cased, and only the ones the ledger uses."""
    out = {}
    for k, v in headers.items():
        name = str(k).lower()
        if name in FORWARD and name not in out:
            out[name] = str(v)
    return out


def client_ip(headers) -> str:
    """The client's address as Vercel reports it.

    Vercel sets x-vercel-forwarded-for itself and it cannot be spoofed by the
    client; x-forwarded-for can be appended to, so its left-most entry is
    attacker-controlled and is only a fallback.
    """
    for name in ("x-vercel-forwarded-for", "x-real-ip"):
        v = (headers.get(name) or "").strip()
        if v:
            return v.split(",")[0].strip()
    xff = (headers.get("x-forwarded-for") or "").strip()
    return xff.split(",")[0].strip() if xff else "0.0.0.0"


def report(payload: dict) -> bool:
    """Tell the ledger what we saw. Never raises: the page must be served anyway."""
    base = (os.environ.get("CANARY_INGEST_URL") or "").strip().rstrip("/")
    key = (os.environ.get("CANARY_INGEST_KEY") or "").strip()
    if not base or not key:
        return False
    ts = str(time.time())
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("utf-8")
    req = urllib.request.Request(
        base + "/ingest", data=body, method="POST",
        headers={"Content-Type": "application/json",
                 TS_HEADER: ts, SIG_HEADER: sign(payload, ts, key)})
    try:
        with urllib.request.urlopen(req, timeout=INGEST_TIMEOUT_S) as r:
            return 200 <= r.status < 300
    except (urllib.error.URLError, OSError, ValueError):
        return False


def respond(path: str, headers: dict, ip: str, base: str):
    """Decide the response for one GET. Pure: no network, no socket.

    Returns (status, content_type, body, report) where `report` is the payload to
    hand to the ledger, or None when there is nothing to report - a 404 or a
    static file. A human produces GATE_REPORT, which carries nothing about them. Keeping this separate from the handler is what lets the tests
    drive the real decision instead of a mock of it.
    """
    path = path.split("?", 1)[0]
    if path == "/robots.txt":
        # Ours, actually served. Disallow nothing: we are measuring what clients
        # do when they are NOT blocked.
        return 200, "text/plain", f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", None
    if path == "/sitemap.xml":
        return 200, "application/xml", maze.sitemap(base + "/"), None

    client = forwardable(headers)
    parts = [p for p in path.split("/") if p]

    if len(parts) == 2 and parts[0] == "m":
        slug = parts[1]
        if slug not in maze.slugs():
            return 404, "text/plain", "not found", None
        page_path = f"/m/{slug}"
        # A human gets the same page with no canary link, no secret and no report.
        # The gate is run AGAIN at the ledger, which is what actually protects the
        # privacy claim; this copy only avoids minting for a browser.
        if not is_automated(client):
            return 200, "text/html", maze.page(slug, page_path), GATE_REPORT
        ctx = derive(client, ip)
        secret = mint.secret_for(page_path, ctx, epoch=mint.salt_epoch())
        body = maze.page(slug, mint.canary_path(secret, slug))
        return 200, "text/html", body, {
            "kind": "mint", "method": "GET", "path": page_path, "ip": ip,
            "headers": client, "via": EDGE_NAME, "secret": secret, "size": len(body)}

    if len(parts) == 3 and parts[0] == "c":
        # Always 200, for every context, known secret or not. A 404 here for the
        # second context would end the observation before it starts.
        secret, slug = parts[1], parts[2]
        body = maze.full_text(slug if slug in maze.slugs() else maze.slugs()[0])
        if not is_automated(client):
            return 200, "text/html", body, GATE_REPORT
        return 200, "text/html", body, {
            "kind": "canary", "method": "GET", "path": f"/c/{secret}/{slug}",
            "ip": ip, "headers": client, "via": EDGE_NAME, "secret": secret,
            "size": len(body)}

    return 404, "text/plain", "not found", None


class handler(BaseHTTPRequestHandler):
    def _send(self, body: str, status: int = 200, ctype: str = "text/html") -> None:
        raw = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        # No caching: a cached canary page would hide the very fetch we record.
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:                       # noqa: N802
        headers = {k: v for k, v in self.headers.items()}
        lower = {k.lower(): v for k, v in headers.items()}
        ip = client_ip(lower)
        host = lower.get("x-forwarded-host") or lower.get("host") or ""
        base = f"https://{host}" if host else ""
        status, ctype, body, payload = respond(self.path, headers, ip, base)
        if payload is not None:
            report(payload)
        self._send(body, status=status, ctype=ctype)

    def log_message(self, *a) -> None:              # noqa: D102
        return                                       # Vercel captures stdout itself
