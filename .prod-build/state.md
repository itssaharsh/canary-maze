# state — Canary Maze

phase: M1-M3 complete (build), M4 pending (live + gates)
mode: hackathon · channel: direct · base 81795d7

## Done
- T01 append-only ledger, /24 truncation at the write boundary
- T02 human-exclusion gate + request-context derivation (RED-first)
- T03 HMAC mint with salt epochs, maze surface, always-200 canary route
- T04 sighting detection (same-context and duplicate guards)
- T05 evidence bundle, Merkle root, offline verifier
- T06 seeded two-client replay through the real path, derived viewer export
- T07 viewer: every line computed from the export, context diff, promoted verification
- T08 make demo / make verify, README

88 tests green. `make verify` PASS on all five checks including the
model-enabled-vs-off byte-identical proof graph.

## Not done — these are Saharsh's, Saturday
- T09 domain, DNS, TLS, sitemap, first deploy. NO CODE DEPS. Start 10:00, it is
  the long pole and it is mostly waiting. The organic-sighting clock starts when
  DNS resolves.
- T10 chat-paste trigger + honest organic harvest into docs/RESULTS.md
- T11 merged gate: fresh review + security checklist + demo x3

## Open decisions
- Host: ADR-0005 recommends viewer on Vercel + canary surface via Cloudflare
  Tunnel (SQLite untouched, demo == production). Saharsh has not confirmed.
  Alternative is a Neon/Supabase Postgres port, contained to ledger.py +
  schema.sql, at the cost of demo and production running different backends.

## Next step
Decide the host, then T09. Nothing in the code blocks on it.
