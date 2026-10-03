"""End-to-end through the real routes: mint, then a sighting by a second context."""
import pytest

from canarymaze.app import create_app
from canarymaze.ledger import Ledger

CRAWLER = {"User-Agent": "Mozilla/5.0 (compatible; GPTBot/1.2; +https://openai.com/gptbot)",
           "Accept": "text/html", "Accept-Encoding": "gzip"}
OTHER = {"User-Agent": "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
         "Accept": "text/html", "Accept-Encoding": "gzip"}
HUMAN = dict(OTHER, **{"Accept-Language": "en-GB,en;q=0.9", "Sec-Fetch-Mode": "navigate"})


@pytest.fixture()
def client(tmp_path):
    app = create_app(db_path=str(tmp_path / "t.sqlite3"))
    app.config["TESTING"] = True
    with app.test_client() as c:
        c.db = str(tmp_path / "t.sqlite3")
        yield c


def canary_url_from(html: str) -> str:
    import re
    m = re.search(r'href="(/c/[^"]+)"', html)
    assert m, "the maze page must carry exactly one canary link"
    return m.group(1)


def test_a_crawler_is_minted_for_and_a_second_context_produces_a_sighting(client):
    r = client.get("/m/q3-supplier-review", headers=CRAWLER,
                   environ_overrides={"REMOTE_ADDR": "20.171.207.14"})
    assert r.status_code == 200
    url = canary_url_from(r.get_data(as_text=True))

    r2 = client.get(url, headers=OTHER, environ_overrides={"REMOTE_ADDR": "104.28.52.9"})
    assert r2.status_code == 200

    led = Ledger(client.db)
    assert led.counts()["mints"] == 1
    assert led.counts()["sightings_organic"] == 1
    s = led.rows("sighting")[0]
    assert s["mint_ctx_id"] != s["seen_ctx_id"]
    led.close()


def test_the_minting_context_refetching_is_not_a_sighting(client):
    r = client.get("/m/q3-supplier-review", headers=CRAWLER,
                   environ_overrides={"REMOTE_ADDR": "20.171.207.14"})
    url = canary_url_from(r.get_data(as_text=True))
    client.get(url, headers=CRAWLER, environ_overrides={"REMOTE_ADDR": "20.171.207.14"})
    led = Ledger(client.db)
    assert led.counts()["sightings_organic"] == 0
    led.close()


def test_an_unknown_secret_still_returns_200_and_writes_no_sighting(client):
    r = client.get("/c/deadbeefdeadbeef/q3-supplier-review", headers=OTHER,
                   environ_overrides={"REMOTE_ADDR": "9.9.9.9"})
    assert r.status_code == 200, "a 404 would tell the client the URL was a trap"
    led = Ledger(client.db)
    assert led.counts()["sightings_organic"] == 0
    led.close()


def test_a_human_is_never_minted_for_and_never_enters_the_ledger(client):
    r = client.get("/m/q3-supplier-review", headers=HUMAN,
                   environ_overrides={"REMOTE_ADDR": "81.2.3.4"})
    assert r.status_code == 200
    led = Ledger(client.db)
    c = led.counts()
    assert c["requests"] == 0 and c["mints"] == 0 and c["human_requests"] == 0
    led.close()


def test_a_human_fetching_a_canary_is_also_not_recorded(client):
    r = client.get("/m/q3-supplier-review", headers=CRAWLER,
                   environ_overrides={"REMOTE_ADDR": "20.171.207.14"})
    url = canary_url_from(r.get_data(as_text=True))
    before = Ledger(client.db).counts()["requests"]
    client.get(url, headers=HUMAN, environ_overrides={"REMOTE_ADDR": "81.2.3.4"})
    assert Ledger(client.db).counts()["requests"] == before


def test_robots_disallows_nothing_and_advertises_the_sitemap(client):
    body = client.get("/robots.txt").get_data(as_text=True)
    assert "Disallow:" not in body
    assert "Sitemap:" in body


def test_sitemap_lists_every_maze_page(client):
    from canarymaze import maze
    body = client.get("/sitemap.xml").get_data(as_text=True)
    for slug in maze.slugs():
        assert f"/m/{slug}" in body


def test_the_server_refuses_to_start_on_the_committed_development_salt(monkeypatch):
    """The dev salt is public. Serving on it would make every secret forgeable."""
    import pytest as _pytest

    from canarymaze.app import require_production_salt

    monkeypatch.delenv("CANARY_SALT", raising=False)
    with _pytest.raises(SystemExit) as e:
        require_production_salt()
    assert "CANARY_SALT is not set" in str(e.value)
    assert "forge a secret" in str(e.value)

    monkeypatch.setenv("CANARY_SALT", "a" * 64)
    require_production_salt()        # now it is allowed to serve


def test_x_forwarded_for_is_never_trusted(client):
    """One peer sending two different XFF values used to produce a complete
    sighting with BOTH networks fabricated and the real peer absent."""
    r = client.get("/m/q3-supplier-review", headers=dict(CRAWLER, **{"X-Forwarded-For": "20.171.207.14"}),
                   environ_overrides={"REMOTE_ADDR": "198.51.100.77"})
    url = canary_url_from(r.get_data(as_text=True))
    client.get(url, headers=dict(CRAWLER, **{"X-Forwarded-For": "104.28.52.9"}),
               environ_overrides={"REMOTE_ADDR": "198.51.100.77"})
    led = Ledger(client.db)
    assert led.counts()["sightings_organic"] == 0, "a forged XFF must not make a sighting"
    for row in led.rows("request"):
        assert row["ip_net"] == "198.51.100.0/24", "the real peer must be what is stored"
    led.close()


def test_dotfiles_and_stray_files_in_the_viewer_are_never_served(tmp_path, monkeypatch):
    """Against files that EXIST. The old version asked for paths that are not in
    viewer/ at all, so they 404'd whether the guards were there or not: deleting
    both the dotfile check and the allowlist left it green while the mutant served
    viewer/.gitignore, and anything else dropped in that directory, over a
    publicly tunnelled surface.

    GET /.vercel/project.json really did return 200 on the live surface once."""
    import canarymaze.app as appmod
    viewer = tmp_path / "viewer"
    viewer.mkdir()
    (viewer / ".gitignore").write_text("data.js\n", encoding="utf-8")
    (viewer / ".env").write_text("CANARY_SALT=secret\n", encoding="utf-8")
    (viewer / "notes.txt").write_text("an export nobody meant to publish\n", encoding="utf-8")
    (viewer / "data.js").write_text("window.CANARY_DATA={};\n", encoding="utf-8")
    monkeypatch.setattr(appmod, "VIEWER", viewer)
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    c = appmod.create_app(db_path=str(tmp_path / "t.sqlite3")).test_client()

    for path in ("/.gitignore", "/.env", "/notes.txt", "/.vercel/project.json",
                 "/../canarymaze/schema.sql"):
        assert c.get(path).status_code == 404, f"{path} was served"
    assert c.get("/data.js").status_code == 200, "an allowlisted asset must still be served"


def test_an_unknown_trust_mode_refuses_to_start(monkeypatch):
    import pytest as _pytest
    from canarymaze.app import create_app as _create
    monkeypatch.setenv("CANARY_TRUST_PROXY", "please-trust-everything")
    with _pytest.raises(SystemExit):
        _create(db_path=":memory:")
