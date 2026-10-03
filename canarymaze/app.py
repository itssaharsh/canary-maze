"""Routing only. All decisions live in gate, context, mint and detect."""
from __future__ import annotations

import hmac
import os
import sqlite3
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_from_directory

from . import detect, maze, mint
from .context import derive
from .gate import is_automated
from .ledger import Ledger

VIEWER = Path(__file__).resolve().parents[1] / "viewer"

#: The only files the surface will serve from viewer/. An allowlist rather than
#: an existence check, so nothing that lands in that directory becomes public.
ALLOWED_ASSETS = {"app.css", "render.js", "verify.js", "data.js", "data.json"}


#: Which proxy header, if any, may be believed. Set by CANARY_TRUST_PROXY.
#:   "none"       - default. Only the real peer address is used.
#:   "cloudflare" - trust CF-Connecting-IP, which Cloudflare's edge SETS (it does
#:                  not merely append), so a client cannot forge it through the
#:                  tunnel. This is what scripts/serve_public.sh runs under.
TRUST_MODES = ("none", "cloudflare")


def client_ip(req, trust: str = "none") -> str:
    """Return the address to attribute this request to.

    X-Forwarded-For is NEVER trusted, in any mode. The earlier version took its
    left-most hop and a review showed the consequence: one peer sending two
    different XFF values produced a complete sighting with BOTH networks fabricated
    and the real peer absent from the record. Cloudflare *appends* to XFF, so under
    the shipped tunnel deploy the left-most entry is entirely attacker-controlled -
    the comment claiming the deploy made it safe had the direction backwards.
    """
    if trust == "cloudflare":
        cf = (req.headers.get("CF-Connecting-IP") or "").strip()
        if cf:
            return cf
    return req.remote_addr or "0.0.0.0"


def require_production_salt() -> None:
    """Refuse to serve publicly on the committed development salt.

    `mint.load_salt()` falls back to a fixed development salt so tests and
    `make demo` run on a clean checkout with no setup. That fallback is in a
    PUBLIC repository. Serving with it would mean anyone who read the repo could
    forge a secret, which destroys the one thing the HMAC genuinely bounds - token
    provenance - and with it every claim this project makes. The library stays
    permissive so the offline demo works; the server is strict.
    """
    if os.environ.get("CANARY_SALT"):
        return
    raise SystemExit(
        "refusing to start: CANARY_SALT is not set, so minting would use the "
        "development salt that is committed in this repository, and any reader "
        "could forge a secret.\n"
        "  generate one:  python3 -c \"import secrets; print(secrets.token_hex(32))\"\n"
        "  then:          export CANARY_SALT=<that value>\n"
        "Set CANARY_ALLOW_DEV_SALT=1 only for local, non-public runs.")



SELFTEST_HEADER = "X-Canary-Selftest"


def request_origin(req, default: str) -> str:
    """Resolve the origin of ONE request, rather than stamping the whole process.

    The operator needs to probe their own surface - a smoke test, an uptime check,
    `scripts/verify.sh`. Before this existed, `origin` was a single process-wide
    config value, so every one of those probes was written to the ledger as
    'organic' and published to a reader as third-party traffic. A verification
    curl is not evidence that anyone else fetched the secret, and counting it as
    such is exactly the overclaim this product exists to refuse.

    The token is a SECRET, and absence fails closed to `default`. If the header
    alone were enough, any fetcher could label itself a self-test and stay out of
    the organic count - letting the observed party opt out of being observed.
    """
    token = os.environ.get("CANARY_SELFTEST_TOKEN", "").strip()
    if not token:
        return default
    sent = (req.headers.get(SELFTEST_HEADER) or "").strip()
    if sent and hmac.compare_digest(sent, token):
        return "selftest"
    return default


