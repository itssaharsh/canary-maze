"""The only module that writes to the ledger.

Append-only by construction: every write is an INSERT, and the schema's triggers
abort UPDATE and DELETE. Addresses are truncated at this boundary and the full
address is never passed further in, so no later mistake can store one.
"""
from __future__ import annotations

import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA = Path(__file__).with_name("schema.sql")

ORIGINS = ("organic", "seeded", "paste", "selftest")


from .netaddr import truncate_ip  # re-exported: callers imported it from here


#: Every table that may be read out as part of the proof graph.
PROOF_TABLES = ("request", "mint", "sighting", "published")

#: A sighting the server recorded as organic, on a secret the operator had already
#: published by hand when the fetch happened. One definition, in SQL, shared with
#: scripts/build_results.py - two spellings of this rule would eventually disagree
#: about the one number the project asks to be believed on. The comparison is on
#: ISO-8601 UTC strings, which order correctly as text.
SQL_PASTE_TRIGGERED = (
    "sighting.origin = 'organic' AND EXISTS (SELECT 1 FROM published p "
    "WHERE p.secret = sighting.secret AND p.ts <= sighting.ts)")
SQL_COUNT_ORGANIC = (
    f"SELECT COUNT(*) FROM sighting WHERE origin = 'organic' AND NOT ({SQL_PASTE_TRIGGERED})")
