# Architecture — Canary Maze

Two deployables, one datastore, no model on the proof path. The public surface is a
stdlib-only serverless function on a host that refuses no crawler; the ledger is a
file on the operator's machine. They are joined by an HMAC-signed hand-off, because
the host that can reach the clients is not the host that should hold the evidence
(ADR-0005, ADR-0006, F-0005).

```
      automated client                          a human                   a third party
             │                                     │                            │
             ▼                                     ▼                   verify-bundle (offline)
  ┌──────────────────────────────────────────────────────┐                      ▲
  │  site/api/surface.py   — Vercel, stdlib only          │                      │
  │     gate.is_automated ──no──▶ same page, no secret    │                bundle.verify
  │            │yes                        │              │               (also in the browser,
  │     context.derive ─▶ ctx              │              │                viewer/verify.js)
  │     mint.secret_for(path, ctx) ─ HMAC ─┤              │                      │
  │     serves the page immediately        │              │                      │
  └────────────┬───────────────────────────┴──────────────┘                      │
               │  POST /ingest  — HMAC-signed, timestamped, replay-refused       │
               │  (headers allowlisted; a human reports only THAT it happened)    │
               ▼                                                                 │
  ┌──────────────────────────────────────────────────────┐                       │
  │  app.py (Flask), on the operator's machine           │                       │
  │     gate runs AGAIN, on the forwarded headers        │                       │
  │     refuses a secret or context it derives otherwise │                       │
  │     detect.on_canary_request ─────────┐              │                       │
  │     GET /c/<secret>/<slug> → ALWAYS 200│             │                       │
  └───────────────────────────────────────┼─────────────┘                        │
                                          ▼                                      │
                            ledger.sqlite3 (append-only) ──▶ bundle.json ─────────┘
                              request · mint · sighting · published    (Merkle root, and a
                                          │                             digest of what the
                                          └──▶ export.py ──▶ viewer     page displays)
```

| Component | The requirement that forces it |
|---|---|
| `gate.py` | AC-1 and the privacy constraint. Without it this is a visitor-tracking tool. |
| `context.py` | J1/J2 need a context identifier that is stable without being an identity claim. |
| `mint.py` | J1. HMAC over (salt, path, context, date). The date changes the secret daily; the salt itself is long-lived. The epoch is stored per mint so yesterday's secrets still resolve. |
| `ledger.py` | J1–J3. Append-only SQLite; the only writer. |
| `detect.py` | AC-3/AC-4. The one branching function a judge will probe hardest. |
| `bundle.py` | J3, AC-5/AC-6. The deliverable that outlives the server. |
| `paths.py` | One place decides which ledger is live, and refuses a retired one. Three separate stale defaults had reopened quarantined ledgers (F-0004). |
| `ingest.py` | The signed hand-off, and the replay memory that bounds it. |
| `site/api/surface.py` | The public surface. Imports copies of the modules above, placed by `scripts/build_site.py`; a test fails if a copy drifts from its source. |
| `maze.py` | The surface an automated client must reach to be minted for. Plumbing; never demoed. |
| `app.py` | Routing, the proxy-trust decision, and `/ingest`. |

**Not present, deliberately:** no queue, no cache, no second datastore, no ORM, no user accounts, no actor table, no background jobs, no model on the proof path. The only authentication is between the edge and the ledger; there is no user-facing auth of any kind.

## Decisions

> Numbering note: these are **D1-D5**, local to this file. They are NOT the same
> sequence as `docs/memory/decisions/ADR-*`, which numbers independently and is the
> canonical record. Each entry below cites its ADR where one exists. Three further
> decisions live only in memory: ADR-0004 (viewer on Vercel), ADR-0005 (keep SQLite
> and tunnel the surface) and ADR-0006 (public surface on Vercel, ledger local,
> joined by a signed hand-off).

**D1 — SQLite, append-only, one file.** *(no memory record; architecture-local)* One deployable with zero ops, and the durable artifact is the *bundle*, not the database. Postgres would add a service for no gain: nothing here is concurrent beyond one process, and the record a third party checks is a file.

**D2 — No model on the proof path.** *(canonical record: `docs/memory/decisions/ADR-0001`)* A verbatim sighting is a table lookup. Laundered (paraphrased) token matching is the only place a model could help, and it ships **disabled** in a separate table that is never joined into the proof graph, so a judge can switch the model off and diff the graph to byte-identical. Also removes the inference bill, which matters because this entrant gets no compute reimbursement.

**D3 — Write the maze; do not fork Pyison.** *(canonical record: `docs/memory/decisions/ADR-0003`)* The brief said to fork [Pyison](https://github.com/JonasLong/Pyison) (MIT) for the serving layer. Reversed, deliberately: the maze is the one component that is *never demoed*, the critic pass named "forking an unfamiliar 125-star repo" as the single most likely way to lose Saturday, and the maze we need is ~60 lines fully understood. Pyison is credited in the README as the alternative considered. **This is a documented deviation from the build brief, not an oversight.**

**D4 — There is no actor entity.** *(canonical record: `docs/memory/decisions/ADR-0002`)* The schema has `request`, `mint`, `sighting` and a context identifier. It has no `actor` table and no join that would produce one, because in the organizers' own public dump 1,752 of the 1,768 named agent labels with two or more revisions wrote from more than one address, the busiest from 308 (`scripts/label_spread.py`). The product's claim is bounded by its data model, not by a disclaimer in the copy.

**D5 — Merkle root over canonicalized rows.** *(no memory record; architecture-local)* Rows are serialized with sorted keys and no whitespace, SHA-256 leaf-hashed, and combined into a root. A verifier needs the file and nothing else: no server, no network, no trust in the operator. This is the whole wedge, so it is the one place worth the extra 40 lines.

## Review gate

| Question | Answer |
|---|---|
| Necessity | Every component above maps to an acceptance criterion. |
| Simplest viable | One process, one file, stdlib + Flask. |
| Dependency fails | Model: not integrated at all; the proof path could not reach its output if it were. SQLite locked: retry once, then serve the page *without* minting — never block a crawler, because a blocked crawler is a lost sighting. |
| Data grows | The canary URL space is unbounded by design; rows are small. Bundle export paginates by salt epoch if it ever needs to. |
| State and secrets | **Three** long-lived secrets, all env vars, none committed: `CANARY_SALT` (forges secrets), `CANARY_INGEST_KEY` (writes ledger rows) and `CANARY_SELFTEST_TOKEN` (marks traffic as the operator's). The salt is also held by the edge, which needs it to mint. The *secret* changes daily because the date is an HMAC input; the *salt* does not rotate, so a leak forges every day's secrets, past and future, until it is replaced. Rotating it orphans every secret already issued, which is why nothing rotates it automatically. |
| Observability | Structured request log with a request id; the ledger *is* the audit trail. |
| What can be cut | Laundered matching (already disabled), the figure (could be a table), multi-site federation (out). |
| Fresh architect reviewer needed? | It was run anyway: seven independent reviewers across security, correctness, scripts, documents, the viewer, the tests and a cold-clone judge, each finding adversarially re-verified. 25 findings confirmed. |
