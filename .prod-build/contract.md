# Implementation contract — Canary Maze
mode: hackathon | channel: direct | created: 2026-10-02
Upstream read: `hackathon-idea/ai-swarm-dynamics/idea-package.md` (gated, 0 FAIL), `UI-SPEC.md`, `ui-prototype/index.html`

## 1. Intent
- **User and moment:** the operator of a site or public API, at the moment they are asked to show a third party what happened rather than just block it.
- **What they can do:** serve a canary surface, then read a record of which request context was issued a secret and which *other* context later asked for it, and hand that record to someone who does not trust them.
- **Before → after:** before, the operator can say "these clients look similar"; after, they hold a dated record that a specific secret moved between two request contexts, and a bundle that verifies with their server switched off.

## 2. Scope
**MUST**
- Human-exclusion gate: humans are never minted for and never enter the ledger.
- Per-context mint: `secret = HMAC(salt, path|ctx_id)`, with the mint row binding secret → ctx → timestamp → raw request.
- Stable canary URL space: a secret issued to A returns **200 for any context**, or no sighting is possible.
- Sighting detection: a request for secret S by a context other than S's mint context.
- Two ledgers (mints, sightings) plus raw request rows, append-only.
- Evidence bundle + **offline** verifier (Merkle root; no network, no server).
- Seeded two-client replay as the **primary** deliverable.
- Viewer showing the claim, the figure, the record pair, verification, and the honesty counters.
- `make verify`: runs the scenario end to end, asserts a real before/after number, prints PASS/FAIL, no network.

**SHOULD**
- Chat-paste trigger script: record which third-party fetchers return after a minted URL is pasted into a public model product.
- Organic sighting counter, reported separately from seeded.

**COULD (not in this build)**
- Semantic matching of laundered (paraphrased) tokens — ships **disabled**, in a separate table, never in the proof graph.
- Multi-site federation.

**WON'T now**
- Any claim that two contexts are two actors. Any blocking or mitigation. Any user accounts. Any queue, cache, or second datastore.

## 3. Core journeys
- **J1 Mint:** an automated client requests a maze page → the gate classifies it automated → a secret is minted for its context → the page embeds that secret's canary URL → mint row + raw request persisted.
- **J2 Sight:** a *different* context requests that canary URL → it returns 200 → a sighting row is written linking both contexts and both raw requests.
- **J3 Prove:** the operator exports a bundle → a third party runs the verifier offline → it recomputes the Merkle root and confirms, or names the row that fails.

## 4. Surfaces
| Surface | Why it must exist |
|---|---|
| Maze pages (`/m/<slug>`) | the only way an automated client is issued a secret. Plumbing; never demoed. |
| Canary route (`/c/<secret>/<slug>`) | the sighting channel. Must 200 for every context. |
| Viewer (`/`) | the product: the claim, the figure, the records, verification, honesty counters. |
| `GET /export.json` | feeds the viewer and the bundle. |
| CLI: `seed-replay`, `export-bundle`, `verify-bundle`, `trigger-paste` | the deterministic path a judge can run offline. |

## 5. States per journey
| Journey | initial | loading | success | error | empty | partial | retry | disabled | permission-denied | offline/degraded |
|---|---|---|---|---|---|---|---|---|---|---|
| J1 Mint | no mints | n/a (sync) | mint row written | gate rejects → no row, 200 page | n/a | n/a | idempotent per (path,ctx,salt epoch) | human → no mint, plain page | n/a (public) | n/a |
| J2 Sight | mint exists, no sighting | n/a | sighting row + both raw requests | unknown secret → 404, logged, no row | "awaiting a sighting" | mint present, sighting absent | same secret re-fetched by same ctx → **no** sighting | n/a | n/a | n/a |
| J3 Prove | no bundle | "Verifying… n/N" | root matches, "server not contacted" | names the failing row, records unchanged | empty ledger → bundle with 0 rows, still verifies | n/a | re-runnable, deterministic | n/a | n/a | **offline is the normal case** |

## 6. Data
| Entity | Key fields | Relationships | Owner | Persistence | Source of truth | PII/retention |
|---|---|---|---|---|---|---|
| `request` | id, ts, method, path, status, raw_line, ctx_id, is_automated, origin(organic/seeded) | referenced by mint + sighting | operator | SQLite, append-only | itself | IP stored **truncated to /24**; humans never stored |
| `mint` | id, secret, ctx_id, path, salt_epoch, ts, request_id | 1 request | operator | SQLite | itself | — |
| `sighting` | id, secret, mint_ctx_id, seen_ctx_id, mint_request_id, seen_request_id, delta_s, origin | 1 mint, 1 request | operator | SQLite | itself | — |
| `laundered` | id, secret, candidate_text, score | **separate table, never joined into the proof graph** | operator | SQLite | itself | disabled by default |

## 7. Interfaces
| Interface | Purpose | Contract | Failure mode | Fallback |
|---|---|---|---|---|
| HTTP server (Flask) | serve maze, canary, viewer | routes above | process down | the bundle and verifier are files; they work with the server down — that is the point |
| SQLite | both ledgers | `schema.sql` | locked | WAL; the mint path retries once then serves the page without minting (never block a crawler) |
| Model provider | laundered-token matching only | n/a | — | **disabled by default**; absence changes nothing on the proof path |