def create_app(db_path: str | None = None, origin: str = "organic") -> Flask:
    """`origin` marks every row this instance writes. Production serves real
    traffic and leaves it "organic"; the seeded replay constructs the app with
    origin="seeded" so its rows are labelled at the moment they are written,
    rather than relabelled afterwards - the ledger is append-only, and a record
    you can retroactively relabel is not a record."""
    if not os.environ.get("CANARY_ALLOW_DEV_SALT") and db_path is None:
        # Guarding only __main__ meant any WSGI entry point skipped this entirely.
        # db_path is None exactly when the app is being constructed for real use;
        # tests and the demo pass an explicit path.
        require_production_salt()
    app = Flask(__name__)
    app.config["ORIGIN"] = origin
    trust = os.environ.get("CANARY_TRUST_PROXY", "none").strip().lower()
    if trust not in TRUST_MODES:
        raise SystemExit(f"CANARY_TRUST_PROXY must be one of {TRUST_MODES}, got {trust!r}")
    app.config["TRUST_PROXY"] = trust
    app.config["LEDGER_PATH"] = db_path or os.environ.get("CANARY_DB", "canary.sqlite3")

    def ledger() -> Ledger:
        if "ledger" not in app.extensions:
            app.extensions["ledger"] = Ledger(app.config["LEDGER_PATH"])
        return app.extensions["ledger"]

    app.extensions = getattr(app, "extensions", {}) or {}

    # ---- the maze: where a secret is issued -------------------------------
    @app.get("/m/<slug>")
    def maze_page(slug: str):
        if slug not in maze.slugs():
            return Response("not found", status=404)
        headers = dict(request.headers)
        ip = client_ip(request, app.config["TRUST_PROXY"])
        automated = is_automated(headers)
        ctx = derive(headers, ip)
        epoch = mint.salt_epoch()
        path = f"/m/{slug}"

        if not automated:
            # A human. No secret, no ledger row, no record that they were here -
            # only a bare counter, so the exclusion is falsifiable without storing
            # anything about them. The page renders identically, so this is not
            # cloaking.
            ledger().note_gate_rejection()
            return Response(maze.page(slug, f"/m/{slug}"), mimetype="text/html")

        secret = mint.secret_for(path, ctx, epoch=epoch)
        body = maze.page(slug, mint.canary_path(secret, slug))
        req_origin = request_origin(request, app.config["ORIGIN"])
        # ARCHITECTURE.md and the contract promise: on a ledger failure, serve the
        # page anyway and never block a crawler. That promise had no implementation
        # until a review looked for it. A blocked crawler is a lost sighting, which
        # is strictly worse than a missing row.
        try:
            rid = ledger().record_request(method="GET", path=path, status=200, ip=ip,
                                          ua=headers.get("User-Agent", ""), ctx_id=ctx,
                                          origin=req_origin, size=len(body))
            if ledger().mint_for_secret(secret) is None:
                try:
                    ledger().record_mint(secret=secret, ctx_id=ctx, path=path,
                                         salt_epoch=epoch, request_id=rid)
                except sqlite3.IntegrityError:
                    pass          # a concurrent request minted it first; fine
        except sqlite3.Error:
            app.logger.warning("ledger unavailable; served without minting", exc_info=True)
        return Response(body, mimetype="text/html")

    # ---- the canary: ALWAYS 200, for every context ------------------------
    @app.get("/c/<secret>/<slug>")
    def canary(secret: str, slug: str):
        """A 404 here for the second context would end the observation before it
        starts, so this route returns 200 for anyone who asks, known secret or not."""
        headers = dict(request.headers)
        ip = client_ip(request, app.config["TRUST_PROXY"])
        body = maze.full_text(slug if slug in maze.slugs() else maze.slugs()[0])

        if not is_automated(headers):
            ledger().note_gate_rejection()
            return Response(body, mimetype="text/html")

        ctx = derive(headers, ip)
        req_origin = request_origin(request, app.config["ORIGIN"])
        try:
            rid = ledger().record_request(method="GET", path=f"/c/{secret}/{slug}",
                                          status=200, ip=ip,
                                          ua=headers.get("User-Agent", ""), ctx_id=ctx,
                                          origin=req_origin, size=len(body))
            detect.on_canary_request(ledger(), secret=secret, seen_ctx_id=ctx,
                                     seen_request_id=rid, origin=req_origin)
        except sqlite3.Error:
            # Losing a sighting here is the worst failure in the product, so it is
            # logged loudly rather than swallowed silently.
            app.logger.error("LEDGER FAILURE on the canary route; a sighting may "
                             "have been lost", exc_info=True)
        return Response(body, mimetype="text/html")

    # ---- what the viewer reads -------------------------------------------
    @app.get("/export.json")
    def export_json():
        from .export import export
        return jsonify(export(ledger()))

    @app.get("/sitemap.xml")
    def sitemap():
        base = request.url_root
        return Response(maze.sitemap(base), mimetype="application/xml")

    @app.get("/robots.txt")
    def robots():
        # Nothing is disallowed. A Disallow here would make the whole instrument
        # dishonest: we are measuring what clients do when they are not blocked.
        return Response(f"User-agent: *\nAllow: /\nSitemap: {request.url_root}sitemap.xml\n",
                        mimetype="text/plain")

    @app.get("/")
    def viewer_index():
        if (VIEWER / "index.html").exists():
            return send_from_directory(VIEWER, "index.html")
        return Response("viewer not built; run `make demo`", mimetype="text/plain")

    @app.get("/<path:asset>")
    def viewer_asset(asset: str):
        # Only the viewer's own files, and never a dotfile: a review found
        # GET /.vercel/project.json returning 200 on the live canary surface,
        # handing out the Vercel project and org ids.
        if any(part.startswith(".") for part in asset.split("/")):
            return Response("not found", status=404)
        if asset not in ALLOWED_ASSETS:
            return Response("not found", status=404)
        if (VIEWER / asset).exists():
            return send_from_directory(VIEWER, asset)
        return Response("not found", status=404)

    return app


if __name__ == "__main__":  # pragma: no cover
    if not os.environ.get("CANARY_ALLOW_DEV_SALT"):
        require_production_salt()
    create_app().run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
