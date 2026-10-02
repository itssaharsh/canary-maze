"""The only module that writes to the ledger.

Append-only by construction: every write is an INSERT, and the schema's triggers
abort UPDATE and DELETE. Addresses are truncated at this boundary and the full
address is never passed further in, so no later mistake can store one.
"""
from __future__ import annotations

import ipaddress
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA = Path(__file__).with_name("schema.sql")

ORIGINS = ("organic", "seeded", "paste")


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def truncate_ip(addr: str) -> str:
    """Reduce an address to the network we are allowed to keep.

    IPv4 -> /24, IPv6 -> /48. An unparseable address becomes 'unknown' rather than
    being stored verbatim, because the failure mode we refuse is storing a full
    address by accident.
    """
    try:
        ip = ipaddress.ip_address(addr.strip())
    except ValueError:
        return "unknown"
    prefix = 24 if ip.version == 4 else 48
    net = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)
    return str(net)


def combined_log_line(ip_net: str, ts: str, method: str, path: str,
                      status: int, size: int, ua: str) -> str:
    """Render a row the way an operator reads it in their own access log.

    The address is already truncated, so this is the record as we are willing to
    publish it, not a reconstruction of the original line.
    """
    return (f'{ip_net} - - [{ts}] "{method} {path} HTTP/1.1" '
            f'{status} {size} "-" "{ua}"')


@dataclass(frozen=True)
class RequestRow:
    id: int
    ts: str
    method: str
    path: str
    status: int
    ip_net: str
    ua: str
    ctx_id: str
    raw_line: str
    origin: str
    is_automated: int


class Ledger:
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA.read_text(encoding="utf-8"))
        self.db.commit()

    # -- writes ----------------------------------------------------------------
    def record_request(self, *, method: str, path: str, status: int, ip: str,
                       ua: str, ctx_id: str, origin: str = "organic",
                       is_automated: bool = True, size: int = 0,
                       ts: str | None = None) -> int:
        if origin not in ORIGINS:
            raise ValueError(f"origin must be one of {ORIGINS}, got {origin!r}")
        ts = ts or now_iso()
        ip_net = truncate_ip(ip)
        raw = combined_log_line(ip_net, ts, method, path, status, size, ua)
        cur = self.db.execute(
            "INSERT INTO request (ts, method, path, status, ip_net, ua, ctx_id,"
            " raw_line, origin, is_automated) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (ts, method, path, status, ip_net, ua, ctx_id, raw, origin,
             1 if is_automated else 0))
        self.db.commit()
        return int(cur.lastrowid)

    def record_mint(self, *, secret: str, ctx_id: str, path: str,
                    salt_epoch: str, request_id: int, ts: str | None = None) -> int:
        cur = self.db.execute(
            "INSERT INTO mint (secret, ctx_id, path, salt_epoch, ts, request_id)"
            " VALUES (?,?,?,?,?,?)",
            (secret, ctx_id, path, salt_epoch, ts or now_iso(), request_id))
        self.db.commit()
        return int(cur.lastrowid)

    def record_sighting(self, *, secret: str, mint_ctx_id: str, seen_ctx_id: str,
                        mint_request_id: int, seen_request_id: int, delta_s: float,
                        origin: str, ts: str | None = None) -> int:
        cur = self.db.execute(
            "INSERT INTO sighting (secret, mint_ctx_id, seen_ctx_id, mint_request_id,"
            " seen_request_id, delta_s, origin, ts) VALUES (?,?,?,?,?,?,?,?)",
            (secret, mint_ctx_id, seen_ctx_id, mint_request_id, seen_request_id,
             float(delta_s), origin, ts or now_iso()))
        self.db.commit()
        return int(cur.lastrowid)

    # -- reads -----------------------------------------------------------------
    def mint_for_secret(self, secret: str) -> sqlite3.Row | None:
        return self.db.execute("SELECT * FROM mint WHERE secret = ?", (secret,)).fetchone()

    def mint_for(self, ctx_id: str, path: str, salt_epoch: str) -> sqlite3.Row | None:
        return self.db.execute(
            "SELECT * FROM mint WHERE ctx_id = ? AND path = ? AND salt_epoch = ?",
            (ctx_id, path, salt_epoch)).fetchone()

    def request(self, request_id: int) -> sqlite3.Row | None:
        return self.db.execute("SELECT * FROM request WHERE id = ?", (request_id,)).fetchone()

    def rows(self, table: str) -> list[dict[str, Any]]:
        if table not in ("request", "mint", "sighting"):
            raise ValueError(f"{table!r} is not part of the proof graph")
        return [dict(r) for r in self.db.execute(f"SELECT * FROM {table} ORDER BY id")]

    def counts(self) -> dict[str, int]:
        """The honesty counters. `human_requests` exists so the claim that humans
        are excluded is checkable rather than asserted; the gate should keep it 0."""
        one = lambda q, *a: int(self.db.execute(q, a).fetchone()[0])
        return {
            "mints": one("SELECT COUNT(*) FROM mint"),
            "sightings_organic": one("SELECT COUNT(*) FROM sighting WHERE origin='organic'"),
            "sightings_seeded": one("SELECT COUNT(*) FROM sighting WHERE origin='seeded'"),
            "sightings_paste": one("SELECT COUNT(*) FROM sighting WHERE origin='paste'"),
            "human_requests": one("SELECT COUNT(*) FROM request WHERE is_automated=0"),
            "requests": one("SELECT COUNT(*) FROM request"),
        }

    def close(self) -> None:
        self.db.close()