## 8. Constraints
- **Judging criteria: none published.** Home page, verbatim: "We're assembling a team of ~3-5 judges (members of the AI Village staff and experts in the field)." Logistics, verbatim: "A panel of Grove Research and AI Village staff will review submissions." Decisions roughly a week later. Criteria assumed in the idea package: execution/method ~30%, impact on the investigators' workflow ~25%, real results on real data ~20%, originality ~15%, presentation ~10%, theme fit as a gate.
- **Submission, verbatim:** "(a) a short write-up / video explaining your project, (b) a link to github repo with your code, and (c) optionally a write-up of real results you identified by using your tool." Treated as mandatory.
- **Sponsor rules:** none. No sponsor API exists at this event; compute reimbursement is in-person only and this builder is online.
- **Budget:** £0 inference. The proof path must not call a model.
- **Deadline:** Sun 2026-10-04 17:00 PT. Build stops 15:00; the last two hours are the write-up.
- **Privacy:** per-visitor minting applied to humans would be a tracking tool. The gate is a correctness requirement, not a nicety. IPs truncated to /24 before storage.
- **Deploy:** one small host, stable URL, HTTPS, XML sitemap, **no proof-of-work gate in front of it** (it would block the traffic we need to observe).

## 9. Acceptance criteria
- **AC-1** WHEN a request carries browser headers (`Accept-Language` plus any `Sec-Fetch-*`) THE SYSTEM SHALL NOT mint and SHALL NOT write any ledger row. *Verify:* `pytest tests/test_gate.py -q`. must
- **AC-2** WHEN the same context requests the same path twice in one salt epoch THE SYSTEM SHALL return the same secret and write exactly one mint row. *Verify:* `pytest tests/test_mint.py -q`. must
- **AC-3** WHEN a canary URL is requested by the context it was minted for THE SYSTEM SHALL return 200 and SHALL NOT write a sighting. *Verify:* `pytest tests/test_detect.py -q`. must
- **AC-4** WHEN a canary URL is requested by a different context THE SYSTEM SHALL return 200 and SHALL write exactly one sighting carrying both raw request rows. *Verify:* `pytest tests/test_detect.py -q`. must
- **AC-5** WHEN any byte of any bundled row is altered THE SYSTEM SHALL fail verification and SHALL name the failing row. *Verify:* `pytest tests/test_bundle.py -q`. must
- **AC-6** WHEN the verifier runs THE SYSTEM SHALL make no network call and SHALL NOT require the server. *Verify:* `make verify` with the server stopped. must
- **AC-7** WHEN rows exist in the `laundered` table THE SYSTEM SHALL produce a byte-identical bundle, because the bundle writer cannot read that table. *Verify:* `make verify` (check 5) and `pytest -q tests/test_bundle.py -k laundered`. must. *(Reworded: the original named a `--compare-model-off` flag that was never implemented, and described disabling a model integration that was never built.)*
- **AC-8** WHEN the viewer renders THE SYSTEM SHALL display organic and seeded sighting counts separately and the human-requests-in-ledger count. *Verify:* `make demo` then assert on `viewer/data.json`. must
- **AC-9** WHEN `make demo` is run on a clean checkout with no network THE SYSTEM SHALL produce the viewer and print PASS. *Verify:* `make demo`. must

## 10. Assumptions
- **A-1 [safe]** Automated clients that ignore robots and fetch sitemap links exist and will reach a new domain quickly — validated at run time by the organic counter, reported honestly whatever it says.
- **A-2 [safe]** A request context derived from UA + /24 + header shape is stable enough within a session to make "same context re-fetch" detectable. Documented as an assumption in the README, not claimed as fact.
- **A-3 [reversible]** Flask over stdlib `http.server`: one dependency, boring, stable.
- **A-4 [blocking → resolved]** Writing the maze rather than forking Pyison. See ADR-0003: the maze is never demoed, forking an unfamiliar repo was the critic's named time risk, and ~60 lines fully understood beats a dependency for the one component with no judged surface. Pyison credited in the README as the alternative considered.

## 11. Demo script
| t | On screen | Earns |
|---|---|---|
| 0:00 | The claim sentence over the marked record pair. "We help site operators prove two automated clients shared information, without guessing from how alike they look." | theme fit, presentation |
| 0:15 | Mint table: secret → context A, 11:04:12. Sighting table: same secret, context B, 11:08:47. The marker lands in both records. | the product moment |
| 0:40 | **Stop the server.** Run `make verify`. Root matches, "server not contacted". | the wow moment, execution |
| 1:10 | Disable the model, re-run, diff the proof graph: byte-identical. | execution / method |
| 1:30 | The unhappy path: one actor label in the organizers' dump spans 741 IPs, so a sighting is **not** two actors. The tool says so on its own face. | honesty, originality |
| 1:50 | Honesty counters: organic N, seeded 1, human requests in ledger 0. | real results, trust |
