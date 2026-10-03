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
| Operator self-test sightings | 2 | 0 |
| Seeded-replay sightings | 0 | 1 |
| Requests recorded from third parties | 9 | 0 |
| Requests recorded from the operator's own probes | 50 | 0 |
| Requests recorded in the seeded replay | 0 | 2 |
| Secrets issued to third parties | 0 | 0 |
| Secrets issued to the operator's own probes | 16 | 0 |
| Secrets issued in the seeded replay | 0 | 1 |
| Secrets the operator published by hand | 13 | 0 |
| Browser-shaped requests turned away, nothing stored | 15 | 0 |
| Human requests stored | 0 | 0 |

The two columns are never added together. The left one is what the public surface has recorded; the right one shows the mechanism working on a scripted replay. Nothing in the right column is an observation.

**Organic sightings stand at 0.** No third party has been observed fetching a secret it was not handed. That is reported as-is.

**3 sightings are paste-triggered**: a third-party fetcher followed a link the operator had published first (the census below). They show the surface and the ledger recording real third-party infrastructure. They are not evidence that anyone shares anything with anyone, and they are never counted as organic.

9 requests from third parties and 50 requests from the operator's own probes are recorded. The operator's are labelled as self-tests at the moment they are written (F-0004), so they cannot inflate any third-party number.

15 browser-shaped requests were turned away and nothing about them was stored. That counter moves for anything that arrives with a browser's header set - people, the operator's own browser, and headless-browser fetch services alike. It counts the gate firing, not humans.
<!-- counts:end -->

## Real results on the organizers' own corpus

The claim this product refuses to overstate is that **a sighting shows a secret
moved between two request contexts, not that there are two operators**. That is
only worth saying if one actor really does present as many contexts. We measured
it twice, in unrelated corpora.

**AI Village agent logs** (`aidigestorg/ai-village`, access granted for research use):

| | |
|---|---|
| Agents in the corpus | 46 |
| Computer-use sessions | 78,362 |
| Agents presenting more than one session | **46 of 46** |
| Most sessions for a single agent | **7,465** (Gemini 2.5 Pro) |
| Median sessions per agent | 1,080 |

Every agent in the corpus presents more than one session context. The busiest
presents 7,465. Reproduce with
`python3 scripts/village_spread.py` (needs `HF_TOKEN` and dataset access);
the full output is in `docs/village_spread.json`.

**collusion.wiki dump** (independent, measured earlier): one actor label carries
899 revisions across **741 distinct addresses**.

Two unrelated datasets, same shape. This is why the schema has no `actor` entity
and why the viewer says "context A" and "context B" rather than naming actors: an
identity-per-context assumption would have been wrong by three orders of
magnitude on the organizers' own data.

Data: AI Village / AI Digest. Used for research and analysis only, with no
attempt to re-identify anyone; no identifier, goal or message content is read,
printed or stored by the script, only counts and the model names the dataset
itself publishes.

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
