"""The ledger under concurrency, under REPLACE, and when it cannot be opened.

Every case here was demonstrated by an independent correctness review. The worst
was silent: sixteen simultaneous first requests built sixteen separate SQLite
connections, so the lock that makes sharing safe serialised nothing, and in most
runs the shared connection ended wedged in a dead transaction - the surface kept
answering 200 while the ledger recorded nothing.
"""
from __future__ import annotations

import sqlite3
import subprocess
import sys
import threading
from pathlib import Path

import pytest

from canarymaze import bundle
from canarymaze.app import create_app
from canarymaze.ledger import Ledger
from canarymaze.paths import is_retired, ledger_path

ROOT = Path(__file__).resolve().parents[1]
BOT = {"User-Agent": "Mozilla/5.0 (compatible; GPTBot/1.2)"}


# --- one connection, whatever arrives ----------------------------------------

def test_simultaneous_first_requests_build_one_ledger(tmp_path, monkeypatch):
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    built = []
    import canarymaze.app as appmod
    real = appmod.Ledger

    class Counting(real):
        def __init__(self, *a, **k):
            built.append(1)
            super().__init__(*a, **k)

    monkeypatch.setattr(appmod, "Ledger", Counting)
    app = create_app(db_path=str(tmp_path / "t.sqlite3"))
    client = app.test_client()
    start = threading.Barrier(16)

    def hit(i):
        start.wait()
        client.get("/m/q3-supplier-review", headers={"User-Agent": f"Bot-{i}/1.0"},
                   environ_overrides={"REMOTE_ADDR": f"198.51.100.{i + 1}"})

    ts = [threading.Thread(target=hit, args=(i,)) for i in range(16)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    assert sum(built) == 1, f"{sum(built)} connections: the per-connection lock guards nothing"
    led = Ledger(str(tmp_path / "t.sqlite3"))
    n = led.counts()["requests"]
    led.close()
    assert n == 16, f"recorded {n} of 16"


def test_a_failed_write_does_not_wedge_the_connection(tmp_path):
    """detect.py swallows the IntegrityError raised when a context re-fetches a
    secret it has already been sighted on. Without a rollback that left the
    connection inside an open write transaction, holding SQLite's write lock: the
    next writer timed out and every later write on that connection failed."""
    led = Ledger(str(tmp_path / "t.sqlite3"))
    rid = led.record_request(method="GET", path="/m/x", status=200, ip="198.51.100.7",
                             ua="GPTBot/1.2", ctx_id="a")
    led.record_mint(secret="a" * 16, ctx_id="a", path="/m/x", salt_epoch="e", request_id=rid)
    rid2 = led.record_request(method="GET", path="/c/x", status=200, ip="192.0.2.9",
                              ua="Other/1.0", ctx_id="b")
    led.record_sighting(secret="a" * 16, mint_ctx_id="a", seen_ctx_id="b",
                        mint_request_id=rid, seen_request_id=rid2, delta_s=1.0, origin="organic")
    with pytest.raises(sqlite3.IntegrityError):          # UNIQUE(secret, seen_ctx_id)
        led.record_sighting(secret="a" * 16, mint_ctx_id="a", seen_ctx_id="b",
                            mint_request_id=rid, seen_request_id=rid2, delta_s=2.0,
                            origin="organic")
    assert not led.db.in_transaction, "a refused write must not leave a transaction open"
    assert led.record_request(method="GET", path="/m/y", status=200, ip="198.51.100.8",
                              ua="GPTBot/1.2", ctx_id="c")
    led.close()


def test_another_process_can_still_write_after_a_refused_write(tmp_path):
    db = tmp_path / "t.sqlite3"
    led = Ledger(str(db))
    rid = led.record_request(method="GET", path="/m/x", status=200, ip="198.51.100.7",
                             ua="GPTBot/1.2", ctx_id="a")
    led.record_mint(secret="a" * 16, ctx_id="a", path="/m/x", salt_epoch="e", request_id=rid)
    rid2 = led.record_request(method="GET", path="/c/x", status=200, ip="192.0.2.9",
                              ua="O/1", ctx_id="b")
    led.record_sighting(secret="a" * 16, mint_ctx_id="a", seen_ctx_id="b", mint_request_id=rid,
                        seen_request_id=rid2, delta_s=1.0, origin="organic")
    try:
        led.record_sighting(secret="a" * 16, mint_ctx_id="a", seen_ctx_id="b",
                            mint_request_id=rid, seen_request_id=rid2, delta_s=2.0,
                            origin="organic")
    except sqlite3.IntegrityError:
        pass
    r = subprocess.run([sys.executable, "-c",
                        "import sys; sys.path.insert(0, %r)\n"
                        "from canarymaze.ledger import Ledger\n"
                        "l = Ledger(%r)\n"
                        "l.record_request(method='GET', path='/m/z', status=200,"
                        " ip='198.51.100.9', ua='GPTBot/1.2', ctx_id='z'); l.close()"
                        % (str(ROOT), str(db))], capture_output=True, text=True, timeout=30)
    led.close()
    assert r.returncode == 0, "a second process must not be locked out:\n" + r.stderr


# --- append-only has to mean append-only -------------------------------------

#: (table, column, a value the column's CHECK constraint ACCEPTS). The value
#: matters: updating sighting.origin to 'rewritten' raises IntegrityError from the
#: CHECK, not from the trigger, so the test passed with the trigger deleted. It has
#: to be a change the schema would otherwise welcome - 'selftest' -> 'organic' is
#: precisely the rewrite this table exists to prevent.
REWRITES = [("request", "ua", "Rewritten/9.9"),
            ("mint", "path", "/m/somewhere-else"),
            ("sighting", "origin", "organic"),
            ("published", "method", "never happened")]


@pytest.mark.parametrize("table,col,value", REWRITES)
@pytest.mark.parametrize("verb", ["UPDATE", "DELETE"])
def test_no_table_can_be_updated_or_deleted(tmp_path, table, col, value, verb):
    """Only `request` was covered. Deleting the mint and sighting triggers from the
    schema left every test green, and `UPDATE sighting SET origin='organic'` -
    turning the operator's own probe into third-party evidence - would then have
    rewritten the record in place."""
    led = _populated(tmp_path)
    sql = (f"UPDATE {table} SET {col} = ?" if verb == "UPDATE" else f"DELETE FROM {table}")
    with pytest.raises(sqlite3.IntegrityError) as e:
        led.db.execute(sql, (value,) if verb == "UPDATE" else ())
    assert "append-only" in str(e.value), f"refused by {e.value}, not by the trigger"
    led.db.rollback()
    led.close()


def _populated(tmp_path):
    led = Ledger(str(tmp_path / "t.sqlite3"))
    rid = led.record_request(method="GET", path="/m/x", status=200, ip="198.51.100.7",
                             ua="GPTBot/1.2", ctx_id="a", origin="selftest")
    led.record_mint(secret="a" * 16, ctx_id="a", path="/m/x", salt_epoch="e", request_id=rid)
    led.record_published(secret="a" * 16, method="handed over")
    rid2 = led.record_request(method="GET", path="/c/x", status=200, ip="192.0.2.9",
                              ua="O/1", ctx_id="b", origin="selftest")
    led.record_sighting(secret="a" * 16, mint_ctx_id="a", seen_ctx_id="b",
                        mint_request_id=rid, seen_request_id=rid2, delta_s=1.0, origin="selftest")
    return led


@pytest.mark.parametrize("table,cols,values", [
    ("sighting", "id, secret, mint_ctx_id, seen_ctx_id, mint_request_id, seen_request_id,"
                 " delta_s, origin, ts",
     (1, "a" * 16, "a", "b", 1, 2, 1.0, "organic", "2026-10-03T10:00:00Z")),
    ("request", "id, ts, method, path, status, ip_net, ua, ctx_id, raw_line, origin, is_automated",
     (1, "2026-10-03T10:00:00Z", "GET", "/m/x", 200, "203.0.113.0/24", "Rewritten/9",
      "a", "rewritten", "organic", 1)),
])
def test_insert_or_replace_cannot_rewrite_a_row(tmp_path, table, cols, values):
    """UPDATE and DELETE abort. REPLACE deletes and re-inserts without firing
    either trigger, so every row could be rewritten under its own id - and the
    rebuilt bundle verified clean, because it is consistent with the new rows."""
    led = Ledger(str(tmp_path / "t.sqlite3"))
    rid = led.record_request(method="GET", path="/m/x", status=200, ip="198.51.100.7",
                             ua="GPTBot/1.2", ctx_id="a", origin="selftest")
    led.record_mint(secret="a" * 16, ctx_id="a", path="/m/x", salt_epoch="e", request_id=rid)
    rid2 = led.record_request(method="GET", path="/c/x", status=200, ip="192.0.2.9",
                              ua="O/1", ctx_id="b", origin="selftest")
    led.record_sighting(secret="a" * 16, mint_ctx_id="a", seen_ctx_id="b", mint_request_id=rid,
                        seen_request_id=rid2, delta_s=1.0, origin="selftest")
    q = f"INSERT OR REPLACE INTO {table} ({cols}) VALUES ({','.join('?' * len(values))})"
    with pytest.raises(sqlite3.IntegrityError):
        led.db.execute(q, values)
    led.db.rollback()
    assert led.counts()["sightings_organic"] == 0
    led.close()


# --- an operator-issued secret is never organic evidence ----------------------

def test_a_stranger_fetching_an_operator_issued_secret_is_not_organic(tmp_path):
    """If the operator's own probe was issued the secret, a third party can only
    have the URL because the operator passed it on. Counting that as organic
    relies on remembering to record a disclosure - the opt-in step F-0004 says
    gets forgotten. It is structural now: organic needs a third party on BOTH
    sides."""
    led = Ledger(str(tmp_path / "t.sqlite3"))
    rid = led.record_request(method="GET", path="/m/x", status=200, ip="203.0.113.5",
                             ua="ctx-probe/1.0", ctx_id="op", origin="selftest")
    led.record_mint(secret="a" * 16, ctx_id="op", path="/m/x", salt_epoch="e", request_id=rid)
    rid2 = led.record_request(method="GET", path="/c/x", status=200, ip="23.98.142.180",
                              ua="ChatGPT-User/1.0", ctx_id="third", origin="organic")
    led.record_sighting(secret="a" * 16, mint_ctx_id="op", seen_ctx_id="third",
                        mint_request_id=rid, seen_request_id=rid2, delta_s=5.0, origin="organic")
    c = led.counts()
    led.close()
    assert c["sightings_organic"] == 0, "the secret was issued to the operator's own probe"
    assert c["sightings_paste"] == 1


def test_a_stranger_fetching_a_strangers_secret_is_organic(tmp_path):
    """The mirror: the rule must not have made organic unreachable."""
    led = Ledger(str(tmp_path / "t.sqlite3"))
    rid = led.record_request(method="GET", path="/m/x", status=200, ip="198.51.100.7",
                             ua="GPTBot/1.2", ctx_id="a", origin="organic")
    led.record_mint(secret="a" * 16, ctx_id="a", path="/m/x", salt_epoch="e", request_id=rid)
    rid2 = led.record_request(method="GET", path="/c/x", status=200, ip="192.0.2.9",
                              ua="ClaudeBot/1.0", ctx_id="b", origin="organic")
    led.record_sighting(secret="a" * 16, mint_ctx_id="a", seen_ctx_id="b", mint_request_id=rid,
                        seen_request_id=rid2, delta_s=5.0, origin="organic")
    c = led.counts()
    led.close()
    assert c["sightings_organic"] == 1 and c["sightings_paste"] == 0


# --- retired ledgers, and the archives of them --------------------------------

def test_an_archived_ledger_is_refused_as_a_live_one(tmp_path):
    """retire_ledger.py names archives <stem>-<stamp>-<label>.sqlite3, and none of
    those names was in the registry - so every archived copy was accepted as a
    live ledger and could republish the rows it was retired for.

    Synthetic names, plus whatever is really in ledgers/archive/. The real files
    are gitignored (they are evidence, not source), so a clone has none - and an
    assertion that there are some made the suite fail on arrival."""
    names = ["canary-20261003T095144Z-dev.sqlite3",
             "canary-public-20261003T141052Z-polluted.sqlite3",
             "anything-at-all.sqlite3"]            # by directory, whatever it is called
    for n in names:
        f = tmp_path / "ledgers" / "archive" / n
        f.parent.mkdir(parents=True, exist_ok=True)
        f.touch()
        assert is_retired(str(f)), f"{n} is accepted as a live ledger"
        with pytest.raises(SystemExit):
            ledger_path(str(f))
    for f in sorted((ROOT / "ledgers" / "archive").glob("*.sqlite3")):
        assert is_retired(str(f)), f"{f.name} is accepted as a live ledger"


def test_the_live_ledger_is_not_mistaken_for_an_archive():
    """The first version of that rule matched any name starting with a retired
    stem, so `canary-public-3` read as an archive of `canary` and every make
    target refused to run."""
    assert is_retired(ledger_path()) is None


def test_the_canary_route_answers_200_even_when_the_ledger_cannot_be_opened(tmp_path, monkeypatch):
    """ALWAYS 200 is the route's contract: a 404 or 500 for the second context
    ends the observation. A lookup outside the try made an unopenable ledger
    return 500."""
    monkeypatch.setenv("CANARY_ALLOW_DEV_SALT", "1")
    bad = tmp_path / "no-such-dir" / "t.sqlite3"
    client = create_app(db_path=str(bad)).test_client()
    for path in ("/m/q3-supplier-review", "/c/deadbeefdeadbeef/q3-supplier-review"):
        r = client.get(path, headers=BOT, environ_overrides={"REMOTE_ADDR": "198.51.100.7"})
        assert r.status_code == 200, f"{path} returned {r.status_code}"
