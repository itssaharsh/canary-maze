"""Routing only. All decisions live in gate, context, mint and detect."""
from __future__ import annotations

import hmac
import ipaddress
import os
import sqlite3
import threading
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_from_directory

from . import detect, maze, mint
from .context import derive
from .gate import is_automated
from .ingest import SIG_HEADER, TS_HEADER, SeenSignatures, ingest_key
from .ingest import verify as ingest_verify
from .paths import ledger_path
from .ledger import Ledger, truncate_ip

VIEWER = Path(__file__).resolve().parents[1] / "viewer"

#: The only files the surface will serve from viewer/. An allowlist rather than
#: an existence check, so nothing that lands in that directory becomes public.
ALLOWED_ASSETS = {"app.css", "render.js", "verify.js", "data.js", "data.json"}


#: Which proxy header, if any, may be believed. Set by CANARY_TRUST_PROXY.
#:   "none"       - default. Only the real peer address is used.
#:   "cloudflare" - trust CF-Connecting-IP, which Cloudflare's edge SETS (it does
#:                  not merely append), so a client cannot forge it through the
#:                  tunnel. This is what scripts/keep_alive.sh runs under.
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
    peer = req.remote_addr or "0.0.0.0"
    if trust == "cloudflare" and _is_loopback(peer):
        # Believed ONLY from cloudflared, which dials loopback. The header used to
        # be believed from any peer while the server listened on every interface,
        # so anyone who could reach the port chose the network recorded for them -
        # including the operator's, which made their traffic a "self-test".
        cf = (req.headers.get("CF-Connecting-IP") or "").strip()
        if cf:
            return cf
    return peer


def _is_loopback(addr: str) -> bool:
    try:
        return ipaddress.ip_address(addr).is_loopback
    except ValueError:
        return False


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


def operator_nets() -> tuple[str, ...]:
    """Networks whose traffic is the operator's own, from CANARY_OPERATOR_NETS.

    Given as truncated networks, exactly as the ledger stores them, comma
    separated: "103.81.39.0/24,2001:db8::/48".
    """
    raw = os.environ.get("CANARY_OPERATOR_NETS", "")
    return tuple(n.strip() for n in raw.split(",") if n.strip())


def request_origin(req, default: str, *, ip: str | None = None) -> str:
    """Resolve the origin of ONE request, rather than stamping the whole process.

    The operator constantly probes their own surface - smoke tests, uptime checks,
    a curl to see whether the tunnel is up. Before this existed, `origin` was a
    single process-wide config value, so every one of those was written to the
    ledger as 'organic' and published to a reader as third-party traffic. A
    verification curl is not evidence that anyone else fetched the secret.

    Two independent ways to be recognised, because one was not enough:

    1. **The operator's own network.** Checked first and needing nothing of the
       client, because the header is opt-in and opt-in controls get forgotten.
       They were forgotten three times here, the third time while diagnosing the
       second, which is how a counter that exists to be trusted acquired four
       sightings that were all the operator's own curl. Traffic from the
       operator's own network is not third-party evidence, whatever it sends.
    2. **A secret token**, for probing from somewhere else. It is a SECRET and
       absence fails closed: if the header alone sufficed, any fetcher could
       label itself a self-test and stay out of the organic count, letting the
       observed party opt out of being observed.

    This is deliberately asymmetric. Mislabelling our own traffic as organic
    manufactures evidence; mislabelling a stranger's as self-test only loses
    some. Only the first is a lie, so the doubt goes that way.
    """
    return request_origin_from(req.headers, default, ip=ip)


def request_origin_from(headers, default: str, *, ip: str | None = None) -> str:
    """The same decision over a plain headers mapping.

    Both the directly served routes and the signed edge hand-off go through this,
    so a request forwarded by an edge cannot end up classified by different rules
    than one this process saw itself.
    """
    nets = operator_nets()
    if nets and ip and truncate_ip(ip) in nets:
        return "selftest"

    token = os.environ.get("CANARY_SELFTEST_TOKEN", "").strip()
    if not token:
        return default
    lower = {str(k).lower(): str(v) for k, v in dict(headers).items()}
    sent = (lower.get(SELFTEST_HEADER.lower()) or "").strip()
    # Compared as BYTES. compare_digest raises TypeError on a non-ASCII str, and
    # the header went into it raw: one request header, with no knowledge of the
    # token, made the route 500 and the fetch vanish from the ledger - the opt-out
    # this function's docstring says cannot exist.
    if sent and hmac.compare_digest(sent.encode("utf-8", "replace"),
                                    token.encode("utf-8", "replace")):
        return "selftest"
    return default


