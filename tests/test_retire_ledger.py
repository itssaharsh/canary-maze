"""An archive has to hold what its source held.

The first three retired ledgers were archived with `cp`. They are WAL-mode
databases, so the copies came out with 1 of 7 requests, no tables at all, and 14
of 18 - the last one missing the sighting it had been retired for. Nobody had
opened them. scripts/retire_ledger.py copies through SQLite's backup API and
refuses to succeed unless the row counts match.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from retire_ledger import counts, retire          # noqa: E402

from canarymaze.ledger import Ledger               # noqa: E402


def test_an_archive_holds_every_row_even_while_the_source_is_still_open(tmp_path):
    """The source connection is deliberately left OPEN and un-checkpointed: that
    is the state a ledger is in when a running server is retired, and the state
    in which a plain file copy silently drops whatever is still in the WAL."""
    src = tmp_path / "live.sqlite3"
    led = Ledger(str(src))
    for i in range(40):
        rid = led.record_request(method="GET", path=f"/m/p{i}", status=200,
                                 ip="198.51.100.7", ua="GPTBot/1.2", ctx_id=f"ctx{i}")
        led.record_mint(secret=f"{i:016x}", ctx_id=f"ctx{i}", path=f"/m/p{i}",
                        salt_epoch="e", request_id=rid)
    led.note_gate_rejection()

    dest = retire(src, "test", tmp_path / "archive" / "copy.sqlite3")
    assert counts(dest) == {"request": 40, "mint": 40, "sighting": 0, "published": 0,
                            "gate_rejection": 1}
    assert not Path(str(dest) + "-wal").exists(), "an archive must be one self-contained file"
    led.close()


def test_the_archive_is_still_append_only(tmp_path):
    """A retired ledger is evidence. The triggers travel with it."""
    import sqlite3
    import pytest
    src = tmp_path / "live.sqlite3"
    led = Ledger(str(src))
    led.record_request(method="GET", path="/m/x", status=200, ip="198.51.100.7",
                       ua="GPTBot/1.2", ctx_id="c")
    dest = retire(src, "test", tmp_path / "copy.sqlite3")
    led.close()
    con = sqlite3.connect(dest)
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("UPDATE request SET ua='edited'")
    con.close()
