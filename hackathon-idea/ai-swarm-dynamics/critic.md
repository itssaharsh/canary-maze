# critic.md — adversarial review, subagent K
Written 2026-10-02. 13 web lookups + one direct download of the organizers' own dump.
Verdicts: **C1 FIX · C2 KILL · C3 FIX (pitch inverted)**.

Nobody owns these ideas. Nothing below is softened and nothing is invented to look rigorous.
Where I disagree with the generating pass, my answer stands unless a source settles it.

---

## 0. The one thing the generating pass got right, said once

**All three pass the reduction test.** None of them is a model wrapper. The deterministic core
of each — HMAC mint + fingerprint ledger; DOI/ISBN/HTTP resolution; minhash + LSH over text —
is classic, model-free computer science that would still run if every LLM vanished tomorrow.
That is unusual for this theme and the pass deserves the credit.

The three failures are on three *different* axes: **prior art (C1), data (C2), demand (C3).**
Do not read this document as "all three are bad". Read it as "none of them fails where the
pass was looking."

---

## 1. Overlap with the organizers' list and with recycled shapes

| | Organizer-suggestion overlap | Recycled shape |
|---|---|---|
| C1 Canary Maze | **#5** "tools to trace how information spreads within a group" and **#6** "tools that go beyond agent transcripts using the web or digital forensics". It is a web-forensics information-spread tracer. Two of seven. | **None.** The only one of the three that is not a classifier or a clusterer. |
| C2 Source sweep | **#1** "tools to discover agent swarms in the wild". | **Coordinated-inauthentic-behaviour detection** — on the pre-registered recycled list, and `defaults.md` D1. Group accounts by a shared join key *is* CIB detection. |
| C3 Batch card | #1, loosely. | **Coordinated-inauthentic-behaviour detection**, minhash as the join key. Same shape as C2. |

**Structural finding the pass did not state: C2 and C3 are the same idea.** Both are
"group accounts by a shared deterministic artefact, then present the group." One uses a
fabricated citation as the key, the other a near-duplicate PR body. They differ in venue and
key, not in mechanism. If the brief's rule is one idea per problem, it should also notice that
two of its three final ideas collapse to one mechanism. C1 is the only genuinely different one.

The claim that these were "generated AWAY from" the organizer list is weakest for C1, which
lands on two suggestions at once. That is not fatal — the suggestions are broad — but the
write-up should not claim distance it does not have.

---

## 2. CANDIDATE 1 — Canary Maze

### Strongest existing alternative
**arXiv:2605.13706, "Identifying AI Web Scrapers Using Canary Tokens"**, Seiden, Ren, Zhang,
Kim, Liu, Wenger (Duke). Submitted 2026-05-13, **revised 2026-09-03** — one month before this
event. https://arxiv.org/abs/2605.13706 and https://arxiv.org/html/2605.13706v1

The pass listed this as "closest prior art, already found" and then did not absorb what it does.
Opened verbatim from the v1 HTML:

- Identity key is a fingerprint: they treat **"two scrapers the same if they have the same
  User-Agent information and ASN information"**, chosen because it **"provides a balance between
  complexity and granularity in identifying distinct scrapers"**, and they note the approach
  **"can be easily extended to use arbitrarily complex fingerprinting techniques, such as TLS
  fingerprinting or browser fingerprinting."**
- They already keep the ledger: **"we maintain a mapping between scrapers and the tokens served
  to them, so we can later map tokens found in chatbot responses back to scrapers."**
- They already do mint→sighting resolution: **"For each token in a response, we query our
  database for the scraper identity (User-Agent, ASN pair) associated with that token
  assignment."**
- Timescale: **"we wait for two months to allow the scrapers to retrieve the content"**.

So: per-visitor mint ✓, fingerprint-keyed identity ✓, mint↔token ledger ✓, sighting resolved
back to a minting identity ✓, across 22 production LLM systems. The novel residue of C1 is
**the sighting channel only** — an HTTP refetch by a different fingerprint, instead of prompting
a chatbot — and the paper pre-emptively says its fingerprinting is extensible. The shortlist's
"the 'do not fork' bucket came back EMPTY" may be true of *repos*; it is not true of the method.

