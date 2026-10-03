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
Two measurements, both reproducible from the repo.

1. On your own corpus (aidigestorg/ai-village). Across 78,362 computer-use
   sessions, 46 of 46 agents present more than one session context. The busiest
   presents 7,465; median 1,080. This is why the tool says "context" and never
   "actor": an identity-per-context assumption would have been wrong by three
   orders of magnitude on your data. A second, unrelated corpus agrees - in the
   collusion.wiki dump one actor label spans 741 addresses.
   Reproduce: python3 scripts/village_spread.py  (needs HF_TOKEN + dataset access)
   Output: docs/village_spread.json

2. On the infrastructure, which we did not go looking for. A public model product
   asked to read one of our canary URLs returned 403. Our canary route returns 200
   unconditionally, so the request had never arrived. Measured directly, same URL,
   same second, varying only the user-agent: GPTBot, ClaudeBot, PerplexityBot,
   CCBot and Bytespider were refused at the CDN edge and never reached the
   application; ChatGPT-User, OAI-SearchBot, Googlebot, Google-Extended and curl
   passed. Five of ten. The same edge replaced our 66-byte "Allow: /" robots.txt
   with 3871 bytes of its own policy, so we could not publish the permission our
   own experiment depended on.

   This generalises: a zero result in any crawler-behaviour measurement taken from
   behind a CDN may be a property of the host rather than the clients, and the bias
   runs toward the null with no log line at the origin. Anyone doing this should
   check what their edge admits before reporting what arrived.
   Written up as docs/memory/failures/F-0005.

Organic sightings on our own surface: 0, reported as-is.

Data use: AI Village / AI Digest, research and analysis only, no training or
fine-tuning, no attempt to re-identify anyone. Happy to share any resulting
write-up with you.
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
make verify          # expect: PASS, five checks
python3 -m pytest -q # expect: 224 passed
```

And click these:

- <https://github.com/itssaharsh/canary-maze> — loads, public
- <https://site-nine-hazel-35.vercel.app/viewer/> — press *Recompute the hashes locally*, expect "Verified. The server was not contacted."
- <https://site-nine-hazel-35.vercel.app/m/q3-supplier-review> — loads

---

## 5. If a judge asks "what's real?"

Have this ready; it is the first Q&A question at every event.

| Claim | Status |
|---|---|
| The gate, mint, detector and bundle | **real**, running, 224 tests |
| Offline verification in the browser | **real** — recomputed with `crypto.subtle`, zero network requests, confirmed with the panel open |
| The seeded two-client replay | **real code, synthetic traffic** — labelled "seeded" on its own face, never counted as organic |
| The 78,362-session corpus result | **real**, on their data, reproducible |
| The CDN edge measurement | **real**, measured directly |
| Organic sightings | **zero**, stated as zero |
| Semantic matching of paraphrased tokens | **ships disabled**, in a separate table, provably cannot change the bundle by a byte |

Nothing in the entry is mocked. The one simulated thing — seeded traffic — says so
on screen and is counted in its own column.
