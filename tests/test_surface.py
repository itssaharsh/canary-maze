"""The Vercel function: the code every third-party client actually talks to.

It shipped with no tests at all. Its imported modules were covered, but the
function that wires them together - and that decides what leaves the edge - was
not, which is how a false sighting reached the live ledger (F-0006): the function
handed every header it saw, the platform's own included, to a fingerprint that
hashed all of them.

These tests drive `respond()`, the real decision function, with no socket and no
network, and then replay its reports into a real ledger through the real signed
/ingest route, so the edge and the ledger are tested as the pair they are.
"""
from __future__ import annotations

import filecmp
import importlib.util
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "site" / "api"

BOT = {"User-Agent": "Mozilla/5.0 (compatible; GPTBot/1.2; +https://openai.com/gptbot)",
       "Accept": "*/*", "Accept-Encoding": "gzip, br"}
BROWSER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129.0",
           "Accept": "text/html", "Accept-Language": "en-GB,en;q=0.9",
           "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "none"}
# What a hosting platform adds, and it is NOT the same set on every route.
ON_MAZE = {"x-vercel-id": "bom1::aaaa", "x-forwarded-for": "198.51.100.7",
           "x-matched-path": "/api/surface", "x-now-route-matches": "1=q3-supplier-review"}
ON_CANARY = {"x-vercel-proxy-signature": "Bearer zz", "x-vercel-id": "bom1::bbbb",
             "x-forwarded-for": "198.51.100.7", "x-vercel-sc-host": "h",
             "x-now-route-matches": "1=abc&2=q3-supplier-review", "cdn-loop": "edge"}
KEY = "k" * 48
IP = "198.51.100.7"