### Most likely reason it fails
**The central claim is false as written.** "False-positive rate bounded by HMAC collision, not
classifier precision" — the HMAC bounds whether *the token is one you minted and for which
fingerprint*. It says nothing about whether two different fingerprints are two different actors.
The inference "minted for A, fetched by B ⇒ A and B talked" requires `fingerprint A ≠ fingerprint B
⇒ actor A ≠ actor B`. That is a classifier assumption, and it is precisely the assumption the
idea claims to escape.

It is also false on the event's own reference data. In the organizers' `labels.jsonl.gz`
(downloaded 2026-10-02) a single actor label carries `stored_revisions: 899` against
`stored_revision_ips: 741` and `stored_revision_ip16: 114`. **One actor, 741 IPs, 114 /16s.**
Every intra-actor fingerprint change in that corpus would register as a "sighting" — a
propagation edge between an actor and itself. The false-positive rate is bounded by nothing.

This is fixable by restating the claim, not by deleting the project. But as written it is the
kind of overclaim a research jury tests in one question.

### Label check
- **"False-positive rate bounded by HMAC collision"** — overclaim, see above. Weak evidence
  dressed as a cryptographic guarantee.
- **"GPTBot 29,000+ requests and ChatGPT-User 1 in the first 12 hours, so a crawler->user-agent
  handoff is the expected first sighting"** — **the arithmetic does not follow.** One
  ChatGPT-User request is one request to an unknown URL. For a sighting, that single request must
  land on a URL *minted for GPTBot*, drawn from a per-visitor URL space. n=1, with no stated
  overlap, is not an expectation. And the group that actually ran this experiment waited two
  months. The 12-hour crawl figure and the two-month propagation figure describe different
  events; using the first to argue weekend feasibility is the error.
- **"a model is used only to match paraphrased (laundered) tokens"** — fine, and well separated.
  No complaint.

### Buzzwords / vague wedges
- "an evidence bundle a third party can verify offline" — verify *what* offline? The HMAC proves
  token provenance. Nothing offline-verifiable supports "fingerprint B is a different actor from
  fingerprint A," which is the load-bearing claim.
- "token mint", "sighting ledger", "Canary Maze" — three coined nouns for one hash table and one
  diff. Three brands for one artefact reads as padding.
- "propagation graph" on one edge is a line.

### Reduction test, in my own words
> "The user gives an HTTP request to a key-derivation function and gets a unique token back;
> later the server gives two fingerprints and a matching token to a lookup and gets an edge back."

**Fair? No — and that is the point in C1's favour.** There is no model anywhere on the primary
path. If models disappeared tomorrow, the mint, the ledger, the sighting detector, the graph and
the bundle all still function; only the paraphrase-matching side table dies, and it is already
quarantined out of the proof graph. **Substantial.** C1 is the cleanest pass of the three.

### Interesting but not good?
**No.** The pain is documented. The Duke paper exists because 22 production LLM systems scrape,
and the brief's own site-operator problem carries five independent orgs. Real pain.

### Verdict: **FIX**
Keep the mechanism. Three mandatory changes:
1. **Delete the HMAC-bound claim.** Replace with: the HMAC proves the token is ours and names the
   fingerprint it was minted for; whether two fingerprints are two actors is a separate, weaker
   inference — and render it as such in the graph (solid edge = token authenticity, dashed =
   actor distinctness). This is a *better* pitch, not a weaker one, because it is the honest one
   and the jury is research staff.
2. **Cite arXiv:2605.13706 in the README and position against it explicitly:** their sighting
   channel is prompting 22 LLMs and waiting two months; this one is a same-day HTTP refetch.
   An unacknowledged overlap with a paper revised a month before the event reads far worse than
   the overlap itself.
3. **Replace "deploy and wait" with the plan in §5(b).**

---

## 3. CANDIDATE 2 — Non-existent source sweep

### Strongest existing alternatives
- **Wikipedia:WikiProject AI Cleanup**, https://en.wikipedia.org/wiki/Wikipedia:WikiProject_AI_Cleanup
  — the community body that owns this exact problem, with real cases documented (the article
  **"Leninist historiography ... was entirely written by AI and included a list of completely fake
  sources in Russian and Hungarian at the bottom of the page. Google turned up no results for
  these sources."**). It ships **Cite Unseen** (a user script marking citations to AI-generated
  sites or URLs with LLM tracking parameters), the **LLM dungeon** list, **Signs of AI writing**,
  and a **VWF bot log**.
