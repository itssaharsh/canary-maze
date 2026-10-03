---
id: F-0004
type: failure
title: process-wide origin labelled the operator's own probes as third-party evidence
status: active
scope: global-candidate
components: canarymaze/app.py, canarymaze/ledger.py, canarymaze/export.py, viewer/render.js, scripts/trigger_paste.py
triggers: adding an origin/source/provenance column, probing a surface that records its own traffic, any counter that is the product's headline claim
evidence: canarymaze/app.py:request_origin, tests/test_selftest_origin.py, ledgers/archive/README.md
verified_at: 2026-10-03
relates: F-0003, U-0001, ADR-0002
supersedes: 
helpful: 0
harmful: 0
cite_hash: 
created: 2026-10-03
source: self-observed during live verification
---

ATTEMPTED: verify the public tunnel was serving after restarting Flask, with a
plain `curl https://<tunnel>/c/<secret>/<slug>`.

ERROR SIGNATURE: none - status 200, exactly as wanted. The damage was silent and
only visible one step later, when the exporter reported `sightings_organic: 1`
on a ledger that had had 0. The sighting was my own curl: UA `curl/8.5.0`,
`origin='organic'`, 90 seconds old, and about to be published to judges as
evidence that a third party had fetched a secret.

ROOT CAUSE: `origin` was a single process-wide value (`app.config["ORIGIN"]`,
set once in `create_app`), so the server stamped the same label on every row it
ever wrote. There was no way for a request to be anything other than what the
process was started as. The operator's smoke tests, uptime checks and
verification probes were therefore indistinguishable from third-party traffic in
the one table the whole product asks to be believed on. A second, quieter bug sat
behind it: `render.js` fell through to the string "organic traffic" for any
origin it did not recognise, so even a correctly-labelled row would have been
published as organic by the viewer.

FIX: `request_origin(req, default)` resolves the origin per request. A request
carrying `X-Canary-Selftest: <token>` matching `CANARY_SELFTEST_TOKEN` is
recorded as `origin='selftest'`; `sightings_selftest` is counted separately and
never folded into organic; `_claim()` discloses a self-test sighting in the
headline; `render.js` names every origin explicitly and says "unrecognised"
rather than guessing the strongest reading. The token is secret and absence fails
closed to the default - if the header alone sufficed, a fetcher could label
itself a self-test and opt out of being observed, which inverts the threat model.
The polluted ledger was NOT edited: it is append-only, and that immutability is
the product's integrity claim. It was retired to `ledgers/archive/` with a
written reason and production moved to `ledgers/canary-public.sqlite3`.
Verified over the public internet: correct token -> selftest, forged token ->
organic, 4 new tests, 117 passing.

LESSON: when a system records its own traffic, the operator is a participant in
the data, not an observer of it. Any provenance field that is configured
per-process rather than per-request will eventually attribute the operator's
actions to someone else, and it will do so silently, because the probe that
causes it is the one that reports success. A field whose whole job is to
separate "us" from "them" must be resolvable at the granularity that the
distinction occurs - the request - and the UI over it must refuse to guess.

CHEAPEST EARLY CHECK: before trusting any count that distinguishes your traffic
from a third party's, grep your own verification commands for requests to the
surface, then ask which row each one wrote and under what label. If the answer is
"the same label as a stranger", the counter is not evidence.

---

## Recurrence, same day, two new routes (2026-10-03, hours later)

The fix above was correct and incomplete. Moving the live ledger to
`ledgers/canary-public.sqlite3` was done by hand in `make serve` only;
`seed_replay.py`, `export_all.py`, `trigger_paste.py` and the app's own fallback
still defaulted to the old path, which by then held the RETIRED ledger. So
`trigger_paste.py --report` printed `sightings_organic 1` - reading the very row
that had been retired for being the operator's own curl - while the live ledger
sat at 0. The number was wrong, plausible, and about to be reported.

At the same moment the second half failed too: the script was run in a shell that
had not sourced `.env`, so `CANARY_SELFTEST_TOKEN` was unset, the warning was
printed and ignored, and the operator's own setup request was recorded as
`origin='organic'` exactly as before.

FIX: `canarymaze/paths.py` is now the only place that decides which ledger to
open. `ledger_path()` resolves explicit argument -> `CANARY_DB` -> default, and
RAISES on a ledger listed in `RETIRED` (matched on file name, so every spelling
is caught) unless deliberately overridden. `load_env()` loads `.env` inside the
scripts that need the token, so the operator cannot forget to source it; exported
values still win. `--report` now prints which ledger it read. 9 tests.

LESSON: retiring a file is not finished when the new path is written down
somewhere - it is finished when the OLD path is made to fail loudly. A default
that still resolves to retired data will be found by some code path, and it will
return a plausible number rather than an error. The same applies to a required
environment variable: a warning that the operator can scroll past is not a
control, because the failure it predicts lands silently in the data.

CHEAPEST EARLY CHECK: after moving any file that code opens by default,
`grep -rn '<old-name>'` across the whole repo before claiming the move is done,
and make the old name raise.

---

## Third recurrence: a guard only guards the callers that consult it (2026-10-03)

`canarymaze/paths.py` was written precisely so a retired ledger would raise
instead of being read, and the scripts were routed through it. `build_results.py`
was not - it had its own `--live` default pointing at the generation-1 ledger and
opened it directly with `sqlite3`. So `docs/RESULTS.md`, the file whose entire
claim is that its numbers are generated rather than typed, was regenerated from a
QUARANTINED ledger and published **four "organic" sightings** that were the
operator's own curls, retired hours earlier for exactly that reason.

Caught only because the number changed between two audit runs and looked wrong.

FIX: `build_results.py` resolves `--live` through `ledger_path()` like everything
else, and two tests now assert that it refuses a retired ledger and that no
hardcoded ledger path reappears in the file.

LESSON: adding a guard does not retire a path - routing every caller through it
does. The dangerous caller is always the one written *before* the guard existed
and never revisited, because it still works, and because its wrongness shows up
as a plausible number rather than an error. When introducing a chokepoint, the
commit that adds it must also be the commit that greps for everyone who should be
going through it.
