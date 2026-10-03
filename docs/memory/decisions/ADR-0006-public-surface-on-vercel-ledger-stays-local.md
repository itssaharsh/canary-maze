---
id: ADR-0006
type: decision
title: public surface on Vercel, ledger stays local, joined by a signed hand-off
status: active
scope: project
components: site/api/surface.py, canarymaze/ingest.py, canarymaze/app.py
evidence: measured 2026-10-03; tests/test_ingest.py
relates: ADR-0004, ADR-0005, F-0005
created: 2026-10-03
---

## Decision

Serve the public canary surface from Vercel. Keep the ledger on the operator's
machine. Join them with an HMAC-signed, timestamped hand-off, and record on every
row which edge reported it.

## Why

ADR-0005 put the surface on a Cloudflare quick tunnel so the bundle a third party
verifies would be built from the same file that collected the evidence. That still
matters, but it turned out to cost the measurement itself: the Cloudflare edge
returns 403 to GPTBot, ClaudeBot, PerplexityBot, CCBot and Bytespider and never
forwards them, and it replaces our robots.txt with its own (F-0005). The surface
was unreachable by precisely the clients it exists to observe. Vercel refuses none
of them and serves our robots.txt.

Moving the ledger too would have reversed ADR-0005 and needed a hosted database.
Moving only the surface keeps ADR-0005 intact, because the function needs no
database: the secret is a pure HMAC of the salt, the path and the request context,
so Vercel can compute and serve everything, then report.

## What it costs, stated rather than buried

The ledger no longer sees the client; it records what an edge *reported*. That is
one more hop of the kind we already accept in trusting CF-Connecting-IP, but it is
not free:

- Every row carries `via`. 'direct' means this process saw the connection;
  anything else is a report. `counts()` splits them, so a reader can weigh the two
  differently instead of taking the whole ledger on one trust level.
- The hand-off is signed and timestamped. Unsigned, it would let anyone post
  invented rows into an append-only ledger where they could never be removed -
  worse than the problem it solves. Tests attack it first.
- The salt now lives on Vercel as well, so a Vercel compromise could forge
  secrets. Accepted: without it the function cannot mint, and minting from the
  laptop would make every page depend on the laptop being awake.
- The gate runs at the ledger, on the forwarded headers, not at the edge. The
  human-exclusion guarantee is the one thing that must not live on a machine we do
  not control.

## Alternatives rejected

- **Full port to Vercel + Neon.** Survives sleep and gives a stable collector, but
  reverses ADR-0005, rewrites the append-only triggers for Postgres and needs an
  account provisioned the day before the deadline.
- **A different free tunnel.** Would move the problem to another edge whose bot
  policy we also do not control, and would have to be re-measured.
- **Accept the blocking.** Honest, and F-0005 is written up either way - but it
  leaves the product unable to make its own measurement when a working host was
  one deploy away.