- **arXiv:2607.22693** "Detecting Hallucinated and Suspicious Citations: What Current Tools Can
  and Cannot Do", Badalova & Mayr (PDF body is image-only, so this is a **lead**, not evidence).
- **arXiv:2605.08583** "Source or It Didn't Happen: A Multi-Agent Framework for Citation
  Hallucination Detection" (title only — **lead**).
- Commercial, from search titles only (**leads**): AiCitationChecker, Sourcely Citation Verifier,
  Citely Fake Citation Checker. The *resolution* half of C2 is a commodity.

### Most likely reason it fails — and I went and measured it
I downloaded the organizers' dump directly (https://collusion.wiki/explorer/download, ungated,
2026-10-02) and ran the candidate's own extractors over `revisions.jsonl.gz`, all 14,591
revisions, 3,103 actor labels:

| Extractor in the C2 spec | Revisions matched | Share |
|---|---|---|
| **DOI** (`10.xxxx/...`) | **0** | 0.00% |
| **ISBN** | **0** | 0.00% |
| **`<ref>` / `{{cite}}` template** | **0** | 0.00% |
| journal-ish `(YYYY)` — loosest possible proxy | 44 | 0.30% |
| bare URL | 10,101 | 69.23% |

**Distinct DOIs in the entire corpus: 0.** Three of the four extractors in the specification have
nothing to extract. The brief's data note — *"citation density there is probably low"* — is wrong
in kind, not in degree. It is a hedge where a 4.2 MB download would have given a number.

The surviving extractor makes it worse, not better. 23,617 distinct URLs, of which **8,473 are
shared by ≥2 actors**. Top shared hosts:

```
wikiservice.at       2412      md.succ.ai            498
jqp.vercel.app       1523      markdown.new          192
api.datausa.io       1017      pure.md               145
www.sec.gov           660      r.jina.ai             109
```

That is the wiki's own host, plus URL-to-markdown scraping proxies (`r.jina.ai`, `pure.md`,
`md.succ.ai`, `markdown.new`) and public data APIs (`api.datausa.io`, `sec.gov`). **Shared
tooling, not shared sources.** A join on shared URL yields thousands of groups all meaning
"two agents used the same scraper." The claim *"a fabricated citation is a near-perfect join
key"* is contradicted on the only corpus available: the identifier classes that would be
near-perfect are empty, and the class that is populated is saturated with trivial co-occurrence.
Requiring ≥2 shared fabrications does not save it when the top hosts are shared by hundreds.

### The organizers already ship steps 1, 3 and the substrate of 4
Not flagged anywhere in the brief. The same download includes:
- **`links.jsonl.gz`, 23,877 rows**, schema `{url, host, record_ids, relation, followed,
  source_url_sha256, url_withheld}`. `record_ids` is the inverted index from URL back to the
  revisions containing it, and there is already a `followed` boolean. **That is C2's
  extract-and-index step, pre-computed and published.**
- **`labels.jsonl.gz`, 3,103 rows**, schema includes `stored_revision_ips`, `stored_revision_ip16`,
  `pages`, `first_write`, `last_write`, `is_human_handle`, `save_requests`. **That is C2's
  account-grouping metadata, pre-computed and published.**

The brief's own §Stage-5 note already warns: *"collusion.wiki's /explorer ALREADY SHIPS browse,
revision history, search of recovered deleted content, and metadata"* and *"The German dump is
therefore good for TESTING a method cheaply, not for BEING the product."* That warning applies
to C2 harder than the brief realised.

### Label check
- **"citation density there is probably low"** — a guess in the place where a number belongs.
  It is zero for every identifier class the tool resolves.
- **"a fabricated citation is a near-perfect join key"** — asserted as a fact, unmeasured, and
  falsified above on the event's own corpus.
- **"resolves each DETERMINISTICALLY (DOI content negotiation, OpenLibrary, HTTP HEAD, archive
  check)"** — **"deterministically" is wrong.** HTTP HEAD against the live web is not
  deterministic: Cloudflare 403s, paywalls, 429s, geo-blocks, link rot, robots refusals, and
  legitimate pre-DOI-era journals and offline books all return "does not resolve". Every one of
  those is a false fabrication claim fed into an accusation of sockpuppetry. The capitalisation
  of DETERMINISTICALLY is doing argumentative work the mechanism does not support.
