# Submission checklist — everything you need, in order

**Deadline: Monday 5 October 2026, 05:30 IST** (Sun 4 Oct, 17:00 PT).
Submit at <https://swarmchasing.com/> — the entry form is an Airtable form linked
from the site. Decisions roughly a week later.

---

## 1. What the organizers actually require

Verbatim from <https://swarmchasing.com/logistics/>:

| # | Required? | Item | Status |
|---|---|---|---|
| 1 | **required** | "A short write-up or video explaining your project" | **done** — `SUBMISSION.md`; video script ready if you want both |
| 2 | **required** | "A link to a GitHub repo with your code" | **done** — https://github.com/itssaharsh/canary-maze (public) |
| 3 | **required** | "The names and emails of everyone on your team" | **you** — see §3 |
| 4 | *optional* | "a write-up of real results" | **done** — the highest-leverage optional field at this event |

Item 4 is optional on paper and the single best thing in this entry. The hosts
wrote *"We have more data than we can possibly process ourselves though."* We ran
their corpus and returned a finding. **Do not skip that field.**

---

## 2. Paste these, in this order

### Project name
```
Canary Maze
```

### One-line description
```
Prove a secret moved between two automated clients, and hand someone a record that verifies with your server switched off.
```

### GitHub repo
```
https://github.com/itssaharsh/canary-maze
```

### Live links (if there is a field; otherwise they are in the write-up)
```
Live site:     https://site-nine-hazel-35.vercel.app
Live evidence: https://site-nine-hazel-35.vercel.app/viewer/
Canary surface: https://site-nine-hazel-35.vercel.app/m/q3-supplier-review
```

### Write-up
Paste the contents of **`SUBMISSION.md`**. If the field is short, paste §"The gap"
and §"What it refuses to claim", and link the repo for the rest.

### Real results (the optional field — fill it)

Paste this:

```
Four results, each reproducible from the repo.

1. ON YOUR OWN CORPUS. Your tables carry no address or request header, so they
   cannot say how many request contexts an agent presents to a website. They do
   carry every command the agents ran. Across 2,019,963 turn rows:

   - 40 of 46 agents fetched with more than one client program, and 29 fetched the
     SAME url with both a browser and a command-line client (566 of those pairs
     inside a single session). In the other direction, 29 different agents presented
     one identical user-agent string: contexts collide as well as multiply.
   - "Two contexts, one agent" is a property of the definition, not of the agents:
     58% when a context is a session, 7% when it is the agent's client program -
     a factor of eight - and 34% vs 62% either side of your 2026-03-24
     scaffold change. That dependence is the clearest argument we have for why the
     tool reports contexts and stops.
   - For the 1,054 URLs that cannot be guessed (a token in the path; API endpoints
     and the shared ai-village-agents namespace excluded) there were 410 first
     fetches by a different agent, and 92% were preceded by a visible chat post
     or broadcast within 7 days; 4% had nothing in the tables we read. The control
     is what makes that readable: the same test applied where no hand-off is needed
     (an agent re-fetching its own URL later) fires for only 36%.

   Reproduce: python3 scripts/village_reuse.py   (~5 min, HF_TOKEN + dataset access)
   Output: docs/village_reuse.json

   A visible channel shows a channel existed, not that it was used. "Not found"
   means not in the tables we read - prompts, shared documents, email and link
   clicks are not in them.

2. ON THE COLLUSION.WIKI DUMP (public, ungated). 1,752 of the 1,768 named
   agent labels with two or more revisions wrote from more than one address, and
   1,740 from more than one /16 network - each of which our tool would
   necessarily have seen as more than one context. Median 4 addresses.
   Reproduce: python3 scripts/label_spread.py   (no credentials)

3. ON THE INFRASTRUCTURE, which we did not go looking for. A public model product
   asked to read one of our canary URLs returned 403, and the request never reached
   us. Measured, same URL, same second, varying only the user-agent: GPTBot,
   ClaudeBot, PerplexityBot, CCBot and Bytespider were refused at the Cloudflare
   edge; ChatGPT-User, OAI-SearchBot, Googlebot and curl passed. Five of ten. The
   same edge served its own 3871-byte robots.txt in place of our 66-byte
   "Allow: /", so we could not publish the permission the experiment depends on.

   This generalises, and it is the result we would most want you to have: a zero
   in any crawler-behaviour measurement taken from behind a CDN may be a property
   of the host rather than the clients, and the bias runs toward the null with no
   log line at the origin. docs/memory/failures/F-0005.

4. ON LIVE THIRD-PARTY FETCHERS. Twelve public fetch services were each handed one
   canary URL. Three reached the surface and were recorded through the real
   serverless function and signed hand-off; five arrived with a full browser header
   set, so the human-exclusion gate declined to record them and stored nothing -
   the gate's stated cost, shown rather than described. Every one of those URLs was
   handed over by us, and the act of handing it over is itself a ledger row written
   first, so all of them are reported as paste-triggered and none is counted as
   organic.

   ORGANIC SIGHTINGS: 0. Reported as 0.

WITHDRAWN, and recorded as withdrawn rather than quietly dropped: an earlier
version of this entry cited "one actor label carries 899 revisions across 741
distinct addresses" (that row's label is the empty string - every unlabelled
revision pooled) and reported 78,362 of your computer-use sessions as "46 of 46
agents present more than one session context ... wrong by three orders of
magnitude" (the counts were right; a session is a ~40-action window your scaffold
cuts on the agent's one machine, so the inference was not). Both were on the
product's own face until independent review found them.

Data use: AI Village / AI Digest, research and analysis only, no training or
fine-tuning, no attempt to re-identify anyone. URL keys and user-agent strings are
hashed in memory with a per-run key and never written; output is counts and
quantiles only. Happy to share the write-up with you.
```

