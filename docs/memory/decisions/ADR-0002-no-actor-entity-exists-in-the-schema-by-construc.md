---
id: ADR-0002
type: decision
title: No actor entity exists in the schema, by construction
status: active
scope: project
components: canarymaze/schema.sql, canarymaze/detect.py
triggers: adding an actors table, claiming two contexts are two operators, joining contexts
evidence: ARCHITECTURE.md#Decisions
verified_at: 2026-10-02@81795d7
relates: 
supersedes: 
helpful: 0
harmful: 0
cite_hash: 41874f6bbd79ea0f
created: 2026-10-02
source: unknown
---

The schema has request, mint, sighting and a context identifier. It has no actor table and no join that would produce one, because one actor label in the organizers' own collusion.wiki dump spans 741 distinct addresses (stored_revisions 899 / stored_revision_ips 741). The product's claim is bounded by its data model rather than by a disclaimer in the copy. The earlier framing that false positives were 'bounded by HMAC collision' was FALSE: the HMAC bounds token provenance, not actor distinctness. Never reintroduce it.