- **"Extension:SimilarEditors, whose 'deployment is paused as of July 2023'"** — **stale by three
  years.** https://www.mediawiki.org/wiki/Extension:SimilarEditors, page last updated
  2026-09-02: **"This extension has not been maintained for some time, and no longer supports
  recent releases of MediaWiki. It was archived per T436880."** It is archived, not paused. The
  correction favours the idea's no-competitor claim — but quoting a 2023 status in an October
  2026 write-up tells a jury the author did not re-check, which costs more than it gains.
- **"report 'same hand OR same model' as the honest finding"** — this is presented as a
  mitigation for the same-model objection. **It is not a mitigation; it is the admission that the
  join key does not identify an actor.** The product is an account-grouping queue. A group that
  might be one hand or might be two strangers who used the same model is not actionable in a
  sockpuppet investigation, which is the one output format the idea commits to.

### Buzzwords / vague wedges
"near-perfect join key", "resolves each DETERMINISTICALLY", "weight by rarity of the fabricated
string" (rarity measured against what corpus? there is no base rate). The one concrete and
genuinely good thing in it is the output format: a pre-filled page in the community's own
sockpuppet-investigation template. That is real craft and it should survive into something else.

### Reduction test, in my own words
> "The user gives a stream of wiki revisions to a resolver and gets a list of account groups back."

**Fair? Yes, and it is model-free** — the paraphrase step is absent, the resolution is HTTP and
catalogue lookups. If models disappeared tomorrow the resolver and the grouper still run.
**Substantial on the reduction axis.** C2 does not die on reduction. It dies because the input
it reduces does not exist in the corpus this event is built on.

