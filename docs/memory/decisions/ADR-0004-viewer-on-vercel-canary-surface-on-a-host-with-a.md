---
id: ADR-0004
type: decision
title: Viewer on Vercel; canary surface on a host with a persistent disk
status: active
scope: project
components: canarymaze/ledger.py, canarymaze/app.py
triggers: deploying, choosing a host, moving to serverless, adding Postgres
evidence: ARCHITECTURE.md#Decisions
verified_at: 2026-10-02@534ff22
relates: 
supersedes: 
helpful: 0
harmful: 0
cite_hash: 41874f6bbd79ea0f
created: 2026-10-02
source: unknown
---

Saharsh asked to deploy the frontend on Vercel. The viewer is static HTML plus a JSON export, so Vercel is a clean fit and gives a free public hostname. The canary SURFACE cannot go there as-is: it writes an append-only SQLite ledger that must survive for hours while crawlers arrive, and Vercel functions have an ephemeral filesystem, so the ledger would be wiped between invocations and no sighting could ever be detected. Chosen: viewer on Vercel, canary surface on a host with a persistent volume (Fly.io/Railway/VPS), SQLite unchanged, zero code change, and make demo keeps running offline byte-identically to what a judge runs. Rejected for now: all-Vercel with a Marketplace Postgres, because porting the schema and ledger on Saturday is the kind of work the critic pass named as the way to lose the build window. Revisit if the project outlives the hackathon.