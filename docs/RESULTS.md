# Results

**Numbers are reported exactly as they stand.** The counts below are generated
from the ledgers by `scripts/build_results.py`; nothing in that table is typed by
hand. `python3 scripts/build_results.py --check` fails if this file has drifted
from the data, which it had done once before the generator existed.

## Live surfaces

| What | Where |
|---|---|
| Landing page | https://site-nine-hazel-35.vercel.app |
| Live evidence viewer | https://site-nine-hazel-35.vercel.app/viewer/ |
| Canary surface | ephemeral per run: `bash scripts/serve_public.sh` prints the hostname |

## Counts

<!-- counts:start -->
| Category | Live public surface | Seeded replay |
|---|---|---|
| **Organic sightings** - a third party fetched a secret nobody handed it | 0 | 0 |
| Paste-triggered sightings - a third party fetched a link the operator published | 3 | 0 |
| Operator self-test sightings | 4 | 0 |
| Seeded-replay sightings | 0 | 1 |
| Requests recorded from third parties | 9 | 0 |
| Requests recorded from the operator's own probes | 54 | 0 |
| Requests recorded in the seeded replay | 0 | 2 |
| Secrets issued to third parties | 0 | 0 |
| Secrets issued to the operator's own probes | 17 | 0 |
| Secrets issued in the seeded replay | 0 | 1 |
| Secrets the operator published by hand | 13 | 0 |
| Browser-shaped requests turned away, nothing stored | 15 | 0 |
| Human requests stored | 0 | 0 |

The two columns are never added together. The left one is what the public surface has recorded; the right one shows the mechanism working on a scripted replay. Nothing in the right column is an observation.

**Organic sightings stand at 0.** No third party has been observed fetching a secret it was not handed. That is reported as-is.

**3 sightings are paste-triggered**: a third-party fetcher followed a link the operator had published first (the census below). They show the surface and the ledger recording real third-party infrastructure. They are not evidence that anyone shares anything with anyone, and they are never counted as organic.

9 requests from third parties and 54 requests from the operator's own probes are recorded. The operator's are labelled as self-tests at the moment they are written (F-0004), so they cannot inflate any third-party number.

15 browser-shaped requests were turned away and nothing about them was stored. That counter moves for anything that arrives with a browser's header set - people, the operator's own browser, and headless-browser fetch services alike. It counts the gate firing, not humans.
<!-- counts:end -->

## Does one actor present as many contexts? Measured

The tool reports that a secret moved between two request CONTEXTS and refuses to
say two contexts are two actors. In the organizers' public collusion.wiki dump:

| | |
|---|---|
| Named agent labels with two or more revisions | **1,768** |
| Of those, from more than one address | **1,752** (99%) |
| Of those, from more than one /16 network | **1,740** (98%) |
| Median per label | 4 addresses, 3 /16 networks |
| Busiest named agent label | 317 revisions from 308 distinct addresses in 96 /16 networks |

`python3 scripts/label_spread.py` (no credentials; the dump is public and its file
hash is pinned in the script). Raw output: `docs/label_spread.json`.

**Withdrawn:** "one actor label carries 899 revisions across 741 distinct
addresses". That row's label is the empty string - every unlabelled revision
pooled - and it was cited on the product's own face until a reviewer opened the
file. **Also withdrawn:** reporting 78,362 AI Village computer-use sessions as
"46 of 46 agents present more than one session context" and "wrong by three orders
of magnitude". The counts were right and the inference was not: a session is a
~40-action window the scaffold cuts on the agent's one machine. What that corpus
can support is in `docs/village_reuse.json` (`scripts/village_reuse.py`).

*Data: AI Digest / AI Village, research use only, aggregates only; collusion.wiki
dump, public.*

## On the organizers' own corpus: how URLs move, and what a "context" is worth

The AI Village export holds no address and no request header, so it cannot say how
many of this tool's request contexts an agent would present to a website. It does
hold every command the agents ran. `python3 scripts/village_reuse.py` streams all
2,019,963 turn rows it needs (307s) and reports three things. Raw output:
`docs/village_reuse.json`.

