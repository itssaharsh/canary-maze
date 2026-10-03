# Archived ledgers

An append-only ledger is never edited, so one that turns out to be unpublishable
is retired here rather than corrected. Nothing in this directory is deleted, and
`canarymaze/paths.py` refuses to open a retired ledger by accident.

The database files are not in git (they are evidence, not source); this file is.
Row counts below are produced by `python3 scripts/retire_ledger.py --verify`.

**These archives were once wrong.** The first three were made with `cp`. The
ledgers are WAL-mode SQLite, so most of their rows were still in the `-wal` file,
and the copies came out holding 1 of 7 requests, no tables at all, and 14 of 18
requests - the last one missing the very sighting it had been retired for. An
independent review opened them and found it. They have been rebuilt with SQLite's
backup API, which reads through the WAL, by `scripts/retire_ledger.py`, which
counts the rows on both sides and refuses to report success unless they match.

| Archive | Requests | Mints | Sightings | Retired because |
|---|---|---|---|---|
| `canary-20261003T095144Z-dev.sqlite3` | 7 | 4 | 1 | its one sighting is the operator's own `curl`, recorded as organic |
| `canary-public-20261003T141052Z-polluted.sqlite3` | 9 | 5 | 4 | four "organic" sightings are the operator's diagnostic `curl`s |
| `canary-public-2-20261003T180203Z-unstable-context.sqlite3` | 18 | 15 | 3 | its context ids came from a fingerprint that hashed the platform's headers |

## 1. `canary-*-dev` — the operator's probe, recorded as organic

Sighting 1 in it is the operator's own `curl/8.5.0`, written with
`origin='organic'` by a build that stamped one process-wide origin on every row.
Mechanically a true sighting; worthless as evidence, and misleading if published
as third-party traffic. `origin` is now resolved per request (F-0004).

## 2. `canary-public-*-polluted` — the same mistake, the third time

Four sightings, all marked organic, are the operator's diagnostic `curl`s, sent
while investigating why a crawler received 403 from the edge - without the
self-test token, because the token was opt-in and was forgotten for the third
time, *while diagnosing the second*. A token the operator must remember on every
probe is a reminder, not a control. The surface now recognises the operator's own
networks with no cooperation from the client (F-0004).

## 3. `canary-public-2-*-unstable-context` — contexts that could not be trusted

The fingerprint hashed the name of every request header it saw, including the
ones the hosting platform injects, which differ between routes. One client that
fetched a maze page and then followed its own canary link came out as two
contexts, and the ledger recorded a sighting for the commonest harmless event
there is (sighting 3, 17:57:34Z). It was found by testing for it directly from
the operator's own network, so it is labelled `selftest` and never touched the
organic count. The context is now derived from an allowlist of client headers
with order ignored (F-0006).

None of the three ever held a row from a third party. The live ledger is whatever
`python3 -c "from canarymaze.paths import ledger_path; print(ledger_path())"`
prints.