def _owed_epoch(secret: str, path: str, ctx: str) -> str | None:
    """The epoch under which `secret` is the one this context is owed, or None.

    Yesterday counts too, because the edge computes the epoch at its own clock and
    a request minted a moment before midnight UTC is reported a moment after. The
    epoch that MATCHED is returned and stored on the mint row: recording the
    ledger's own `salt_epoch()` instead wrote a row whose stored epoch did not
    verify its own secret, which is exactly what the epoch column exists to prevent.
    """
    if not secret.isascii():
        return None
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    for when in (now, now - timedelta(days=1)):
        epoch = mint.salt_epoch(when)
        if hmac.compare_digest(mint.secret_for(path, ctx, epoch=epoch), secret):
            return epoch
    return None


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
    # Nothing this service receives is large. An unauthenticated 40 MB POST to
    # /ingest used to be read and parsed in full before the signature was checked.
    app.config["MAX_CONTENT_LENGTH"] = 256 * 1024
    seen_signatures = SeenSignatures()
    app.config["ORIGIN"] = origin
    trust = os.environ.get("CANARY_TRUST_PROXY", "none").strip().lower()
    if trust not in TRUST_MODES:
        raise SystemExit(f"CANARY_TRUST_PROXY must be one of {TRUST_MODES}, got {trust!r}")
    app.config["TRUST_PROXY"] = trust
    # A retired ledger must never be served again; paths.ledger_path refuses one.
    app.config["LEDGER_PATH"] = db_path or ledger_path()

    app.extensions = getattr(app, "extensions", {}) or {}
    ledger_lock = threading.Lock()

    def ledger() -> Ledger:
        """Exactly one Ledger per app, however many requests arrive at once.

        This was an unsynchronised check-then-set, so sixteen simultaneous first
        requests built sixteen connections - each with its own lock, so the lock
        that makes sharing safe serialised nothing - and in most runs the shared
        connection ended wedged while every response stayed 200.
        """
        led = app.extensions.get("ledger")
        if led is None:
            with ledger_lock:
                led = app.extensions.get("ledger")
                if led is None:
                    led = app.extensions["ledger"] = Ledger(app.config["LEDGER_PATH"])
        return led

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
            try:
                ledger().note_gate_rejection()
            except sqlite3.Error:
                app.logger.warning("ledger unavailable; gate counter not moved", exc_info=True)
            return Response(maze.page(slug, f"/m/{slug}"), mimetype="text/html")

        secret = mint.secret_for(path, ctx, epoch=epoch)
        body = maze.page(slug, mint.canary_path(secret, slug))
        req_origin = request_origin(request, app.config["ORIGIN"], ip=ip)
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
            try:
                ledger().note_gate_rejection()
            except sqlite3.Error:
                app.logger.warning("ledger unavailable; gate counter not moved", exc_info=True)
            return Response(body, mimetype="text/html")

        ctx = derive(headers, ip)
        req_origin = request_origin(request, app.config["ORIGIN"], ip=ip)
        try:
            # Answered 200 like everything else, and NOT recorded: the ledger cannot
            # delete, so a row per guess would be a permanent, attacker-sized ledger.
            # Inside the try, because an unopenable ledger must not break the one
            # contract this route has - a 500 for the second context ends the
            # observation just as surely as a 404 would.
            if ledger().mint_for_secret(secret) is None:
                return Response(body, mimetype="text/html")
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

    # ---- signed hand-off from a public edge --------------------------------
    @app.post("/ingest")
    def ingest():
        """Record a request a public edge observed on our behalf.

        This exists because the host that can reach the clients we want to observe
        is not the host that holds the ledger (F-0005, ADR-0006). It is the only
        write path in the product that is not driven by a real connection, so it
        is the one most worth attacking: an unauthenticated version would let
        anyone post invented rows into an append-only ledger, where they could
        never be removed. Hence a shared key, a timestamp, and `via` on every row
        so a reader can tell a reported request from an observed one.
        """
        key = ingest_key()
        if not key:
            return jsonify({"ok": False, "error": "ingest disabled"}), 404

        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return jsonify({"ok": False, "error": "body must be a JSON object"}), 400

        ok, why = ingest_verify(body, request.headers.get(TS_HEADER, ""),
                                request.headers.get(SIG_HEADER, ""), key)
        if not ok:
            app.logger.warning("ingest refused: %s", why)
            return jsonify({"ok": False, "error": why}), 403
        if not seen_signatures.first_time(request.headers.get(SIG_HEADER, "")):
            app.logger.warning("ingest refused: this signed report was already delivered")
            return jsonify({"ok": False, "error": "already delivered"}), 409

        if body.get("kind") == "gate":
            # The edge turned a browser away and says so. It sends nothing about
            # the visitor and nothing is stored: one counter goes up by one.
            ledger().note_gate_rejection()
            return jsonify({"ok": True, "recorded": False, "reason": "human"}), 200

        edge = str(body.get("via") or "edge")[:32]
        headers = {str(k): str(v) for k, v in (body.get("headers") or {}).items()}
        ip = str(body.get("ip") or "0.0.0.0")
        path = str(body.get("path") or "/")
        ua = headers.get("User-Agent") or headers.get("user-agent") or ""

        # The gate runs HERE, on the forwarded headers, not at the edge. The edge
        # reports what it saw; this process decides what it means. Moving the
        # human-exclusion decision outward would put the privacy guarantee on a
        # machine we do not control.
        if not is_automated(headers):
            ledger().note_gate_rejection()
            return jsonify({"ok": True, "recorded": False, "reason": "human"}), 200

        ctx = derive(headers, ip)
        kind = body.get("kind")
        secret = str(body.get("secret") or "")

        # Everything is checked BEFORE a row is written, because a row is for ever.
        if body.get("ctx") and body["ctx"] != ctx:
            # The edge minted for one context and this process derives another from
            # the same request. A row written now would bind the secret to a
            # context no later request could ever match. Refuse, loudly.
            app.logger.error("ingest refused: edge derived context %s, ledger derives %s",
                             body["ctx"], ctx)
            return jsonify({"ok": False, "error": "context mismatch"}), 409
        owed_epoch = None
        if kind == "mint":
            # The ledger holds the salt, so it does not take the edge's word for the
            # secret: it must be the one this context is owed for this path.
            owed_epoch = _owed_epoch(secret, path, ctx)
            if owed_epoch is None:
                app.logger.error("ingest refused: reported secret does not verify for "
                                 "the reported path and context")
                return jsonify({"ok": False, "error": "secret does not verify"}), 409
        elif kind == "canary":
            if ledger().mint_for_secret(secret) is None:
                # never issued: answered at the edge, and not stored here
                return jsonify({"ok": True, "recorded": False, "reason": "unknown secret"}), 200
        else:
            return jsonify({"ok": False, "error": "unknown kind"}), 400

        req_origin = request_origin_from(headers, app.config["ORIGIN"], ip=ip)
        method = "HEAD" if str(body.get("method") or "GET").upper() == "HEAD" else "GET"
        try:
            rid = ledger().record_request(
                method=method, path=path, status=200, ip=ip, ua=ua, ctx_id=ctx,
                origin=req_origin, size=int(body.get("size") or 0), via=edge)
            if kind == "mint":
                if ledger().mint_for_secret(secret) is None:
                    try:
                        ledger().record_mint(secret=secret, ctx_id=ctx, path=path,
                                             salt_epoch=owed_epoch, request_id=rid)
                    except sqlite3.IntegrityError:
                        pass
            else:
                detect.on_canary_request(ledger(), secret=secret, seen_ctx_id=ctx,
                                         seen_request_id=rid, origin=req_origin)
        except sqlite3.Error:
            app.logger.error("LEDGER FAILURE on ingest", exc_info=True)
            return jsonify({"ok": False, "error": "ledger unavailable"}), 503
        return jsonify({"ok": True, "recorded": True, "ctx": ctx}), 200

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
    # Loopback by default: the tunnel dials 127.0.0.1 and nothing else needs the port.
    create_app().run(host=os.environ.get("CANARY_BIND", "127.0.0.1"),
                     port=int(os.environ.get("PORT", 8000)))
