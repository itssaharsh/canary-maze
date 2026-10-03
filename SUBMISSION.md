# Canary Maze

**Prove a secret moved between two automated clients — and hand someone a record
that verifies with your server switched off.**

AI Swarm Dynamics Hackathon · AI Village × Grove Research
Repo: <https://github.com/itssaharsh/canary-maze> · Live: <https://site-nine-hazel-35.vercel.app>

---

## The gap

The organizers' own post names the bottleneck: *"We have more data than we can
possibly process ourselves though."* Two of their suggested directions are
tracing how information spreads within a group, and going beyond transcripts
using the web and digital forensics.

Everything that exists for this works from the **inside** — you instrument agents
you control, or you compare clients and guess from how alike they look. A site
operator watching unfamiliar automated traffic has neither option. They can say
"these two clients look similar." They cannot show anyone *why*.

Canary Maze changes what the operator is holding. Instead of a resemblance
argument, they hold a dated record that **one specific secret, issued to one
request context, was later fetched by a different one** — and a file that a
skeptic can verify without trusting them and without the server running.

## How it works

1. An automated client requests a page. A human-exclusion gate runs first: a
   browser is served the same page, is **never minted for, and never enters the
   ledger**. Only a counter moves.
2. The client is issued a secret unique to its request context:
   `secret = HMAC(salt, path | context)`. The page embeds that secret's URL.
3. That URL returns **200 for everybody**. A 404 for the second context would end
   the observation before it starts.
4. When a *different* context fetches it, a sighting is written — both raw request
   rows, the elapsed time, the two contexts.
5. The operator exports a bundle. A third party recomputes every hash and the
   Merkle root **offline**, in their own browser, and the page names the row that
   fails if a byte was altered.

The ledger is append-only: `UPDATE` and `DELETE` abort at the database. A record
you can quietly revise is not a record.

## What it refuses to claim

**A sighting is not two actors.** The schema has no `actor` entity, so the claim
cannot be made by accident, and the viewer says "context A" and "context B".

That restraint is not modesty, it is measurement. We checked whether one actor
really does present as many contexts, in two unrelated corpora:

| Corpus | Result |
|---|---|
| **AI Village agent logs** (the organizers' own) | Across **78,362** computer-use sessions, **46 of 46** agents present more than one session context. The busiest presents **7,465**. Median 1,080. |
| collusion.wiki dump | One actor label carries 899 revisions across **741** distinct addresses. |

An identity-per-context assumption would have been wrong by three orders of
magnitude on the hosts' own data. Reproduce: `python3 scripts/village_spread.py`
(needs `HF_TOKEN` and dataset access); full output in `docs/village_spread.json`.

*Data: AI Village / AI Digest, used for research and analysis only, with no
attempt to re-identify anyone. The script reads no identifier, goal or message
content — only counts and the model names the dataset already publishes.*

## A second real result, which we did not go looking for

We deployed the surface and a public model product was asked to read a canary
URL. It reported **403 Forbidden**. Our canary route returns 200 unconditionally,
so the request had never arrived.

The CDN was refusing it. Measured directly, same URL, same second, varying only
the user-agent:

| Refused at the edge | Passed through |
|---|---|
| GPTBot · ClaudeBot · PerplexityBot · CCBot · Bytespider | ChatGPT-User · OAI-SearchBot · Googlebot · Google-Extended · curl |

**Five of ten never reached the application.** The same layer also replaced our
`robots.txt` — ours is 66 bytes and says `Allow: /`; what crawlers received was
3871 bytes of the CDN's own policy. The operator could not publish the permission
their own experiment depended on.

This matters beyond our deployment. **A zero result in this kind of measurement
may be a property of the host, not of the clients** — and the bias runs toward
the null, invisibly, with no log line at the origin. Anyone measuring crawler
behaviour from behind a CDN should check what their edge admits before reporting
what arrived. Written up as `docs/memory/failures/F-0005`.

We fixed it by moving the public surface to a host that refuses nobody, keeping
the ledger local and joining them with a signed hand-off (`ADR-0006`). Every row
records **which edge reported it**, so a reader can weigh an observed request
differently from a reported one.

## What a judge can check in three commands

No credentials. No dataset access. No network.

```
git clone https://github.com/itssaharsh/canary-maze && cd canary-maze
make verify     # five properties, each able to fail, server stopped
make demo       # builds the viewer offline
```

Then open `viewer/index.html` **from disk** and press *Recompute the hashes
locally*. It recomputes every hash with `crypto.subtle` and contacts nothing —
confirmed in a browser with the network panel open. Edit any record in
`data.js` first and it names the row that no longer matches.

`make verify` asserts five things that can each fail: a sighting count that moves
0 → 1, a browser turned away with nothing stored, the bundle verifying offline,
an edited row being caught **and named**, and the disabled semantic-matching
table being unable to change the bundle by a single byte.

143 tests.

## Limitations, in full

1. **A sighting is not two actors** — measured above, stated on the tool's own face.
2. **Two clients can touch the same secret without having talked.** One may have
   followed the other through the same link graph. The bundle records a shared
   artifact, not intent.
3. **Tokens can be stripped.** A public tool with 150 stars detects canary tokens
   "without triggering alerts". A motivated client defeats this.
4. **The context identifier is an assumption, not a measurement.** It assumes a
   client does not vary its user-agent, network and header order between fetches.
5. **"Without trusting us" is narrower than it sounds.** The bundle proves nothing
   has been edited since it was built. It does not prove it was built honestly.
   Publishing or signing the root somewhere we do not control would close that;
   this build does not.
6. **A client can manufacture a second context against itself** by varying header
   order. The viewer's diff makes it visible; nothing refuses the record.
7. **Organic sightings stand at 0**, reported as-is — and partly a measurement of
   the host, per the finding above.

## On honesty as a build constraint

The ledger distinguishes our own traffic from everyone else's, because it has to.
Three times during the build, a verification `curl` was written as an *organic
sighting* and nearly published as third-party evidence. The fix that held was not
a reminder — it was recognising the operator's own network with no cooperation
from the client, since an opt-in control gets forgotten exactly when you are busy.
Two ledgers were retired rather than edited, with written reasons, because an
append-only ledger you correct is not append-only.

Those episodes are in the repo as `F-0004` and `F-0005`, not hidden. A tool whose
entire claim is "you do not have to trust me" cannot quietly fix its own numbers.

---

Built solo, online, in the event window. AI assistance was used throughout; see
`AGENTS.md`.
