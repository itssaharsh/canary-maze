---
id: F-0005
type: failure
title: the edge blocks the traffic the product exists to observe, and replaces our robots.txt
status: active
scope: global-candidate
components: scripts/serve_public.sh, docs/RESULTS.md, README.md
triggers: deploying behind any CDN, choosing a tunnel or host, interpreting a zero organic count
evidence: measured 2026-10-03 against the live quick tunnel
relates: F-0004, ADR-0004, ADR-0005
supersedes: 
helpful: 0
harmful: 0
cite_hash: 
created: 2026-10-03
source: a third party reported 403 when asked to read a canary URL
---

ATTEMPTED: publish a canary URL and have a public model product read it, which is
the whole paste-triggered path. The product replied that the page returned **403
Forbidden**.

ERROR SIGNATURE: nothing in our logs at all. The canary route returns 200 for
every context unconditionally, by design, so a 403 cannot originate in this
codebase. The request never arrived.

ROOT CAUSE: the surface is served through a Cloudflare quick tunnel, and
Cloudflare blocks AI crawlers at its edge by default. Measured directly, same URL,
same second, varying only the user-agent:

    403  GPTBot          403  ClaudeBot       403  PerplexityBot
    403  CCBot           403  Bytespider
    200  ChatGPT-User    200  OAI-SearchBot   200  Googlebot
    200  Google-Extended 200  curl

Five of ten never reached the application. The split is not random: declared
*training* crawlers are refused, while *user-triggered* fetchers and search
crawlers pass. A second, quieter effect compounds it - the edge does not serve our
`robots.txt` at all. Ours is 66 bytes and says `Allow: /`; the edge returns 3871
bytes of Cloudflare's own Content Signals Policy. The operator cannot publish the
permission their own experiment depends on.

This directly violates a written constraint in the implementation contract: "one
small host, stable URL, HTTPS, XML sitemap, **no proof-of-work gate in front of
it** (it would block the traffic we need to observe)". The check was run against
proof-of-work interstitials and passed; nobody checked for user-agent blocking,
which is the same failure wearing different clothes.

FIX: none available at this layer - quick tunnels expose no bot-management
controls, and that is the price of the free tier. What was fixed is the
*reporting*: a zero organic count can no longer be presented as evidence about
crawler behaviour, because it is partly a measurement of the edge. README and
docs/RESULTS.md now state which user-agents were refused and that our robots.txt
never reached a crawler.

LESSON: when the product's measurement IS the traffic, the hosting layer is part
of the instrument, not a deployment detail. A CDN that silently filters inbound
clients does not just reduce the sample - it biases it in exactly the direction
that flatters the null result, and it does so without a log line on the origin.
Before trusting any count of who did or did not arrive, measure what the edge
admits, by sending the user-agents you expect and checking they appear in YOUR
log rather than merely returning 200 to you.

CHEAPEST EARLY CHECK: curl your own public URL with the three user-agents you
most want to observe, and confirm each one shows up in the origin's access log.
Also diff your robots.txt as served locally against the same file fetched through
the public hostname; if the bytes differ, you are not the one setting policy.
