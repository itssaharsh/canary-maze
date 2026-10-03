# Canary Maze — final build report

mode: hackathon · channel: direct · 2026-10-03

## Built

A canary surface that lets a site operator demonstrate that a secret issued to one
automated request context was later fetched by a **different** one, and hand the
record to someone who does not trust them. The bundle verifies with the server off.

- Human-exclusion gate: humans are never minted for and never enter the ledger.
- Per-context mint: `secret = HMAC(salt, path|ctx_id)`, bound to request and time.
- Canary route returns 200 for every context, or no sighting could be observed.
- Append-only SQLite ledger (UPDATE/DELETE blocked by triggers).
- Evidence bundle + offline verifier, recomputed in the browser with `crypto.subtle`.
- Seeded two-client replay as the primary deliverable.
- Viewer whose every sentence is computed in `canarymaze/export.py`.

All 9 acceptance criteria pass. 117 tests. `make verify` PASS, run three times
with a reset between.

## Architecture

One Flask process, one SQLite file, no queue, no cache, no second datastore, no
model on the proof path (ADR-0001). Four decision functions carry the product:
`gate.is_automated`, `mint.secret_for`, `detect.on_canary_request`,
`bundle.verify`. Everything else is plumbing.

The schema has no `actor` entity, by construction, so the claim "these two
contexts are two operators" cannot be made by accident (ADR-0002).

Viewer is static and deploys to Vercel; the canary surface is a Cloudflare quick
tunnel to this machine, because the ledger must be the same file the bundle was
built from (ADR-0004, ADR-0005).

## Deployment

| Surface | URL | State |
|---|---|---|
| Landing page | https://site-nine-hazel-35.vercel.app | 200, 0 axe violations |
| Evidence viewer | https://site-nine-hazel-35.vercel.app/viewer/ | 200, zero external requests |
| Canary surface | printed by `scripts/serve_public.sh` | up, URL changes per run |

Deployment Protection is off, so a judge can open both without an account.
Verified live by fetching each over the public internet.

## Bugs

Six blocking findings from a fresh reviewer, each reproduced before being fixed:

1. B1 the viewer's verify button computed nothing while claiming it did (F-0003). [E0057]
2. B2 `/export.json` published the live secret, letting any reader manufacture a sighting. [E0058]
3. B3 one SQLite connection shared across Flask threads, 500ing the canary route. [E0059]
4. B4 three distinct bundle tamperings still verified. [E0060]
5. B5 a UA claiming Googlebot beat real browser headers; rule order was inverted. [E0061]
6. B6 the human-exclusion counter could not rise, so the privacy claim was vacuous. [E0062]

A seventh was found during live verification, after the review: a verification
`curl` was recorded as an **organic sighting**, because `origin` was a single
process-wide value. Fixed by resolving origin per request behind a secret token
(`X-Canary-Selftest`), counted separately, disclosed in the headline claim, and
recorded as F-0004. The polluted ledger was retired to `ledgers/archive/` rather
than edited, because it is append-only and that is the integrity claim. [E0049]

That fix was correct and incomplete, which the next live run exposed: moving the
ledger was done in `make serve` only, so four other defaults still pointed at the
old path and `trigger_paste.py --report` printed `sightings_organic 1` by reading
the retired row itself, while the live ledger sat at 0. `canarymaze/paths.py` is
now the only place that resolves a ledger, and a retired one raises rather than
resolving. `.env` loads inside the scripts that need the self-test token, because
a warning the operator can scroll past is not a control. [E0063]

Earlier, self-inflicted: `make clean` deleted the live ledger during a demo gate
(F-0002), and the committed development salt would have let any reader forge a
secret (F-0001). [E0046]

## Verification

| Check | Command or observation | Result |
|---|---|---|
| Full suite | `python3 -m pytest -q` | 117 passed [E0056] |
| Offline proof, 5 properties | `make verify` with the server stopped | PASS [E0040] |
| Demo flow, three runs with a reset between | `make clean && make demo` x3 | identical output each time [E0044] |
| Human-exclusion gate, live over HTTP | real browser visit to the public surface | turned away 1, ledger rows unchanged [E0062] |
| Per-request origin, live over the internet | correct token vs forged token | selftest vs organic [E0049] |
| Canary surface publicly reachable | tunnel: robots, sitemap, mint, canary | all 200 [E0047] |
| Viewer and landing page on Vercel | both URLs, no account needed | 200, 0 axe violations [E0048] |
| Secrets | tracked files and full git history | clean [E0055] |
| Reported numbers match the ledgers | `scripts/build_results.py --check` | matches, gated by `make verify` |

The verifier is the load-bearing one: it recomputes every hash in the page with
`crypto.subtle` from the bundle it was shipped, contacts nothing, and names the
row that fails when any byte is altered.

## Known limitations

Three were deliberately left unfixed, because each needs a design decision rather
than a patch. They are stated in `README.md#Limitations`, not hidden:

1. The Merkle root is neither published nor signed anywhere the operator does not
   control. The bundle proves nothing has been edited since it was built; it does
   not prove it was built honestly.
2. A client can manufacture a second context against itself by varying header
   order. The viewer's diff makes it visible; nothing refuses the record.
3. No third-party traffic has reached the surface, so there is no organic result.
   `docs/RESULTS.md` reports organic sightings as 0 and is generated from the
   ledgers so it cannot drift.

Also standing: a sighting is not two operators; tokens can be stripped by a
motivated client; the context identifier is an assumption, not a measurement.

## Cleanup

- `canary.sqlite3` retired to `ledgers/archive/` with a written reason; the live
  path is now a single `LEDGER` variable so `make serve` cannot reopen it.
- `make clean` no longer touches any ledger; `clean-ledger` is separate and needs
  a typed confirmation.
- Webfont link removed from the viewer, making the no-network claim true.
- Not removed, pending Saharsh's call: `idea_gate.py` (the prod-idea gate, now
  unused), `graphify-out/` (3.3M, the knowledge graph he asked for) and
  `prod-idea/ledger.jsonl`.

## Optimization

Not pursued, deliberately. The surface serves static pages and writes one row per
request; the viewer is 4 files and ships no framework; the bundle verifies 5 rows.
Nothing here is near a budget worth measuring against, and optimizing before
correctness would have been the wrong order. Measured instead: 0 axe violations,
and the viewer makes zero external requests.

## Memory

F-0001, F-0002, F-0003, F-0004, U-0001, ADR-0001 through ADR-0005.

Most load-bearing: F-0004 — when a system records its own traffic, the operator is
a participant in the data, not an observer of it. Any provenance field configured
per-process rather than per-request will eventually attribute the operator's
actions to someone else, silently, because the probe that causes it is the one
reporting success.

## Next steps

| Item | Owner |
|---|---|
| Paste a canary URL into a public model product, then `trigger_paste.py --report` | Saharsh — only a human can do it |
| Write-up and demo video via `product-demo-video` | after this report |
| Decide on the three cleanup candidates above | Saharsh |
| Keep the machine awake if the surface should collect overnight | the tunnel dies with it |
