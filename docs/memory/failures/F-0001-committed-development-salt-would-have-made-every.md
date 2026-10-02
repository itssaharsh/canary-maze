---
id: F-0001
type: failure
title: Committed development salt would have made every secret forgeable in production
status: active
scope: global-candidate
components: canarymaze/mint.py, canarymaze/app.py
triggers: deploying, setting env vars, removing a startup guard, changing load_salt
evidence: canarymaze/app.py
verified_at: 2026-10-02@3086060
relates: 
supersedes: 
helpful: 0
harmful: 0
cite_hash: 37f0ec81c8be105a
created: 2026-10-02
source: unknown
---

ATTEMPTED: ship mint.load_salt() with a fixed, obviously-named development salt as a fallback, so tests and make demo run on a clean checkout with no setup. ERROR SIGNATURE: no runtime error at all - this fails silently and only in production. ROOT CAUSE: the fallback literal is committed to a PUBLIC repository, and the deploy path had nothing that required CANARY_SALT, so a surface deployed without it would mint under a salt any reader could copy. That makes every secret forgeable and destroys the one property the HMAC genuinely bounds, token provenance, which is the basis of every claim the product makes. FIX: app.require_production_salt() raises SystemExit unless CANARY_SALT is set, called from the server entry point only; the library stays permissive so the offline demo still works with zero setup. Covered by test_the_server_refuses_to_start_on_the_committed_development_salt. LESSON: when a convenience fallback for a SECRET is committed, the guard belongs at the serving entry point, not in the library that provides the fallback, because the library is also what tests and demos call. CHEAPEST EARLY CHECK: grep the repo for the fallback literal and ask 'what happens if this ships unset?'