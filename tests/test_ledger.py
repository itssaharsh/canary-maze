import sqlite3

import pytest

from canarymaze.ledger import Ledger, truncate_ip


@pytest.mark.parametrize("addr,expected", [
    ("20.171.207.14", "20.171.207.0/24"),
    ("104.28.52.9", "104.28.52.0/24"),
    ("2606:4700:4700::1111", "2606:4700:4700::/48"),
    ("not-an-ip", "unknown"),
    ("", "unknown"),
])
def test_addresses_are_truncated_before_storage(addr, expected):
    assert truncate_ip(addr) == expected


def test_full_address_never_reaches_the_row(ledger):
    rid = ledger.record_request(method="GET", path="/m/a", status=200,
                                ip="20.171.207.14", ua="GPTBot/1.2", ctx_id="a1")
    row = ledger.request(rid)
    assert row["ip_net"] == "20.171.207.0/24"
    # the octet we dropped must not survive anywhere on the row, raw line included
    assert ".14" not in row["ip_net"]
    assert "20.171.207.14" not in row["raw_line"]


def test_raw_line_is_a_readable_access_log_record(ledger):
    rid = ledger.record_request(method="GET", path="/c/abc/x", status=200,
                                ip="104.28.52.9", ua="Chrome/124", ctx_id="b2", size=1204)
    raw = ledger.request(rid)["raw_line"]
    assert raw.startswith("104.28.52.0/24 - - [")
    assert '"GET /c/abc/x HTTP/1.1" 200 1204' in raw


def test_ledger_is_append_only(ledger):
    rid = ledger.record_request(method="GET", path="/m/a", status=200,
                                ip="1.2.3.4", ua="GPTBot/1.2", ctx_id="a1")
    with pytest.raises(sqlite3.IntegrityError):
        ledger.db.execute("UPDATE request SET ua='edited' WHERE id=?", (rid,))
    with pytest.raises(sqlite3.IntegrityError):
        ledger.db.execute("DELETE FROM request WHERE id=?", (rid,))


def test_origin_is_constrained(ledger):
    with pytest.raises(ValueError):
        ledger.record_request(method="GET", path="/", status=200, ip="1.2.3.4",
                              ua="x", ctx_id="a1", origin="made-up")


def test_counts_start_clean_and_expose_the_human_counter(ledger):
    c = ledger.counts()
    assert c["human_requests"] == 0
    assert c["sightings_organic"] == 0 and c["sightings_seeded"] == 0


def test_laundered_table_is_not_part_of_the_proof_graph(ledger):
    with pytest.raises(ValueError):
        ledger.rows("laundered")
