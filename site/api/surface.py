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
from _cm.context import derive                  # noqa: E402
from _cm.gate import is_automated               # noqa: E402
from _cm.ingest import SIG_HEADER, TS_HEADER, sign  # noqa: E402

EDGE_NAME = "vercel"
INGEST_TIMEOUT_S = 3.0


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
        path = self.path.split("?", 1)[0]
        headers = {k: v for k, v in self.headers.items()}
        ip = client_ip({k.lower(): v for k, v in headers.items()})
        host = headers.get("x-forwarded-host") or headers.get("Host") or ""
        base = f"https://{host}" if host else ""

        if path == "/robots.txt":
            # Ours, actually served. Disallow nothing: we are measuring what
            # clients do when they are NOT blocked.
            return self._send(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n",
                              ctype="text/plain")
        if path == "/sitemap.xml":
            return self._send(maze.sitemap(base + "/"), ctype="application/xml")

        parts = [p for p in path.split("/") if p]

        if len(parts) == 2 and parts[0] == "m":
            return self._maze(parts[1], headers, ip)
        if len(parts) == 3 and parts[0] == "c":
            return self._canary(parts[1], parts[2], headers, ip)
        return self._send("not found", status=404, ctype="text/plain")

    def _maze(self, slug: str, headers: dict, ip: str) -> None:
        if slug not in maze.slugs():
            return self._send("not found", status=404, ctype="text/plain")
        path = f"/m/{slug}"

        # A human gets the same page with no canary link, no secret and no report.
        # The gate decision is made again at the ledger, which is what actually
        # protects the privacy claim; this copy only avoids minting for a browser.
        if not is_automated(headers):
            return self._send(maze.page(slug, path))

        ctx = derive(headers, ip)
        secret = mint.secret_for(path, ctx, epoch=mint.salt_epoch())
        body = maze.page(slug, mint.canary_path(secret, slug))
        report({"kind": "mint", "method": "GET", "path": path, "ip": ip,
                "headers": headers, "via": EDGE_NAME, "secret": secret,
                "size": len(body)})
        return self._send(body)

    def _canary(self, secret: str, slug: str, headers: dict, ip: str) -> None:
        """Always 200, for every context, known secret or not. A 404 here for the
        second context would end the observation before it starts."""
        body = maze.full_text(slug if slug in maze.slugs() else maze.slugs()[0])
        if not is_automated(headers):
            return self._send(body)
        report({"kind": "canary", "method": "GET",
                "path": f"/c/{secret}/{slug}", "ip": ip, "headers": headers,
                "via": EDGE_NAME, "secret": secret, "size": len(body)})
        return self._send(body)

    def log_message(self, *a) -> None:              # noqa: D102
        return                                       # Vercel captures stdout itself
