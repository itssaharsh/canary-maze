---
id: F-0007
type: failure
title: append-only was enforced against two statements out of three, and the connection wedged on a refused write
status: active
scope: global-candidate
components: canarymaze/schema.sql, canarymaze/ledger.py, canarymaze/app.py
triggers: writing an append-only table; sharing one SQLite connection across threads; swallowing an IntegrityError
evidence: tests/test_durability.py
verified_at: 2026-10-03
relates: F-0004, ADR-0005
created: 2026-10-03
source: independent correctness review
---

ATTEMPTED: make the ledger append-only, and share one connection safely across
Flask's worker threads. Both were believed done: triggers on UPDATE and DELETE,
and a `threading.Lock` held on every read and write.

ERROR SIGNATURE: none in either case. Both held for every test written, and both
failed on a statement nobody had tried.

ROOT CAUSE 1 - append-only. The triggers were BEFORE UPDATE and BEFORE DELETE.
`INSERT OR REPLACE` deletes the conflicting row and inserts a new one WITHOUT
firing either, because `recursive_triggers` defaults off. So every row could be
rewritten under its own id - and the bundle rebuilt from the rewritten ledger
verified clean, because it was internally consistent with the new rows. A reviewer
turned a `selftest` sighting into an `organic` one in a single statement and the
verifier called it fine.

ROOT CAUSE 2 - the shared connection. `ledger()` was an unsynchronised
check-then-set, so N simultaneous first requests each built their own `Ledger`,
each with its own connection and its own lock: the lock that the docstring says
"actually makes the sharing safe" serialised nothing. And no write rolled back.
`detect.py` deliberately swallows the `IntegrityError` raised whenever an
already-sighted context re-fetches its secret - the commonest harmless event there
is - and without a rollback that left the connection inside an open write
transaction holding SQLite's write lock. Later writes failed instantly, reads froze
at a stale snapshot, and another process could not write at all. The routes catch
`sqlite3.Error` and still answer 200, so the surface kept serving while the ledger
recorded nothing. The live ledger already held six such re-fetches.

FIX: BEFORE INSERT guards on all four tables that refuse an insert colliding with a
row already present, plus `PRAGMA recursive_triggers = ON`. One `Ledger` per app,
double-checked under a lock. Every write through one `_write()` that rolls back and
re-raises.

LESSON: "enforced by the database" is a claim about the statements you tried.
UPDATE and DELETE were tested; REPLACE is a third way to change a row and nobody
had written it down. And a lock on a connection protects nothing if the object
holding it can be constructed twice - the race was not in the critical section but
in deciding whose critical section it was.

CHEAPEST EARLY CHECK: for an append-only table, write the test that tries every
statement that can remove a row - UPDATE, DELETE, INSERT OR REPLACE, REPLACE INTO,
ON CONFLICT REPLACE, DROP - not the two you had in mind. For a lazily constructed
shared resource, count the constructions under a thread barrier.
