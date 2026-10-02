---
id: ADR-0005
type: decision
title: Database/host choice: keep SQLite, tunnel the surface; Postgres only if the host changes
status: active
scope: project
components: canarymaze/ledger.py, canarymaze/schema.sql
triggers: deploying, choosing a host, porting to Postgres, Neon, Supabase, serverless
evidence: canarymaze/ledger.py
verified_at: 2026-10-02@efdc3db
relates: 
supersedes: 
helpful: 0
harmful: 0
cite_hash: 46e191f37b83be3a
created: 2026-10-02
source: unknown
---

Saharsh asked for a free tier and named Supabase/Neon. Measured first: there is ZERO raw SQL outside canarymaze/ledger.py and canarymaze/schema.sql - detect.py only catches sqlite3.IntegrityError - so a Postgres port is a contained two-file job, not a rewrite. The decision that actually forces a database is what runs the Flask process, not which Postgres. Recommended: viewer on Vercel (static, free) plus the canary surface exposed via Cloudflare Tunnel from the builder's own machine, because SQLite then stays untouched and  run by a judge is byte-identical to the code path that collected the evidence. A Vercel+Neon split would make the demo run SQLite while production ran Postgres, so a passing demo would stop proving production works - that honesty cost is the reason it was not chosen, not the porting effort. Revisit if the laptop cannot stay awake overnight, or if the project outlives the hackathon; then port ledger.py and schema.sql to Postgres (SERIAL ids, a PL/pgSQL trigger in place of RAISE(ABORT), %s placeholders) and state in the README that tests run SQLite.