### Interesting but not good?
**Yes — this is the flag.** The join key really is absent from every grouping tool I opened
(SimilarEditors archived; WikiProject AI Cleanup's own tooling is Cite Unseen and manual lists).
Novel. And there is no evidence anyone has the pain in a form the key can reach: zero DOIs in
the event corpus, and the community that owns the problem does not frame it as coordination at
all. WikiProject AI Cleanup, which I opened in full, does not group accounts by shared fabricated
source and treats AI misuse as individual editors needing education. Novelty with no reachable
pain is the definition of interesting-but-not-good.

### Verdict: **KILL**
Not for novelty and not for reduction — it survives both. It dies on four stacked facts:
1. Zero DOIs, zero ISBNs, zero `<ref>`/`{{cite}}` in the organizers' 14,591-revision dump.
   Three of four extractors have no input.
2. The one extractor that fires produces 8,473 ≥2-actor groups dominated by shared scraping
   proxies. The join key is not near-perfect; it is saturated.
3. The organizers already publish the extraction index and the account metadata.
4. The only fallback venue (en-wiki recent changes) takes it off-theme (see §5a), and over one
   weekend the count of en-wiki account pairs sharing ≥2 *verified*-non-existent sources is
   plausibly zero. There is no third venue.

Salvage: keep the pre-filled-investigation-page output format and move it inside another idea.

---

## 4. CANDIDATE 3 — Batch card

### Strongest existing alternative
**GitHub itself.** https://github.blog/open-source/maintainers/how-pull-request-limits-are-cutting-down-the-noise/
published **2026-06-18** (the brief says the cap shipped 2026-06-17; date it from the post).
Also: GitHub's pull-request-archiving feature "shipping soon", issue limits "in development", and
"smarter bypass signals" planned. Named by maintainers in the community thread as already in use:
**"Good Egg Trust Scoring"** action and a **Repository Policy Score** checker. Search-title-only
leads I did not open: `ai-moderator`, `anti-slop`, `niubi_guard`, `pr-triage-web`, Spamtoberfest.

### The pass filed its best evidence under "counter-evidence"
GitHub's own post says the cap **"does nothing when someone opens pull requests across hundreds
of repositories at once"**, and names "trust signals, rate limiting, or other cross-repository
controls" as still being explored, none implemented. **That is the platform owner naming C3's
exact gap, in writing, four months ago.** It is the single strongest fact in the whole candidate
set and the brief listed it as evidence against the idea. Lead with it.

### Most likely reason it fails
**The ground truth does not exercise the feature.** The Wiz report checks out
(https://wiz.io/blog/six-accounts-one-actor-inside-the-prt-scan-supply-chain-campaign): six waves
from one actor from 2026-03-11, **"well over 500 malicious PRs"**, two npm packages compromised,
and **"the attacker, operating under the account ezmtebo, opened over 475 malicious PRs in 26
hours"**. So **~95% of the only cited campaign is a single account.** A per-repo open-PR cap plus
a rate limit already handles that shape. The cross-account join — the part GitHub's cap provably
cannot do — is the remaining ~25 PRs. The demo's headline number ("submission 14 of 112 opened by
9 accounts") would be generated almost entirely by the feature that is already solved, while the
novel feature carries a tail.

Second reason, independent: **the output is the one thing nobody asked for.** GitHub community
discussion #185387, https://github.com/orgs/community/discussions/185387, running 2026-01-27 to
2026-08-04 — blocking/banning and rate limits are the most requested; cross-repo detection "wasn't
a common theme"; **"No maintainers explicitly asked for batch-identifying labels"**; and the
thread "emphasizes friction-adding mechanisms (issue-first workflows, CI gates, templates) over
detection/attribution approaches." One maintainer did say **"I had to batch-close several AI
generated PRs which were all submitted around the same time"** — real, and the single piece of
demand evidence for the batch concept, but it is a request for batch *closing*, not batch
*labelling*. This independently corroborates the brief's own 2.1%-label / 20.8%-ban figure.

### Label check
- **"GitHub shipped a per-contributor open-PR cap on 2026-06-17"** — the blog post is dated
  2026-06-18. I did not find a 17th. Minor; cite the post.
- **"six named accounts, one actor, 500+ malicious PRs"** — true but the distribution is omitted,
  and the omission is the whole argument. 475 of 500+ from one account is load-bearing against
  the pitch and should be in the write-up, not left out of it.
- **"~90M PRs/month in 2026"** — corroborated: the GitHub post reports monthly PR volume rising
  from 25 million (Jan 2023) to 90 million (June 2026).
- **"the quality of one submission is arguable; the shape of the batch is not"** — rhetorically
  strong, but false on the cited campaign, where the "shape of the batch" is one account doing
  475 PRs and the interesting shape is a 25-PR tail. The sentence needs a batch that earns it.
- **"a rolling CROSS-INSTALL index"** — presented as architecture, but a GitHub App receives
  webhooks only for repos where it is installed. On a solo weekend the index has one install and
  there is no "cross". The author's cross-repo burst profile from the public events API *does*
  work without installs; the minhash index does not. Stated as a fact, true only at scale the
  project will not reach.

### Buzzwords / vague wedges
"structural tells" — unspecified, and the usual hiding place for whatever did not work.
"writes into a real system of record" (from the shortlist) is doing a lot with "a label and a
collapsed comment". "model-only matches render as 'possible' and never count toward N" is good
discipline, stated clearly — no complaint there.

### Reduction test, in my own words
> "The user gives a PR title and body to a minhash and gets a batch id back."

**Fair? Yes, and it is model-free.** Minhash/LSH plus the public events API plus a burst profile
is 1990s computer science. If models disappeared tomorrow, every deterministic key still works
(and the PR flood would shrink, but that is true of the whole event). **Substantial.**

### Interesting but not good?
**Partially.** Not imaginary — the platform owner wrote the gap down, which is about as good as
problem evidence gets. But the users asked for blocks and friction, and this ships a label. Novel
+ confirmed gap + wrong output.

### Verdict: **FIX, with the pitch inverted**
1. **Lead with GitHub's own sentence** — *"it does nothing when someone opens pull requests
   across hundreds of repositories at once"* — and the fact that cross-repository controls are
   still unimplemented. Stop presenting the cap as a threat.
2. **Find a batch where the cross-account join does the work,** in the GH Archive replay, and
   demo that. If prt-scan's multi-account slice is small, say so and argue why it matters anyway:
   it is precisely the residue the cap cannot touch. Do not let the headline number come from the
   solved case.
3. **Change the output to something a maintainer already wants.** A blocklist export, a bulk-close
   list, a ruleset, or an abuse report with the batch attached. The "batch card" can stay as the
   view; it cannot be the only artefact when the owning community explicitly did not ask for it.
4. **Drop the GitHub App for the weekend** (see §5c). Ship the replay plus a report over real
   public data; show the App as one screenshot of a plan.
5. **Meet the theme problem head-on** (see §5a) rather than borrowing the word "swarm".

---

## 5. The three questions the caller is least sure of

### (a) Theme fit — blunt

The event is framed on two incidents about **agents coordinating with each other**. Judged by
AI Village and Grove Research staff, who wrote that framing.

**Candidate 2: honest in name, off-theme in execution.** The German Wiki incident genuinely *is*
a wiki of agents — I verified it from the organizers' own `labels.jsonl.gz`: 3,103 account labels,
`is_human_handle: False` on the ones I sampled, names like `A3ReadOnlyForensics`,
`AICountyResearch`, `APILinkSourceHelper`, `AgentDataUSAProbeFebX2`. So "wiki accounts = agent
swarm" is fully honest **on that wiki**. The problem is that C2 cannot run there — zero DOIs, zero
ISBNs, zero cite templates — so by its own data note it must run on en-wiki, where the accounts
are humans and human-driven LLM users. At that point the write-up is claiming a wiki-swarm brief
while demoing human sockpuppets. A jury that *built* the agent-wiki dataset will ask which wiki
the results came from in the first minute. **This is not a labelling problem that better framing
fixes; the honest venue and the workable venue are different wikis.**

**Candidate 3: a stretch, and the biggest off-brief exposure of the three.** The prt-scan actor is
one human running six accounts with automation and AI-generated payloads. Nothing in C3 involves
agents coordinating with each other, reading each other's output, or talking. It is a human-directed
botnet that uses a model as a payload generator. There is a defensible adjacent framing — ~17M
AI-authored PRs/month means the surrounding flood genuinely is agents — but that flood is
*uncoordinated*, and C3's whole thesis is that coordination is the detectable thing. The honest
phrase is "agent-generated submissions at scale", which is not a swarm. If the write-up says
"swarm", the jury will read it as the word being borrowed.

**Candidate 1: on-theme, but its first result proves the wrong thing.** C1 sits squarely on
organizer suggestions #5 and #6. But the sighting it expects first — GPTBot crawls, ChatGPT-User
later fetches — is one vendor's crawler and one vendor's fetcher, same company, same index. That
is not two agents talking; it is one company's two services sharing a database. "Did they talk?"
answered with "OpenAI's pipeline works" is a true result about infrastructure and a null result
about swarms, and the write-up has to say which it got.

**Ranking of off-theme risk, highest first: C3, then C2, then C1.** None is disqualifying if the
write-up is honest about what it demonstrated. All three become disqualifying if the write-up
uses "swarm" to paper over the gap — this jury wrote the brief and will test the word.

### (b) Candidate 1's demo dependency

**If the sighting never fires, what is left is the Duke paper's setup with none of its results:**
a website serving unique URLs, and a table of who got which URL. Empty propagation graph, an
evidence bundle with nothing to evidence, and the one claimed insight — planting beats detecting —
entirely unexercised. The mechanism is unfalsified *and* undemonstrated.

**"I deployed it and the sighting has not happened yet" is not a presentable result at this
event** — and the reason is specific, not general. The submission offers an *optional* "write-up
of real results you identified by using your tool". For most entries, skipping that is fine. For
this one, the entire pitch is that it manufactures real evidence instead of inferring it. Skipping
the real-results section concedes the thesis. It is the one project that cannot afford the
optional part to be empty. Meanwhile the group that actually ran this experiment set the jury's
expectation of the right timescale at **two months**, not 31 hours.

**Build the result, do not wait for it.** Two things, both schedulable:
1. **Seeded replay as the primary deliverable.** Mint for two clients you control, have B fetch
   A's token, show the graph and the bundle for a manufactured edge, labelled as synthetic. Plus
   the live deployment running alongside with its log shown honestly: "0 organic sightings in 31
   hours; here is the crawl volume we did see." Working mechanism + honest negative is a real
   result and it is not luck-dependent.
2. **Make the sighting cheap to trigger, instead of hoping.** Paste a minted URL into three
   public AI chat products yourself and watch which fetchers come back for it. Every arriving
   fetcher is a sighting against a fingerprint that never minted the token; it fires in minutes;
   and it answers a question operators actually have — "when a user pastes my URL into a chatbot,
   who fetches it, and does it respect my robots?" Within 20 hours, repeatable, no luck.
   **Caveat, state it:** this demonstrates "a product's fetcher followed a human's paste", not
   "agents talked to each other". Honest, interesting, and not a swarm.

Either way: do not schedule the weekend around an event you do not control.

### (c) The one thing most likely to eat the weekend, per idea

- **C1 — the serving layer and the URL space, not the ledger.** Per-visitor unique *crawlable*
  URLs means an unbounded URL space that must be generated, sitemapped, served, and stay stable
  long enough to be refetched — a token minted for A must still return 200 when B asks, or there
  is no sighting at all. Stand up a domain, DNS, TLS, sitemap, get crawled: hours of
  infrastructure with external latency you do not control. Forking an unfamiliar 125-star repo
  (Pyison) to do per-visitor minting is where Saturday goes. The mint, ledger, sighting detector
  and graph are each an afternoon. **The glamour is in the graph; the weekend goes to DNS.**
- **C2 — the resolver.** Four independent resolution paths (DOI content negotiation, OpenLibrary,
  HTTP HEAD, archive check), each with its own auth, rate limits, retries, timeouts, caching and
  failure semantics — and each one's *failure* mode is the product's *positive* signal, so every
  unhandled false negative becomes a published fabricated-source claim about a named account.
  Getting that to a standard you would put your name on exceeds 20 hours by itself. And on the
  event's corpus, three of the four have nothing to resolve.
- **C3 — getting a real batch to render.** The GH Archive replay of 2026-03-11 → 2026-04-03 is the
  only route to the Wiz ground truth: ~24 days of hourly archives to download, filter and index
  before the minhash produces anything. In parallel the GitHub App is a second full build —
  webhooks, install flow, permission scopes, label and comment write paths, persisted batch
  records — whose cross-install index will have exactly one install. **These are two weekends.
  One must be cut, and the App is the cuttable half**, because the public events API gives the
  cross-repo profile without any install at all.

---

## 6. Summary

| | Verdict | Dies / is saved on |
|---|---|---|
| **C1 Canary Maze** | **FIX** | Mechanism real, reduction test cleanest of the three, only non-CIB idea in the set. Must delete the HMAC-bound false-positive claim (one actor = 741 IPs in the organizers' own data), must cite and position against arXiv:2605.13706v2 (revised 2026-09-03, does mint + fingerprint key + ledger), must replace deploy-and-wait with a seeded replay. |
| **C2 Source sweep** | **KILL** | Survives novelty and reduction; dies on data. 0 DOIs, 0 ISBNs, 0 cite templates in the organizers' 14,591 revisions (measured 2026-10-02). The one firing extractor yields 8,473 ≥2-actor groups dominated by shared scraping proxies. Organizers already publish the link index and the account metadata. Only fallback venue is off-theme. |
| **C3 Batch card** | **FIX** | Gap confirmed in writing by the platform owner — GitHub's cap "does nothing when someone opens pull requests across hundreds of repositories at once". But 475 of 500+ prt-scan PRs came from one account, so the ground truth barely exercises the cross-account join; and the owning community asked for blocks, not labels. Invert the pitch, change the output, drop the App for the weekend, meet the theme problem head-on. |

**Method note.** 13 web lookups. One refused/unusable: arXiv:2607.22693's PDF body is
image-only, so it is a lead, not evidence. Three search-result sets yielded titles I did not open
(`ai-moderator`, `anti-slop`, `niubi_guard`, `pr-triage-web`, AiCitationChecker, Sourcely,
Citely, arXiv:2605.08583) — **leads, not evidence**, and flagged as such above.

**Absence claims, stated properly:**
- None of the 2 Wikipedia-side pages I opened (WikiProject AI Cleanup; Extension:SimilarEditors)
  groups accounts by a shared fabricated source, and neither uses citations as a grouping signal.
- Neither of the 2 Duke-paper versions I opened discusses detecting a *different HTTP client*
  refetching a token minted for another client, or a crawler→user-agent handoff. That residue is
  genuinely C1's.
- None of the 2 GitHub-side pages I opened (the PR-limits post; community discussion #185387)
  describes a shipped cross-repository coordinated-batch detector; GitHub's own post says such
  controls are still being explored.
