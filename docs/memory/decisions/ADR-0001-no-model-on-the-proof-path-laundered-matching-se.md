---
id: ADR-0001
type: decision
title: No model on the proof path; laundered matching segregated and disabled
status: active
scope: project
components: canarymaze/bundle.py, canarymaze/detect.py
triggers: adding AI to the verification path, inference cost, model availability
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

A verbatim sighting is an HMAC table lookup, so the proof path makes no model call. Laundered (paraphrased) token matching lives in a separate table that is never joined into the proof graph and ships disabled. A judge can switch the model off and diff the proof graph to byte-identical. Also removes the inference bill, which matters because this entrant gets no compute reimbursement.