### Team names and emails
```
Saharsh — saharsh7002@gmail.com
```
*(Solo entry. Confirm this is the address you want on the submission.)*

---

## 3. The only things left that need you

1. **Your name and email** in the form — the one required field I cannot fill.
2. **Submit it.** I have not submitted anything on your behalf.
3. *Optional:* record the 2-minute video using `docs/DEMO-SCRIPT.md`. The write-up
   satisfies the requirement on its own, so this is upside, not a blocker. The
   organizers say "write-up **or** video"; shipping both covers whichever the
   reader prefers.
4. **Keep the laptop awake** until you submit. The public surface is on Vercel and
   survives sleep, but the ledger is local — a crawler arriving while the machine
   is off is served and not recorded.

---

## 4. Pre-flight — run this before you submit

```
pip install -r requirements.txt    # one dependency: Flask
make demo                          # builds the offline viewer
make verify                        # five properties, each able to fail
python3 -m pytest -q
```

All four were run in a fresh clone of the public repo before this was written.
`make verify` passes on a clone with no ledgers; the test suite modifies no
tracked file.

And click these:

- <https://github.com/itssaharsh/canary-maze> — loads, public
- <https://site-nine-hazel-35.vercel.app/viewer/> — press *Recompute the hashes locally*; expect "Verified. The server was not contacted."
- <https://site-nine-hazel-35.vercel.app/m/q3-supplier-review> — a crawler-shaped request gets a canary link; a browser gets the same page without one

## 5. If a judge asks "what's real?"

Have this ready; it is the first Q&A question at every event.

| Claim | Status |
|---|---|
| The gate, mint, detector, bundle and the signed edge hand-off | **real**, running, 235 tests |
| Offline verification in the browser | **real** — every hash recomputed with `crypto.subtle`, zero network requests, and what the page *displays* is bound to the Merkle root, not just what it hashes |
| The seeded two-client replay | **real code, synthetic traffic** — labelled "seeded" in the claim sentence itself, never counted as organic |
| Third-party fetchers on the live surface | **real** — three recorded, five turned away by the gate. Every one was handed its URL by us, so all are paste-triggered |
| Organic sightings | **zero**, stated as zero, and structurally unable to be inflated: organic needs a third party on *both* sides of a sighting |
| The corpus results | **real**, on your data and on the public collusion.wiki dump, reproducible by the two named scripts |
| The CDN edge measurement | **real**, measured directly; the host it describes has since been replaced |
| Semantic matching of paraphrased tokens | **never built**. The `laundered` table exists and is provably unable to change a bundle by a byte; no model is called anywhere |

Nothing in the entry is mocked. The one simulated thing — seeded traffic — says so
in the product's own headline sentence.

## 6. If a judge asks "what went wrong?"

Worth having ready, because the answer is the strongest thing about the entry.
Seven independent reviewers read the repo, and every finding was adversarially
re-verified before it was fixed. Twenty-five were confirmed, including:

- the page displayed one object and verified another, so editing the organic
  counter a reader *sees* still printed "Verified";
- four inputs on which the Python and JavaScript verifiers disagreed, one of them
  plantable by any client with a single request;
- "append-only, enforced by triggers" was enforced against UPDATE and DELETE but
  not `INSERT OR REPLACE`, so any row could be rewritten under its own id;
- the shared database connection was built once per concurrent request, and a
  refused write wedged it while the surface kept answering 200;
- two headline measurements in the write-up did not support their conclusions.

All fixed, each with a test that fails without the fix. The failures are in
`docs/memory/failures/` with the reasoning, including the three I caused myself —
the one that keeps recurring is that **a control which depends on remembering is
not a control**, and it took four rounds to make it structural.
