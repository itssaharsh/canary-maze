# Delivery — Canary Maze

mode: hackathon · channel: direct · delivered: 2026-10-03
Deadline: Sun 2026-10-04 17:00 PT. Build complete; the write-up and video remain.

## What was built

A canary surface that lets a site operator show a third party that a secret issued
to one automated request context was later fetched by a **different** one — and
hand over a record that verifies with the server switched off.

It deliberately does **not** claim the two contexts are two operators. That claim
is unprovable from this data, and the schema has no `actor` entity so it cannot be
made by accident (ADR-0002).

## Live

| What | Where | State |
|---|---|---|
| Landing page | https://site-nine-hazel-35.vercel.app | 200, 0 axe violations |
| Evidence viewer | https://site-nine-hazel-35.vercel.app/viewer/ | 200, makes zero external requests |
| Canary surface | **https://site-nine-hazel-35.vercel.app/m/<slug>** | reachable by every crawler; ledger local via signed hand-off |
| Repo | **https://github.com/itssaharsh/canary-maze** (public) | fresh clone passes make verify + make demo |

The canary surface is a tunnel to this machine rather than a host, because the
ledger must be the same file the bundle was built from (ADR-0005). The cost is
that it is only reachable while the process runs. It does not survive sleep.

## Real results

**On the organizers' own corpus** (`aidigestorg/ai-village`): across
78,362 computer-use sessions, **46 of
46** agents present more than one session context; the busiest presents
**7,465**, median 1,080. This is the
second independent corpus supporting "a context is not an actor" - the first was
the collusion.wiki dump, where one actor label spans 741 addresses. An
identity-per-context assumption would have been wrong by three orders of
magnitude on the hosts' own data. `scripts/village_spread.py`,
`docs/village_spread.json`.

**On the infrastructure** (F-0005): of ten crawler user-agents sent to the live
URL, five - GPTBot, ClaudeBot, PerplexityBot, CCBot, Bytespider - were refused at
the Cloudflare edge and never reached the application, while the same edge
replaced our 66-byte `Allow: /` robots.txt with 3871 bytes of its own policy. A
zero organic result in this kind of measurement may be a property of the host
rather than the clients, and the bias runs toward the null with no log line at
the origin. Fixed by moving the public surface to Vercel, which refuses none of
them, keeping the ledger local behind a signed hand-off (ADR-0006).

**Organic sightings: 0**, reported as-is.

## Deliverables

| Item | Where |
|---|---|
| Write-up | `SUBMISSION.md` |
| Demo video shooting script | `docs/DEMO-SCRIPT.md` |
| Public repo | https://github.com/itssaharsh/canary-maze |
| Live surfaces | landing, viewer, canary - all on Vercel |
| Results | `docs/RESULTS.md`, generated from the ledgers, gated by `make verify` |

## Acceptance criteria

| AC | Claim | Check | Result |
|---|---|---|---|
| AC-1 | browser headers → no mint, no ledger row | `pytest tests/test_gate.py` + live HTTP | pass (verified live, twice) |
| AC-2 | same context, same path, one epoch → one mint | `pytest tests/test_mint.py` | pass |
| AC-3 | minting context re-fetches → 200, no sighting | `pytest tests/test_detect.py` | pass |
| AC-4 | different context fetches → 200, one sighting, both raw rows | `pytest tests/test_detect.py` | pass |
| AC-5 | any altered byte → verification fails and names the row | `pytest tests/test_bundle.py` | pass |
| AC-6 | verifier makes no network call, needs no server | `make verify`, server stopped | pass |
| AC-7 | laundered rows cannot change the bundle | `make verify` check 5 | pass, byte-identical |
| AC-8 | viewer separates organic / seeded / paste counts | `make demo` + `viewer/data.json` | pass, plus a self-test column |
| AC-9 | clean checkout, no network → viewer builds and prints PASS | `make demo` | pass |

235 tests. `make verify` PASS. Run three times with a reset between.

## What the numbers actually say

`docs/RESULTS.md` is generated from the ledgers by `scripts/build_results.py`;
`make verify` fails if it has drifted.

- **Organic sightings: 0.** No third-party traffic has reached the surface.
- Seeded sightings: 1 — the mechanism, end to end, through the real gate, mint
  and detector.
- Humans turned away by the gate: counted; humans stored: **0**, by construction.

The seeded replay proves the mechanism. It does not prove that clients in the
wild share URLs. Those are different claims and nothing here merges them.

## The six blocking findings, and what each cost

A fresh reviewer found six. All were reproduced before being fixed.

| # | Finding | Fix |
|---|---|---|
| B1 | the viewer's verify button computed nothing while claiming it did | `viewer/verify.js` recomputes every hash with `crypto.subtle` (F-0003) |
| B2 | `/export.json` published the live secret, so any reader could manufacture a sighting | `secret_prefix` only; raw lines redacted |
| B3 | one SQLite connection across Flask threads → 500s on the canary route | `check_same_thread=False` + a lock on every read and write |
| B4 | three distinct tamperings still verified | header leaf, domain-separated and length-bound Merkle, referential + causal checks |
| B5 | a UA claiming Googlebot beat real browser headers | shape beats declaration; rule order inverted |
| B6 | the human-exclusion counter could not rise | `note_gate_rejection()`, and it is now the one falsifiable privacy number |

A seventh, found during live verification after the review: **a verification
`curl` was recorded as an organic sighting**, because `origin` was one
process-wide value. Fixed by resolving origin per request behind a secret token,
counted separately, disclosed in the headline, and recorded as F-0004. The
polluted ledger was retired rather than edited — it is append-only, and that is
the integrity claim.

## Known limitations (not defects — design decisions)

Three were deliberately not fixed, and are in `README.md#Limitations` instead:

1. The Merkle root is neither published nor signed anywhere the operator does not
   control, so the bundle proves *nothing has been edited since it was built*, not
   that it was built honestly.
2. A client can manufacture a second context against itself by varying header
   order. The viewer's diff makes it visible; nothing refuses the record.
3. No third-party traffic has been observed, so there is no organic result.

Each needs a design decision, not a patch, and saying so is cheaper than a fix
that would look like evidence without being any.

## What remains

| Item | Owner | Why |
|---|---|---|
| Paste a canary URL into a public model product | **Saharsh** | only a human can do it; `scripts/trigger_paste.py <url>` then `--report`. The script now loads `.env` itself and reports which ledger it read. |
| Write-up and demo video | `product-demo-video`, after this | the product is finished first |
| Keep the surface up | the machine must stay awake | the tunnel dies with it; the ledger is a file and survives |

## How a judge checks this in three commands

```
make verify      # five properties, each able to fail, no network
make demo        # builds the viewer offline
```

Then open `viewer/index.html` from disk and press **Recompute the hashes locally**.
Edit any record in `data.js` first, and it names the row that no longer matches.
