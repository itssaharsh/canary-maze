"""Routing only. All decisions live in gate, context, mint and detect."""
from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_from_directory

from . import detect, maze, mint
from .context import derive
from .gate import is_automated
from .ledger import Ledger

VIEWER = Path(__file__).resolve().parents[1] / "viewer"


def client_ip(req) -> str:
    """Behind a proxy the peer address is the proxy. Trust the left-most
    X-Forwarded-For hop only because the deploy terminates TLS at one we control;
    a public deployment behind an untrusted proxy would need an allowlist."""
    fwd = req.headers.get("X-Forwarded-For", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return req.remote_addr or "0.0.0.0"


def create_app(db_path: str | None = None, origin: str = "organic") -> Flask:
    """`origin` marks every row this instance writes. Production serves real
    traffic and leaves it "organic"; the seeded replay constructs the app with
    origin="seeded" so its rows are labelled at the moment they are written,
    rather than relabelled afterwards - the ledger is append-only, and a record
    you can retroactively relabel is not a record."""
    app = Flask(__name__)
    app.config["ORIGIN"] = origin
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
        ip = client_ip(request)
        automated = is_automated(headers)
        ctx = derive(headers, ip)
        epoch = mint.salt_epoch()
        path = f"/m/{slug}"

        if not automated:
            # A human. No secret, no ledger row, no record that they were here.
            # The page still renders identically, so this is not cloaking.
            return Response(maze.page(slug, f"/m/{slug}"), mimetype="text/html")

        secret = mint.secret_for(path, ctx, epoch=epoch)
        body = maze.page(slug, mint.canary_path(secret, slug))
        rid = ledger().record_request(method="GET", path=path, status=200, ip=ip,
                                      ua=headers.get("User-Agent", ""), ctx_id=ctx,
                                      origin=app.config["ORIGIN"], size=len(body))
        if ledger().mint_for_secret(secret) is None:
            ledger().record_mint(secret=secret, ctx_id=ctx, path=path,
                                 salt_epoch=epoch, request_id=rid)
        return Response(body, mimetype="text/html")

    # ---- the canary: ALWAYS 200, for every context ------------------------
    @app.get("/c/<secret>/<slug>")
    def canary(secret: str, slug: str):
        """A 404 here for the second context would end the observation before it
        starts, so this route returns 200 for anyone who asks, known secret or not."""
        headers = dict(request.headers)
        ip = client_ip(request)
        body = maze.full_text(slug if slug in maze.slugs() else maze.slugs()[0])

        if not is_automated(headers):
            return Response(body, mimetype="text/html")

        ctx = derive(headers, ip)
        rid = ledger().record_request(method="GET", path=f"/c/{secret}/{slug}",
                                      status=200, ip=ip,
                                      ua=headers.get("User-Agent", ""), ctx_id=ctx,
                                      origin=app.config["ORIGIN"], size=len(body))
        detect.on_canary_request(ledger(), secret=secret, seen_ctx_id=ctx,
                                 seen_request_id=rid, origin=app.config["ORIGIN"])
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
        if (VIEWER / asset).exists():
            return send_from_directory(VIEWER, asset)
        return Response("not found", status=404)

    return app


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


if __name__ == "__main__":  # pragma: no cover
    if not os.environ.get("CANARY_ALLOW_DEV_SALT"):
        require_production_salt()
    create_app().run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