A **use** here is a fetch - a URL passed to a network client on its command line,
or typed alone into the address bar - not any text containing a URL. The village
quantity is called **re-use**, never a sighting: a canary is issued to exactly one
context and cannot be guessed, and a village URL is neither.

### 1. One agent, several contexts - as far as this corpus can see

| | |
|---|---|
| Agents that fetched with more than one client program | **40 of 46** |
| Agents that fetched the **same URL** with both a browser and a command-line client | **29** (1,073 agent-URL pairs; 566 of them within one session) |
| Agents that set two or more distinct user-agent strings | **22** of the 32 that set one at all |
| And in the other direction: most agents sharing **one** user-agent string | **29** |

Both failure directions, in the hosts' own data. One agent routinely presents
several contexts; and 29 different agents presented one identical user-agent string, so
contexts can collide as well as multiply.

### 2. "Two contexts, one agent" is a property of the definition

How often a URL used in one context and again in another was the same agent:

| A "context" is... | Re-uses | Same agent | Before the scaffold change | After |
|---|---|---|---|---|
| a session | 53,894 | **58%** | 34% | 62% |
| an agent's client program | 9,720 | **7%** | 7% | 7% |

Same corpus, same URLs, same code. **The answer moves by a factor of eight with
the definition of a context**, and by nearly two with the 2026-03-24 scaffold
change that redefined what a session is. (A null: if the later session were drawn
at random from that day's, the same-agent share would be 9%.)

Neither row is this tool's context, which includes the network and the client's
headers. That is the point. A single number here would have been a number about
the definition, and this is the honest version of the result we first tried to
report - and the clearest argument we have for why the tool says "context",
reports what it saw, and stops.

### 3. When a second agent fetched an unguessable URL, had it been posted first?

Restricted to URLs with a token in the path that cannot be constructed without
being told - the nearest village analogue of a canary - excluding API endpoints
and the shared code-hosting namespace every agent is pointed at.

| | |
|---|---|
| Such URLs, fetched | **1,054** |
| Used in more than one session | 353 |
| Of those, only ever by one agent | 137 |
| **First fetches by a different agent** | **410** |

Of those 410 arrivals, in the seven days before each one:

| | |
|---|---|
| another speaker had posted the URL in chat | **83%** |
| it was in another agent's session goal or summary | 9% |
| only its own post, or one older than seven days | 4% |
| **nothing found in the tables read** | **4%** |

**92% of the time a visible hand-off preceded the fetch.** Median 10.3 minutes
from one agent's first use to another's.

The control matters more than the headline: the same test applied where no
hand-off is needed - an agent re-fetching its *own* URL in a later session - fires
for only **36%** (207 cases). So the test discriminates; it is not just
measuring how chatty the village is.

What this does **not** say: that the post caused the fetch. A visible channel
shows a channel existed. And "not found" means not found in the tables we read -
system prompts, shared documents, email and link clicks are not in them, and
agent_memories, claude_code_messages, screenshots were not read.

*Data: AI Digest / AI Village, research use only. URL keys and user-agent strings
are hashed in memory with a per-run key and never written; the output holds counts
and quantiles only.*

## Real third-party fetchers, paste-triggered

<!-- census:start -->
Each of 12 public fetch services was handed one canary URL of its own. The operator's act of handing it over is a row in the ledger's `published` table, written first, so **every sighting below is paste-triggered and none is organic**.

| Service | Outcome | Contexts | Network(s) it came from | User-agent it presented |
|---|---|---|---|---|
| Jina Reader (page-to-text for LLMs) | a browser-shaped request arrived in its window; gate stored nothing | - | - | - |
| Internet Archive, Save Page Now | a browser-shaped request arrived in its window; gate stored nothing | - | - | - |
| W3C Nu HTML checker | recorded | 1 | 52.22.66.0/24 | `Validator.nu/LV https://validator.w3.org/services` |
| W3C Link Checker | recorded | 1 | 52.22.66.0/24 | `W3C-checklink/5.0.0` |
| Microlink (link previews) | a browser-shaped request arrived in its window; gate stored nothing | - | - | - |
| AllOrigins (CORS proxy) | nothing recorded | - | - | - |
| CodeTabs (CORS proxy) | nothing recorded | - | - | - |
| corsproxy.io (CORS proxy) | nothing recorded | - | - | - |
| WordPress mShots (page screenshots) | a browser-shaped request arrived in its window; gate stored nothing | - | - | - |
| thum.io (page screenshots) | a browser-shaped request arrived in its window; gate stored nothing | - | - | - |
| Google PageSpeed Insights | nothing recorded | - | - | - |
| Google Translate (page proxy) | recorded | 1 | 64.233.173.0/24 | `canary-maze-census/1.0 (+https://github.com/itssaharsh/can…` |

- **3 of 12** reached the surface and were recorded, through the real public function and the signed hand-off into the ledger. The table gives the network and the user-agent each one presented; nothing about who operates them is inferred from either.
- For **5**, a request with a full browser header set arrived while that service was the only one being asked, so the human-exclusion gate declined to record it and stored nothing; the only trace is the bare counter moving. That is the gate's stated cost - it would rather lose a sighting than ledger a human - shown rather than described. A full browser header set is what a headless browser sends, which is what a screenshot or page-reading service runs. Attribution is by time window, with a quiet period before each service; the gate keeps no record that could make it exact.
- For **4**, nothing was recorded: the service answered its caller without fetching the page, refused the request, or was rate-limited.

What this is not: evidence that any of these services shares anything with any other. Each fetched a link it was given. Reproduce with `python3 scripts/fetcher_census.py`; raw output in `docs/fetcher_census.json`.
<!-- census:end -->

## What the host refused before we ever saw it

Measured 2026-10-03 against the live public URL, same second, varying only the
user-agent. "Reached us" means the request appears in the application's own log.

| User-agent | Edge | Reached us |
|---|---|---|
| GPTBot | **403** | no |
| ClaudeBot | **403** | no |
| PerplexityBot | **403** | no |
| CCBot | **403** | no |
| Bytespider | **403** | no |
| ChatGPT-User | 200 | yes |
| OAI-SearchBot | 200 | yes |
| Googlebot | 200 | yes |
| Google-Extended | 200 | yes |
| curl | 200 | yes |

Five of ten never arrived. The surface runs behind a Cloudflare quick tunnel,
which blocks declared AI training crawlers by default and exposes no control to
turn that off on the free tier. The same layer also replaces our `robots.txt`:
ours is 66 bytes and says `Allow: /`, the edge serves 3871 bytes of Cloudflare's
own Content Signals Policy. We cannot publish the permission this experiment
depends on.

**This means the organic count is partly a measurement of the host, not of
crawler behaviour**, and it is biased toward zero. A third party asked to read a
canary URL reported 403 and never reached us. See
`docs/memory/failures/F-0005`.

## The honest reading

**No organic sighting has been observed, and no third-party traffic has reached the
surface at all.** Every row in the live ledger was generated by us: local curl
checks, the paste-trigger script, and the seeded replay. Nothing here should be read
as an observation of the wild.

The seeded replay proves the mechanism end to end through the real gate, mint and
detector. It does not prove that automated clients in the wild share URLs with each
other. Those are different claims and this project does not merge them.

For scale: the closest published experiment (arXiv:2605.13706) waited **two months**
for its tokens to surface. A 31-hour window is not evidence of absence.

## What a reader should check first

```
make verify      # five properties, each able to fail
make demo        # builds the viewer offline, in one command
```

Then open the viewer and press **Recompute the hashes locally**. It recomputes every
hash in your browser with `crypto.subtle` from the bundle shipped with the page, and
makes no network request at all. Edit any record in `data.js` and it will tell you
which row no longer matches.

## Pending

```
python3 scripts/trigger_paste.py <public-url>     # mint and print
python3 scripts/trigger_paste.py --report         # what came back
```

A paste-triggered fetch shows **a fetcher following a human's paste**. It is not two
agents sharing information with each other, and it is counted in its own column for
exactly that reason.