@pytest.fixture(scope="module")
def surface():
    """Import site/api/surface.py the way Vercel does: with site/api on the path."""
    sys.path.insert(0, str(API))
    try:
        spec = importlib.util.spec_from_file_location("canary_surface", API / "surface.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        yield mod
    finally:
        sys.path.remove(str(API))


@pytest.fixture
def ledger_app(tmp_path, monkeypatch):
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    monkeypatch.setenv("CANARY_INGEST_KEY", KEY)
    monkeypatch.delenv("CANARY_OPERATOR_NETS", raising=False)
    monkeypatch.delenv("CANARY_SELFTEST_TOKEN", raising=False)
    from canarymaze.app import create_app
    db = str(tmp_path / "t.sqlite3")
    return create_app(db_path=db).test_client(), db


def deliver(client, payload):
    """Hand a report to the ledger exactly as the function does: signed."""
    from canarymaze.ingest import SIG_HEADER, TS_HEADER, sign
    ts = str(time.time())
    return client.post("/ingest", json=payload,
                       headers={TS_HEADER: ts, SIG_HEADER: sign(payload, ts, KEY)})


def canary_link(body: str) -> str:
    i = body.index("/c/")
    return body[i:body.index('"', i)]


# --- the copies the function imports ----------------------------------------

def test_the_deployed_module_copies_match_their_source():
    """site/api/_cm/ holds COPIES of canarymaze modules, made by build_site.py.
    A fix to canarymaze/context.py that is not rebuilt into the copy leaves the
    public surface running the old code while every test passes. This is the
    drift gate for that."""
    copies = sorted(p.name for p in (API / "_cm").glob("*.py") if p.name != "__init__.py")
    assert copies, "site/api/_cm is empty - run python3 scripts/build_site.py"
    stale = [n for n in copies
             if not filecmp.cmp(API / "_cm" / n, ROOT / "canarymaze" / n, shallow=False)]
    assert not stale, f"stale copies in site/api/_cm (run scripts/build_site.py): {stale}"


# --- what leaves the edge ----------------------------------------------------

def test_only_client_headers_are_forwarded(surface, monkeypatch):
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    noisy = {**BOT, **ON_MAZE, "Cookie": "session=secret", "Authorization": "Bearer x",
             "X-Trace": "1"}
    _, _, _, payload = surface.respond("/m/q3-supplier-review", noisy, IP, "https://h")
    sent = payload["headers"]
    assert set(sent) == {"user-agent", "accept", "accept-encoding"}
    assert "cookie" not in sent and "authorization" not in sent
    assert not any(k.startswith("x-") for k in sent)


def test_a_human_is_served_and_nothing_is_reported(surface, monkeypatch):
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    status, _, body, payload = surface.respond("/m/q3-supplier-review", BROWSER, IP, "https://h")
    assert status == 200 and payload is None
    assert "/c/" not in body, "a human must not be issued a canary link"
    status, _, _, payload = surface.respond("/c/deadbeefdeadbeef/q3-supplier-review",
                                            BROWSER, IP, "https://h")
    assert status == 200 and payload is None


def test_the_canary_route_is_200_for_an_unknown_secret_and_an_unknown_slug(surface, monkeypatch):
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    status, _, body, _ = surface.respond("/c/not-a-real-secret/no-such-slug", BOT, IP, "https://h")
    assert status == 200 and body


def test_unknown_paths_and_slugs_are_404_and_unreported(surface, monkeypatch):
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    for path in ("/m/no-such-slug", "/", "/.env", "/m/a/b/c", "/c/only-two"):
        status, _, _, payload = surface.respond(path, BOT, IP, "https://h")
        assert status == 404 and payload is None, path


def test_robots_and_sitemap_are_ours(surface):
    status, ctype, body, payload = surface.respond("/robots.txt", {}, IP, "https://h.example")
    assert (status, ctype, payload) == (200, "text/plain", None)
    assert "Allow: /" in body and "https://h.example/sitemap.xml" in body
    status, _, body, _ = surface.respond("/sitemap.xml", {}, IP, "https://h.example")
    assert status == 200 and "https://h.example/m/q3-supplier-review" in body


# --- the edge and the ledger, together --------------------------------------

def test_a_client_following_its_own_link_is_not_a_sighting(surface, ledger_app, monkeypatch):
    """THE regression test for F-0006, end to end through both halves.

    Same client, same headers, same address - but the platform injects a different
    set of its own headers on the two routes, exactly as it did live."""
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    client, db = ledger_app
    from canarymaze.ledger import Ledger

    _, _, body, mint_report = surface.respond(
        "/m/q3-supplier-review", {**ON_MAZE, **BOT}, IP, "https://h")
    assert deliver(client, mint_report).get_json()["recorded"] is True

    _, _, _, canary_report = surface.respond(
        canary_link(body), {**BOT, **ON_CANARY}, IP, "https://h")
    assert deliver(client, canary_report).get_json()["recorded"] is True

    led = Ledger(db)
    c = led.counts()
    led.close()
    assert c["mints"] == 1 and c["requests"] == 2
    assert c["sightings_organic"] == 0 and c["sightings_selftest"] == 0, \
        "one client re-reading its own link proves nothing and must record nothing"


def test_a_different_client_fetching_that_link_is_a_sighting(surface, ledger_app, monkeypatch):
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    client, db = ledger_app
    from canarymaze.ledger import Ledger

    _, _, body, mint_report = surface.respond("/m/q3-supplier-review", {**ON_MAZE, **BOT}, IP, "https://h")
    deliver(client, mint_report)
    other = {"User-Agent": "Mozilla/5.0 (compatible; ClaudeBot/1.0)", "Accept": "*/*"}
    _, _, _, canary_report = surface.respond(canary_link(body), {**other, **ON_CANARY},
                                             "192.0.2.50", "https://h")
    deliver(client, canary_report)

    led = Ledger(db)
    c = led.counts()
    row = led.rows("request")[-1]
    led.close()
    assert c["sightings_organic"] == 1
    assert row["via"] == "vercel" and row["ip_net"] == "192.0.2.0/24"


def test_the_edge_and_the_ledger_derive_the_same_context(surface, ledger_app, monkeypatch):
    """The function mints for the context IT derives; the ledger records the one
    IT derives from the forwarded headers. If the two ever disagree, every mint is
    bound to a context that no later request can match."""
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    client, _ = ledger_app
    from canarymaze import mint
    from canarymaze.context import derive

    headers = {**ON_MAZE, **BOT, "Cookie": "a=b"}
    _, _, _, report = surface.respond("/m/q3-supplier-review", headers, IP, "https://h")
    ledger_ctx = deliver(client, report).get_json()["ctx"]
    assert ledger_ctx == derive(headers, IP) == derive(report["headers"], IP)
    assert report["secret"] == mint.secret_for("/m/q3-supplier-review", ledger_ctx,
                                               epoch=mint.salt_epoch())