SQL_COUNT_PASTE = (
    f"SELECT COUNT(*) FROM sighting WHERE origin = 'paste' OR ({SQL_PASTE_TRIGGERED})")


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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
        # check_same_thread=False because one Ledger is shared across Flask's
        # worker threads. Without it, every concurrent request after the first
        # raised ProgrammingError and returned 500 - which on the canary route
        # loses the SIGHTING itself, and crawler fleets fetch in parallel, so that
        # was the normal case rather than an edge case. The lock below is what
        # actually makes the sharing safe; the flag only stops sqlite3 refusing.
        self.db = sqlite3.connect(self.path, check_same_thread=False, timeout=5.0)
        self.db.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        with self._lock:
            self.db.executescript(SCHEMA.read_text(encoding="utf-8"))
            self._migrate()
            self.db.commit()

    def _migrate(self) -> None:
        """Additive-only migrations for ledgers created by an earlier schema.

        ADD COLUMN is the only shape allowed here. The append-only guarantee is
        about rows, not columns, but a migration that could rewrite or drop one
        would quietly hand back the ability this product refuses to have.
        """
        have = {r[1] for r in self.db.execute("PRAGMA table_info(request)")}
        if "via" not in have:
            self.db.execute(
                "ALTER TABLE request ADD COLUMN via TEXT NOT NULL DEFAULT 'direct'")

    # -- writes ----------------------------------------------------------------
    def record_request(self, *, method: str, path: str, status: int, ip: str,
                       ua: str, ctx_id: str, origin: str = "organic",
                       is_automated: bool = True, size: int = 0,
                       ts: str | None = None, via: str = "direct") -> int:
        """`via` names the edge that reported this request. 'direct' means this
        process saw the connection; anything else is a report, and the viewer
        says so, because a reader should be able to weigh the two differently."""
        if origin not in ORIGINS:
            raise ValueError(f"origin must be one of {ORIGINS}, got {origin!r}")
        ts = ts or now_iso()
        ip_net = truncate_ip(ip)
        raw = combined_log_line(ip_net, ts, method, path, status, size, ua)
        with self._lock:
            cur = self.db.execute(
                "INSERT INTO request (ts, method, path, status, ip_net, ua, ctx_id,"
                " raw_line, origin, is_automated, via)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (ts, method, path, status, ip_net, ua, ctx_id, raw, origin,
                 1 if is_automated else 0, via))
            self.db.commit()
            return int(cur.lastrowid)

    def record_mint(self, *, secret: str, ctx_id: str, path: str,
                    salt_epoch: str, request_id: int, ts: str | None = None) -> int:
        with self._lock:
            cur = self.db.execute(
                "INSERT INTO mint (secret, ctx_id, path, salt_epoch, ts, request_id)"
                " VALUES (?,?,?,?,?,?)",
                (secret, ctx_id, path, salt_epoch, ts or now_iso(), request_id))
            self.db.commit()
            return int(cur.lastrowid)

    def record_sighting(self, *, secret: str, mint_ctx_id: str, seen_ctx_id: str,
                        mint_request_id: int, seen_request_id: int, delta_s: float,
                        origin: str, ts: str | None = None) -> int:
        with self._lock:
            cur = self.db.execute(
                "INSERT INTO sighting (secret, mint_ctx_id, seen_ctx_id, mint_request_id,"
                " seen_request_id, delta_s, origin, ts) VALUES (?,?,?,?,?,?,?,?)",
                (secret, mint_ctx_id, seen_ctx_id, mint_request_id, seen_request_id,
                 float(delta_s), origin, ts or now_iso()))
            self.db.commit()
            return int(cur.lastrowid)

    def record_published(self, *, secret: str, method: str, ts: str | None = None) -> int:
        """Record that the operator handed this secret to someone by hand.

        From this moment a fetch of it shows a fetcher following a published link,
        not two clients sharing, and is reported as paste-triggered. A secret that
        was never issued cannot be published: there would be nothing to follow.
        """
        if self.mint_for_secret(secret) is None:
            raise ValueError("cannot publish a secret that was never issued")
        with self._lock:
            cur = self.db.execute(
                "INSERT INTO published (secret, ts, method) VALUES (?,?,?)",
                (secret, ts or now_iso(), method))
            self.db.commit()
            return int(cur.lastrowid)

    # -- reads -----------------------------------------------------------------
    def mint_for_secret(self, secret: str) -> sqlite3.Row | None:
        with self._lock:
            return self.db.execute("SELECT * FROM mint WHERE secret = ?", (secret,)).fetchone()

    def mint_for(self, ctx_id: str, path: str, salt_epoch: str) -> sqlite3.Row | None:
        with self._lock:
            return self.db.execute(
                "SELECT * FROM mint WHERE ctx_id = ? AND path = ? AND salt_epoch = ?",
                (ctx_id, path, salt_epoch)).fetchone()

    def request(self, request_id: int) -> sqlite3.Row | None:
        with self._lock:
            return self.db.execute("SELECT * FROM request WHERE id = ?", (request_id,)).fetchone()

    def paste_triggered_ids(self) -> set[int]:
        """Ids of sightings recorded as organic that the paste rule reclassifies."""
        with self._lock:
            return {int(r[0]) for r in self.db.execute(
                f"SELECT sighting.id FROM sighting WHERE {SQL_PASTE_TRIGGERED}")}

    def rows(self, table: str) -> list[dict[str, Any]]:
        if table not in PROOF_TABLES:
            raise ValueError(f"{table!r} is not part of the proof graph")
        with self._lock:
            return [dict(r) for r in self.db.execute(f"SELECT * FROM {table} ORDER BY id")]

    def note_gate_rejection(self) -> None:
        """Count a request the gate refused, storing NOTHING about it.

        This exists because the previous honesty counter was vacuous: it counted
        `request` rows with is_automated=0, and nothing in the codebase ever wrote
        one, so it was pinned to 0 by construction rather than by the gate working.
        A reviewer pointed out you could delete the gate entirely and the number
        would not move.

        This counter can move. It is a bare integer with no address, no user-agent
        and no timestamp per event - recording any of that would rebuild the
        visitor log the gate exists to prevent - but a non-zero value is positive
        evidence that humans arrived and were turned away, which is the claim.
        """
        with self._lock:
            self.db.execute(
                "INSERT INTO gate_rejection (id, n) VALUES (1, 1) "
                "ON CONFLICT(id) DO UPDATE SET n = n + 1")
            self.db.commit()

    def counts(self) -> dict[str, int]:
        """The honesty counters.

        `humans_turned_away` is the falsifiable one: it rises when the gate fires.
        `human_requests` is retained and must stay 0 - it counts ledger rows marked
        non-automated, so a non-zero value means a human reached storage.
        `sightings_selftest` is the operator's own traffic, kept out of the organic
        number on purpose; see request_origin() in app.py.
        """
        with self._lock:
            one = lambda q, *a: int(self.db.execute(q, a).fetchone()[0])
            return {
                "mints": one("SELECT COUNT(*) FROM mint"),
                # Organic excludes anything fetched after the operator published
                # the secret by hand; those are counted as paste-triggered below.
                "sightings_organic": one(SQL_COUNT_ORGANIC),
                "sightings_seeded": one("SELECT COUNT(*) FROM sighting WHERE origin='seeded'"),
                "sightings_paste": one(SQL_COUNT_PASTE),
                # The operator's own probes. Counted, never folded into organic:
                # a verification curl is not third-party evidence, and publishing
                # it as such is the overclaim this whole product exists to avoid.
                "sightings_selftest": one("SELECT COUNT(*) FROM sighting WHERE origin='selftest'"),
                "human_requests": one("SELECT COUNT(*) FROM request WHERE is_automated=0"),
                "humans_turned_away": one("SELECT COALESCE(MAX(n), 0) FROM gate_rejection"),
                "published": one("SELECT COUNT(DISTINCT secret) FROM published"),
                "requests": one("SELECT COUNT(*) FROM request"),
                # Rows this process saw itself, vs rows an edge reported to it.
                # A reader weighing the evidence is entitled to the split.
                "requests_direct": one("SELECT COUNT(*) FROM request WHERE via='direct'"),
                "requests_reported": one("SELECT COUNT(*) FROM request WHERE via<>'direct'"),
            }

    def close(self) -> None:
        self.db.close()
