# Architecture — Canary Maze

One deployable, one datastore, no model on the proof path.

```
                   automated client                       a third party
                          │                                    │
                   GET /m/<slug>                        verify-bundle (offline)
                          ▼                                    ▲
  ┌───────────────────────────────────────────┐                │
  │  app.py (Flask)                           │                │
  │    gate.is_automated ──no──▶ plain page, no row            │
  │           │yes                            │                │
  │    context.derive ──▶ ctx_id              │          bundle.verify
  │           │                               │                │
  │    mint.secret_for(path, ctx) ─ HMAC ─────┼──▶ ledger.sqlite3 ──▶ bundle.json
  │    maze.page(slug, canary_url)            │        ▲   ▲        (Merkle root)
  │                                           │        │   │
  │  GET /c/<secret>/<slug>  → ALWAYS 200 ────┼────────┘   │
  │    detect.sighting(secret, ctx) ──────────┼────────────┘
  │                                           │
  │  GET /  → viewer (static) ◀── export.json │
  └───────────────────────────────────────────┘
```

| Component | The requirement that forces it |
|---|---|
| `gate.py` | AC-1 and the privacy constraint. Without it this is a visitor-tracking tool. |
| `context.py` | J1/J2 need a context identifier that is stable without being an identity claim. |
| `mint.py` | J1. HMAC keyed by a rotating salt; the salt epoch is stored so old secrets still verify. |
| `ledger.py` | J1–J3. Append-only SQLite; the only writer. |
| `detect.py` | AC-3/AC-4. The one branching function a judge will probe hardest. |
| `bundle.py` | J3, AC-5/AC-6. The deliverable that outlives the server. |
| `figure.py` | The viewer's figure, rendered server-side so the viewer stays a static file. |
| `maze.py` | The surface an automated client must reach to be minted for. Plumbing; never demoed. |
| `app.py` | Routing only. |

**Not present, deliberately:** no queue, no cache, no second datastore, no ORM, no auth, no user accounts, no actor table, no background jobs, no model on the proof path.

## Decisions

**ADR-0001 — SQLite, append-only, one file.** One deployable with zero ops, and the durable artifact is the *bundle*, not the database. Postgres would add a service for no gain: nothing here is concurrent beyond one process, and the record a third party checks is a file.

**ADR-0002 — No model on the proof path.** A verbatim sighting is a table lookup. Laundered (paraphrased) token matching is the only place a model could help, and it ships **disabled** in a separate table that is never joined into the proof graph, so a judge can switch the model off and diff the graph to byte-identical. Also removes the inference bill, which matters because this entrant gets no compute reimbursement.

**ADR-0003 — Write the maze; do not fork Pyison.** The brief said to fork [Pyison](https://github.com/JonasLong/Pyison) (MIT) for the serving layer. Reversed, deliberately: the maze is the one component that is *never demoed*, the critic pass named "forking an unfamiliar 125-star repo" as the single most likely way to lose Saturday, and the maze we need is ~60 lines fully understood. Pyison is credited in the README as the alternative considered. **This is a documented deviation from the build brief, not an oversight.**

**ADR-0004 — There is no actor entity.** The schema has `request`, `mint`, `sighting` and a context identifier. It has no `actor` table and no join that would produce one, because one actor label in the organizers' own dump spans 741 distinct addresses. The product's claim is bounded by its data model, not by a disclaimer in the copy.

**ADR-0005 — Merkle root over canonicalized rows.** Rows are serialized with sorted keys and no whitespace, SHA-256 leaf-hashed, and combined into a root. A verifier needs the file and nothing else: no server, no network, no trust in the operator. This is the whole wedge, so it is the one place worth the extra 40 lines.

## Review gate

| Question | Answer |
|---|---|
| Necessity | Every component above maps to an acceptance criterion. |
| Simplest viable | One process, one file, stdlib + Flask. |
| Dependency fails | Model: absent by default, proof path unaffected. SQLite locked: retry once, then serve the page *without* minting — never block a crawler, because a blocked crawler is a lost sighting. |
| Data grows | The canary URL space is unbounded by design; rows are small. Bundle export paginates by salt epoch if it ever needs to. |
| State and secrets | The HMAC salt is the only secret. Env var, never committed, rotated daily, epoch stored per mint so rotation never invalidates history. |
| Observability | Structured request log with a request id; the ledger *is* the audit trail. |
| What can be cut | Laundered matching (already disabled), the figure (could be a table), multi-site federation (out). |
| Fresh architect reviewer needed? | No: no money, no auth, no personal data beyond /24-truncated IPs, no data-loss risk. Threshold not met. |
