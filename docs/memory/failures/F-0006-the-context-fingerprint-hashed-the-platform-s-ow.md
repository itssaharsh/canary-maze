---
id: F-0006
type: failure
title: the context fingerprint hashed the platform's own headers, so a client following its own link was a sighting
status: active
scope: global-candidate
components: canarymaze/context.py, site/api/surface.py, tests/test_surface.py, tests/test_context.py
triggers: moving a service behind any proxy, CDN or serverless platform; fingerprinting a request; adding a header-derived identifier
evidence: live probe 2026-10-03 against the Vercel surface; tests/test_surface.py::test_a_client_following_its_own_link_is_not_a_sighting
verified_at: 2026-10-03
relates: F-0004, F-0005, ADR-0002, ADR-0006
supersedes: 
helpful: 0
harmful: 0
cite_hash: 
created: 2026-10-03
source: self-tested while briefing a security reviewer on what to look for
---

ATTEMPTED: move the public surface to Vercel (ADR-0006) so the crawlers the
Cloudflare edge refused could reach it, keeping the context derivation exactly as
it was - user-agent, truncated network, Accept, Accept-Encoding and "the ORDER of
the header names, which is a property of the HTTP stack".

ERROR SIGNATURE: none. Every unit test passed, because every unit test handed
`derive()` the same headers dict twice. The live surface minted and recorded
happily. The defect only showed when ONE client, with ONE user-agent, fetched a
maze page and then followed its own canary link, seconds apart: the ledger wrote a
sighting. Two different context ids for the same client on the two routes.

ROOT CAUSE: the fingerprint hashed the name of every header the function saw,
minus a short denylist of "volatile" ones. Behind a hosting platform the function
does not see the client's headers; it sees the client's headers plus the
platform's (x-vercel-*, x-forwarded-*, x-matched-path, x-now-route-matches ...),
and that injected set is not the same on a one-parameter route as on a
two-parameter route. So the fingerprint was measuring the platform's routing, not
the client. The commonest harmless event there is - a crawler re-reading its own
link, which the detector's own docstring says "proves nothing" - became evidence.
Had a third-party crawler arrived first, it would have been published as an
organic sighting. It was found first only because the question was asked directly.

A denylist was the wrong shape for this from the start: it has to anticipate every
header every intermediary will ever add, and the one it misses splits a client in
two. And the direction of the error is the bad one. A context that is too coarse
loses a sighting; a context that is too fine manufactures one.

FIX: `CLIENT_HEADERS` is an ALLOWLIST of the request headers a client's own HTTP
stack sends; only those take part, and their order is ignored (an intermediary
reordering headers is the next way the same bug would have arrived). Separately,
the edge function now forwards only those headers to the ledger - an earlier
version forwarded everything, cookies and authorization values included, to a
machine with no use for them. `site/api/surface.py` was refactored around a pure
`respond()` so it could be tested at all; it had shipped with no tests. A drift
test asserts the module copies in site/api/_cm/ match their source, so a fix
cannot pass every test while the deployed copy runs the old code. The ledger whose
context ids came from the broken derivation was retired (generation 3 is live).
Verified live: six requests from one client across both routes share one context
id and produce 0 sightings; a second client produces exactly 1. Mutation-checked:
restoring the old behaviour fails 7 tests.

As a side effect the fix narrows a documented limitation: adding an arbitrary
header (`X-Trace: 1`) or reordering headers no longer presents as a second
context. Changing the user-agent still does.

LESSON: an identifier derived from "the request" is derived from the request AS
THE CODE SEES IT, and the moment a proxy sits in front, that is not what the client
sent. Unit tests cannot find this, because the unit under test is fed a dict the
test author wrote; only a request that actually crossed the intermediary carries
the intermediary's fingerprints. When the product's evidence is "these two
requests differ", the first test on any new vantage point is the negative control:
send the SAME client twice and require that nothing is recorded.

CHEAPEST EARLY CHECK: after putting anything in front of a service that
fingerprints requests, fetch two different routes with one client and compare the
derived identifiers. Thirty seconds; it would have caught this before deploy.
