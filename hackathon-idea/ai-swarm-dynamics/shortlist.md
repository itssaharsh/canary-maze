# Stage 5 — shortlist decisions (a cut, not a ranking)

D returned 8 surviving solutions across 5 kept problems. Rule applied: shortlist at most two
per problem; the FINAL set keeps exactly one per problem, with the strong alternative mentioned
inside that idea's card.

## Shortlisted for a competitor scan (4)
| Solution | Problem | Why it is in |
|---|---|---|
| S2-A Non-existent source sweep | P2 wiki patroller | Validated problem; the German Wiki incident is one of the two incidents named in the event theme; runs on an UNGATED 4.2 MB dump with 14,591 full-text revisions and 3,103 account labels; the deterministic core (does this source exist?) costs almost no inference |
| S4-B Canary Maze | P4 site operator | Most distinctive mechanism in the pool — manufactures the evidence instead of inferring it; false-positive rate bounded by HMAC collision rather than classifier precision; the proof path needs no model at all |
| S4-A Swarm Ledger | P4 site operator | Strongest-evidenced problem in the pool (5 independent orgs); answers the operator's literal question; but sits in the best-funded adjacent field and maps to the organizers' suggestion #1 |
| S1-A Batch card | P1 OSS maintainer | Strongest single evidence item in the pool (curl, primary, with numbers); writes into a real system of record; refuses to judge authorship by design |

## Shortlist kills (logged, not shown as ideas)
| Solution | Stage | Reason |
|---|---|---|
| S3-A Cohort console | shortlist | Weakest theme fit for THIS event. Its evidence is 2024-dated and, by D's own note, "these issues predate the agent era... the wave problem is older than agent swarms". `why_now.kind: none`. A signup-spam wave is not demonstrably a coordinated AI agent swarm, so it risks `wrong_brief` against a theme about agent swarms. A good product at the wrong event. |
| S9-A Participation receipts | shortlist | The market rests on ONE opened evidence item (P9 is a hypothesis). Retained inside S4-B's card as the demo venue, which is what D recommended, rather than shown as its own idea. |
| S1-B Reciprocal evidence exchange | shortlist | `thin` by D's own Stage 4b verdict — a dependent second surface with nothing to publish without S1-A. Retained as S1-A's expansion. |
| S2-B Fabrication registry | shortlist | `thin` — dependent second surface of S2-A. Retained as S2-A's expansion. |

## Constraint carried forward
Only ONE of S4-A / S4-B can reach the final set, because both come from P4 and share the site-operator
user. The decision rests on the competitor scans, the Stage 6H feasibility cut for a solo online builder
with ~20 hours and no compute reimbursement, and the Stage 6W verdict — not on which pitch sounds better.

---
# The P4 decision, after the competitor scans (both ideas came from one problem; only one can be shown)

**Kept: S4-B Canary Maze. Killed: S4-A Swarm Ledger (stage `competition`).**

Not a judgement about which pitch reads better. The scans separated them on facts:

| | S4-A Swarm Ledger | S4-B Canary Maze |
|---|---|---|
| Mechanism novelty | **Gone.** PayPal US12034731B2 (filed 2021-01-29, granted 2024-07-09) claims grouping log entries and assigning "a corresponding common actor identifier" persisting "over the last 12 months". WebDecoy markets "JA4 as a correlation key inside a persistent actor identity" and "fingerprints identify software. Actors identify attackers." A stub repo (`mshaheerjunaid/Panopticon`, 1 star, 2026-08-11) already describes "clustering on behaviour and JA4 TLS fingerprint instead of IP". | **Intact.** The "do not fork" bucket came back EMPTY — no opened repo mints per-visitor tokens AND tracks propagation between clients. |
| Its own core claim | D's insight sentence "nobody answers 'are these 9,000 requests one actor'" is **falsifiable in one search**. Must be deleted, not softened. | Each wedge prong is quoted from a competitor's own page. |
| Real data for the demo | **Blocked.** The one real recent CC-BY log set (Zenodo 18895701, 178,939 requests, Dec 2025) pseudonymises IPs *and* User-Agents, killing ASN, JA4, HTTP/2 SETTINGS and header order. The "spoofed the UA but JA4 matched" moment cannot be shown on real public data. | **Available within hours.** A documented new-domain deployment logged "Within minutes of deploying, GPTBot started crawling", found via XML sitemap; first 12 hours GPTBot 29,000+ requests, Googlebot 11, ChatGPT-User 1 — both ends of a crawler -> user-agent handoff inside 12 hours. |
| Residual wedge | Segment (self-hosted/non-CDN, independently validated by Logrip arXiv 2508.03130) plus operator-facing artifacts. Real, but narrower than claimed. | Manufactures the evidence instead of inferring it; false-positive bound is HMAC collision, not classifier precision; verbatim proof path needs no model at all. |

S4-A is mentioned inside S4-B's card as the strong alternative for the same problem, per the one-idea-per-problem rule.

## FINAL SET (3 ideas, one per problem)
1. **S4-B Canary Maze** (P4 site operator)
2. **S2-A Non-existent source sweep** (P2 wiki patroller)
3. **S1-A Batch card** (P1 OSS maintainer)
