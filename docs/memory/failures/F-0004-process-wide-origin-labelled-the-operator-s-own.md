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
