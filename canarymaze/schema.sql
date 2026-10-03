-- Canary Maze ledger.
--
-- Two things are deliberate here and a reviewer should check both:
--
--  1. There is NO `actor` table, and no join anywhere produces one. The unit is a
--     REQUEST CONTEXT. One operator can present as many contexts: in the organizers'
--     collusion.wiki dump, a single actor label carries 899 revisions across 741
--     distinct addresses. A sighting therefore establishes that a secret moved
--     between two request contexts, and nothing more. See docs/memory/decisions/ADR-0002.
--
--  2. The tables are append-only, enforced by triggers rather than by convention,
--     because the bundle's whole value is that nobody edited the rows after the fact.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS request (
    id           INTEGER PRIMARY KEY,
    ts           TEXT    NOT NULL,              -- ISO-8601 UTC, seconds
    method       TEXT    NOT NULL,
    path         TEXT    NOT NULL,
    status       INTEGER NOT NULL,
    ip_net       TEXT    NOT NULL,              -- /24 (v4) or /48 (v6). NEVER a full address.
    ua           TEXT    NOT NULL,
    ctx_id       TEXT    NOT NULL,
    raw_line     TEXT    NOT NULL,              -- combined-log rendering, for the record pair
    origin       TEXT    NOT NULL CHECK (origin IN ('organic', 'seeded', 'paste', 'selftest')),
    -- Which edge reported this request. 'direct' means this process saw the
    -- connection itself; anything else is a REPORT from a named edge, and a
    -- reader is entitled to weigh it differently. See ADR-0006.
    via          TEXT    NOT NULL DEFAULT 'direct',
    is_automated INTEGER NOT NULL CHECK (is_automated IN (0, 1))
);
CREATE INDEX IF NOT EXISTS request_ctx ON request (ctx_id);

CREATE TABLE IF NOT EXISTS mint (
    id         INTEGER PRIMARY KEY,
    secret     TEXT    NOT NULL UNIQUE,
    ctx_id     TEXT    NOT NULL,
    path       TEXT    NOT NULL,
    salt_epoch TEXT    NOT NULL,                -- so rotation never invalidates history
    ts         TEXT    NOT NULL,
    request_id INTEGER NOT NULL REFERENCES request (id)
);
CREATE INDEX IF NOT EXISTS mint_ctx ON mint (ctx_id);

CREATE TABLE IF NOT EXISTS sighting (
    id              INTEGER PRIMARY KEY,
    secret          TEXT    NOT NULL REFERENCES mint (secret),
    mint_ctx_id     TEXT    NOT NULL,
    seen_ctx_id     TEXT    NOT NULL,
    mint_request_id INTEGER NOT NULL REFERENCES request (id),
    seen_request_id INTEGER NOT NULL REFERENCES request (id),
    delta_s         REAL    NOT NULL,
    origin          TEXT    NOT NULL CHECK (origin IN ('organic', 'seeded', 'paste', 'selftest')),
    ts              TEXT    NOT NULL,
    -- a context that fetches the same secret twice produces one sighting, not two
    UNIQUE (secret, seen_ctx_id)
);

-- Secrets the OPERATOR handed to someone by hand: pasted into a chat product, given
-- to a fetch service, or printed in a published bundle. The server cannot tell a
-- crawler that found a canary URL on its own from a fetcher that was given it -
-- both are real third-party requests - so the operator's act of publishing is
-- recorded HERE, and a fetch that comes after it is reported as paste-triggered,
-- never as organic. The reclassification only runs in that direction.
CREATE TABLE IF NOT EXISTS published (
    id     INTEGER PRIMARY KEY,
    secret TEXT    NOT NULL REFERENCES mint (secret),
    ts     TEXT    NOT NULL,
    method TEXT    NOT NULL          -- where it went, in the operator's own words
);
CREATE INDEX IF NOT EXISTS published_secret ON published (secret);

-- Laundered (paraphrased) token candidates. Shipped DISABLED. This table is never
-- joined into the proof graph and never reaches the bundle: see canarymaze/bundle.py.
CREATE TABLE IF NOT EXISTS laundered (
    id             INTEGER PRIMARY KEY,
    secret         TEXT NOT NULL,
    candidate_text TEXT NOT NULL,
    score          REAL NOT NULL,
    ts             TEXT NOT NULL
);

-- A bare count of requests the gate refused. NO per-request data: no address, no
-- user-agent, no timestamp. Recording any of those would rebuild the visitor log
-- the gate exists to prevent. A single row that only goes up, so the claim
-- "humans are excluded" is falsifiable instead of vacuous.
CREATE TABLE IF NOT EXISTS gate_rejection (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    n  INTEGER NOT NULL DEFAULT 0
);

-- Append-only, enforced.
CREATE TRIGGER IF NOT EXISTS request_no_update BEFORE UPDATE ON request
BEGIN SELECT RAISE(ABORT, 'request is append-only'); END;
CREATE TRIGGER IF NOT EXISTS request_no_delete BEFORE DELETE ON request
BEGIN SELECT RAISE(ABORT, 'request is append-only'); END;
CREATE TRIGGER IF NOT EXISTS mint_no_update BEFORE UPDATE ON mint
BEGIN SELECT RAISE(ABORT, 'mint is append-only'); END;
CREATE TRIGGER IF NOT EXISTS mint_no_delete BEFORE DELETE ON mint
BEGIN SELECT RAISE(ABORT, 'mint is append-only'); END;
CREATE TRIGGER IF NOT EXISTS sighting_no_update BEFORE UPDATE ON sighting
BEGIN SELECT RAISE(ABORT, 'sighting is append-only'); END;
CREATE TRIGGER IF NOT EXISTS sighting_no_delete BEFORE DELETE ON sighting
BEGIN SELECT RAISE(ABORT, 'sighting is append-only'); END;
CREATE TRIGGER IF NOT EXISTS published_no_update BEFORE UPDATE ON published
BEGIN SELECT RAISE(ABORT, 'published is append-only'); END;
CREATE TRIGGER IF NOT EXISTS published_no_delete BEFORE DELETE ON published
BEGIN SELECT RAISE(ABORT, 'published is append-only'); END;
