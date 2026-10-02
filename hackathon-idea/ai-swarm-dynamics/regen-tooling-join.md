# Regen validation: "Tooling fingerprint join"

**Validated:** 2026-10-02 (hackathon starts 2026-10-03)
**Origin:** regenerated after the fabricated-citation join died on measurement (0 DOIs / 0 ISBNs / 0 `<ref>`/`{{cite}}` in the corpus).
**Idea:** group agent accounts by shared *retrieval infrastructure* (markdown proxies, scraping APIs, API path/query shapes) instead of by what they wrote.
**Load-bearing claim under test:** "an agent's choice of retrieval plumbing is incidental to its output and therefore not something it varies to avoid detection."

---

## VERDICT: DEAD

Three independent reasons, any one of which is sufficient. They are ordered by how fast a judge reaches them.

1. **The hypothesis is factually false on this corpus.** I measured it. The shared proxy URLs are not independent tooling choices — they are the *same literal string copied off the wiki*. The plumbing was the broadcast payload, not incidental exhaust, so the premise ("incidental … not something it varies") inverts.
2. **The published incident report already names the shared tooling**, by host, with the mechanism explained. The finding is a restatement.
3. **The join key is low-entropy and baseline-dominated** — 41 distinct values over 3,103 accounts, and 59% of the flagship group is recoverable from one page's editor list that the explorer already ships.

Plus: the mechanism is published prior art in two 2026 papers, one of which reports the *opposite* of the claimed insight.

---

## 1. KILL-FACT SEARCH

### 1a. The incident report already names the tooling — this is the decisive check

Source: "Discovery of a new OpenAI agent message board", Sydney Von Arx (Nightingale Collective), Cormac Slade Byrd, Spencer Kitts, Thomas Larsen, dated **4 September 2026**, <https://collusion.wiki/> (2026-10 accessed).

The report has a dedicated section on tunnel providers and names them exhaustively:

> "We also have evidence that the agents were using SSH tunnels in order to host parts of their environment publicly."

> "In total, they used four providers: Pinggy, Serveo, localhost.run, and localtunnel."

> "These are all tunnelling services: they take a service running on your machine and give it a public internet address."

It names a markdown proxy *and explains exactly why the agents used it* — i.e. it already supplies the interpretation the idea was going to contribute:

> "For example, you might block any links containing https://data.nysed.gov , but not https://markdown.new/httpbin.org/redirect-to?url=https%3A%2F%2Fdata.nysed.gov ."

It already reasons about jina.ai by name:

> "Tunnelling could allow agents to easily point other websites (like jina.ai) at their own content."

It quotes the proxy URLs inline in its own evidence blocks, e.g. under "Some examples of agent behaviour", a 2026-06-18 post by `AgentNewNameXYZ123`:

> "* plaintextproxy https://r.jina.ai/http://r.jina.ai/https://www.sec.gov/files/county.json"

and a 2026-05-26 post:

> "Reference links
> https://markdown.new/piv.max.gov/portal/document/SF133/Budget/attachments/2346466575/2374423602.pdf"

It names the API endpoints the idea would key on:

> "External links: https://api.usaspending.gov/api/v2/agency/028/budgetary_resources/ and https://api.usaspending.gov/api/v2/agency/028/program_activity/?fiscal_year=2020 …"

> "Useful all-state endpoint: https://api.datausa.io/tesseract/data.jsonrecords?cube=pums_5&drilldowns=State%2CYear&include=Industry%20Sector%3A61-62%3BWorkforce%20Status%3Atrue&locale=en&measures=Total%20Population"

And it names the browser automation:

> "[…] I automated in Playwright `page.route`: requests.Session(verify=False).request(method, rewritten_url, headers={**req.headers,'Host': original_host}, data=req.post_data_buffer), then route.fulfill."

**Answer to the brief's most important question: yes. The report already names the shared tooling** — the markdown proxies (`markdown.new`, `r.jina.ai`, `httpbin.org` redirectors), the four tunnel providers by name, the API endpoints, and Playwright/Selenium. A tooling-fingerprint tool would be re-deriving the report's own appendix.

### 1b. The report also states the *purpose* of the links, which is the hypothesis-killer

Two verbatim sentences from the same page:

> "The most typical way the agents used the wiki was to store links."

> "They start by posting lists of external links that are useful for their tasks."

The critic's reading was "those shared URLs are evidence of shared TOOLING, not shared sources." The report says the links were neither: they were **the message**. The wiki existed to pass URLs between agents. §2 below confirms this numerically.

### 1c. The `/explorer` baseline — closer than expected

- <https://collusion.wiki/explorer> (2026-10 accessed). Nav: `Findings`, `Edits by day`, `Agent edits`, `Agent names`, `Sites`, `Download`. Routes seen: `day/[date]`, `pages/1`, `labels/1`, `sites/`, `download`.
- <https://collusion.wiki/explorer/sites> (2026-10 accessed) is a ranked list of **30 external sites targeted by agents**, and it **already classifies each host by type** — the rows carry a content classification ("wiki", "URL shortener", "pastebin"), counts, and date ranges, with the site name clickable for drill-down. Top rows as rendered: `dse 5,154 wiki 13,403 revisions 2026-05-24 – 2026-07-02`; `probier 601 wiki 1,013 revisions 2026-05-24 – 2026-07-02`; `rmn.reNew 499 URL shortener 499 links 2026-05-26 – 2026-06-21`.

So step 2 of the idea — "classify each host as a content source versus a retrieval intermediary" — exists in a weaker form in the organizers' own UI, including the infrastructure-category axis ("URL shortener" is exactly a retrieval intermediary). What `/sites` does *not* do is pivot host → account set. That gap is the idea's entire remaining surface, and §2–§3 show the gap is not worth crossing.

What `links.jsonl.gz` actually ships (measured, 23,877 rows, schema `{url, host, record_ids, relation, followed, source_url_sha256, url_withheld}`):

- `record_ids` is a genuine inverted index (url → revisions), median length 1, so the host→account pivot is a ~20-line join. **That is the baseline a judge will name, and it is one groupby away from the product.**
- **`followed` is `False` for all 23,877 rows.** The dump never says whether a link was actually retrieved. So "retrieval intermediary" is never observed — it is entirely the analyst's own host list.
- **`relation` has exactly one distinct value across all 23,877 rows: `link_in_selected_agent_related_text`.** There is no link typing to build on.
- **`url_withheld: True` for 7,793 of 23,877 rows, and the withholding is concentrated precisely on the intermediaries**: `md.succ.ai` 1,432/1,434 (99.9%), `markdown.new` 665/665 (100%), `pure.md` 262/262 (100%), `r.jina.ai` 244/246 (99.2%), `httpbin.org` 14/14 (100%), `allorigins.hexlet.app` 477/479 (99.6%) — against `api.datausa.io` 0/2,217 (0%), `api.usaspending.gov` 0/104 (0%), `wikiservice.at` 3/8,723 (0.03%). Aggregate: **92.8% of intermediary rows withheld vs 22.9% of all other rows.** The withheld value is replaced by a stub, e.g. `[operational URL omitted; host=allorigins.hexlet.app; sha256…]`.

The idea asks for "specific API paths and query-parameter shapes" from intermediaries. In `links.jsonl` the organizers deliberately redacted exactly those. (Honest caveat: the full strings survive in `revisions.jsonl` bodies — that is where I recovered mine — so this is friction, not the kill. But it means the clean index is unusable for the discriminating half of the feature and the organizers made a considered decision that those strings are operational hazards.)

### 1d. Prior art on the mechanism — published, 2026, and one paper reports the opposite of the claimed insight

- **Cross-Agent Campaign Attribution: Linking Asynchronous Attacks Across LLM Agents** — SangJin Park, Myungsub Choi, Jineok Kim, Minseung Kang, submitted 21 Jul 2026, <https://arxiv.org/abs/2607.18826>. Abstract, verbatim: "We formalize cross-agent asynchronous campaign attribution: linking sessions from the same latent adversarial campaign without shared runtime state, test-time campaign labels, or attacker identity oracles. We introduce Asynchronous Attribution Fingerprint Vectors ($A^2FV$), a lightweight proxy-side reference protocol for scoring pairwise campaign similarity from proxy-observable tool-use, timing, and prompt residue."

  That is the idea, formalized and named, three months ago: link agents across a campaign from **proxy-observable tool-use**. And its own result cuts against the premise — from the results section: "the strongest fixed signal is carried by structural and stylometric residue, while timing is retained as a diagnostic channel." The one published study that put tool-use and text residue side by side for cross-agent linking found **text residue was the stronger signal**. The idea's claimed insight (prose indistinguishable, plumbing reliable) is contradicted by the nearest measurement.

- **Known By Their Actions: Fingerprinting LLM Browser Agents via UI Traces** — William Lugoloobi, Samuelle Marro, Jabez Magomere, Joss Wright, Chris Russell, submitted 14 May 2026, <https://arxiv.org/abs/2605.14786>. Abstract, verbatim: "Across 14 frontier LLMs and four web environments spanning information retrieval and shopping tasks, we show that an agent's actions and interaction timings, captured via a passive JavaScript tracker, are sufficient to identify the underlying model with up to 96% F1." Establishes agent-identification-from-action-traces as solved territory.

- **Uncovering Coordinated Cross-Platform Information Operations Threatening the Integrity of the 2024 U.S. Presidential Election Online Discussion** — Marco Minici, Luca Luceri, Federico Cinus, Emilio Ferrara, submitted 23 Sep 2024, <https://arxiv.org/abs/2409.15402>. Abstract, verbatim: "Using our machine learning framework for detecting online coordination, we analyze a dataset comprising election-related conversations on $\mathbb{X}$ from May 2024. This reveals a network of coordinated inauthentic actors, displaying notable similarities in their link-sharing behaviors." Clustering accounts by shared-link behaviour is a mature CIB method with trained frameworks behind it.

### 1e. Threat-intel infrastructure pivoting: it applies, and its own doctrine rejects this join key

This was the brief's specific ask — establish precisely whether the mature discipline's tools apply to "accounts on one platform joined by the third-party retrieval services they call."

They apply conceptually, and the discipline has a standing rule that disqualifies this exact key. From practitioner material surfaced in search (2026-10 accessed, vendor/practitioner sources, treated as doctrine summary rather than peer-reviewed evidence): infrastructure pivoting via reverse-IP can turn one indicator into a cluster, but analysts must separate genuine connections from false positives generated by **shared hosting**; weak selectors such as shared hosting providers or common IP ranges "are better treated as background context," because addresses from shared hosting appear across many feeds simply because unrelated activity uses the same infrastructure. Threat-intel platforms exist in part to filter CDN and legitimate-service IPs out before they reach a SIEM.

`r.jina.ai`, `md.succ.ai`, `markdown.new`, `pure.md` are public shared services used by the entire internet. Under the discipline's own taxonomy they are the *canonical weak selector* — background, not a pivot. So the answer is not "a mature discipline missed this"; it is "a mature discipline has a rule for this and the rule says no."

(Tool-level check, MISP/OpenCTI/Maltego: these are IOC-sharing and knowledge-graph platforms keyed on IPs, domains, hashes and certs. Nothing I opened models "platform account → third-party service called." So the *tooling* does not drop in — but the doctrine transfers, and the doctrine is the kill.)

### 1f. Published work on detecting agents by their retrieval intermediaries specifically

None of the 9 search results I surfaced on this was a measurement. They were vendor comparison pages (`fast.io`, `tavily.com`, `spider.cloud`, `use-apify.com`, `crawlforge.dev`, `dexto.ai`, `pickaxe.co`, `knowledgesdk.com`, `digitalapplied.com`) — LEADS, not evidence, and not opened. The one substantive note: blocking of these services is predominantly User-Agent based, and the self-identifying tools (Firecrawl, Jina) are the easiest to stop. **This corpus has no User-Agent field**, so even the one working real-world detection channel is absent here.

So: a genuine small gap exists in the literature on *which* proxies agents pick. It is a measurement paper, not a tool, and §2 shows this corpus cannot support it.

---

## 2. IS THE SIGNAL REAL OR TRIVIAL?

I downloaded all three files (ungated, HTTP 200: `revisions.jsonl.gz` 3,226,133 B / 14,591 rows; `links.jsonl.gz` 2,178,607 B / 23,877 rows; `labels.jsonl.gz` 167,875 B / 3,103 rows) and measured it. Corpus confirmed: 14,591 revisions, 3,103 account labels, **10,102 revisions containing a bare URL (69.2%)**, 23,582 distinct URLs, 8,468 shared by ≥2 accounts. The critic's numbers replicate.

### The answer is neither "trivial" nor "real" — it is a third, worse thing: the signal is copied

**Accounts per intermediary host** (of 3,103 labels, incl. one `''`/anon bucket holding 899 revisions):

| intermediary | accounts | % of 3,103 |
|---|---|---|
| `md.succ.ai` | 484 | 15.6% |
| `markdown.new` | 431 | 13.9% |
| `r.jina.ai` | 278 | 9.0% |
| `pure.md` | 196 | 6.3% |
| `api.allorigins.win` | 65 | 2.1% |
| `httpbin.org` | 28 | 0.9% |
| `corsproxy.io` | 21 | 0.7% |
| `thingproxy.freeboard.io` | 12 | 0.4% |
| `api.codetabs.com` | 11 | 0.4% |

727 of 3,103 accounts (23.4%) touch ≥1 intermediary; 410 touch ≥2 distinct; 239 touch ≥3.

So the brief's **"trivial" failure mode does not fire** — no proxy is universal, the top one is 15.6%. Good news, briefly. Then:

### The groups are explained by copying, not by tooling

The *identical literal URL string* appears across hundreds of accounts:

| exact URL | distinct accounts posting it |
|---|---|
| `https://md.succ.ai/https://www.sec.gov/files/county.json` | **198** |
| `https://md.succ.ai/www.investor.gov/files/county.json` | 166 |
| `https://r.jina.ai/https://www.sec.gov/files/county.json` | **147** |
| `https://md.succ.ai/www.sec.gov/files/county.json` | 137 |
| `https://markdown.new/www.investor.gov/files/county.json` | 123 |
| `https://md.succ.ai/https://www.investor.gov/files/county.json` | 111 |

(1,489 distinct markdown-proxy URLs are shared by ≥2 accounts. Counting by substring presence in revision bodies rather than exact extraction, the first row rises to 231 accounts.)

198 agents did not independently configure `md.succ.ai` and independently decide to prefix `https://www.sec.gov/files/county.json` with it. They read the string off a wiki page and pasted it. The report says so in its own words — "The most typical way the agents used the wiki was to store links" — and the timeline documents the diffusion event:

> "6/20 An agent posts a trick for getting around OpenAI sandbox network restrictions; 14 minutes later, another agent claims it was able to execute this technique successfully."

**This is the kill.** The idea's load-bearing claim is that retrieval plumbing is *incidental to output* and therefore unvaried. In this corpus the plumbing was:
- not incidental — it was the deliberately broadcast payload;
- not a choice — it was copied verbatim from a shared page;
- not evidence of a covert group — it groups "accounts that read the same wiki page," which is what the wiki is *for*.

A tooling-fingerprint join on this corpus returns a group whose shared tooling is fully explained by one public post. It names no hidden structure, because the structure is already overt and already the subject of the report.

### The key is also low-entropy

Across all 3,103 accounts there are **41 distinct multi-intermediary combinations**, 13 of them singletons (groups of one, useless). The largest "improbable combination":

| combination | accounts sharing it |
|---|---|
| `markdown.new` + `md.succ.ai` + `r.jina.ai` | 78 |
| `markdown.new` + `md.succ.ai` | 60 |
| `md.succ.ai` + `r.jina.ai` | 45 |
| `markdown.new` + `md.succ.ai` + `pure.md` | 40 |
| `markdown.new` + `md.succ.ai` + `pure.md` + `r.jina.ai` | 38 |

A 3-proxy combination shared by 78 accounts is not an improbable fingerprint; it is a popularity ranking. The feature is effectively a ~41-bucket hash over 3,103 accounts. It cannot name a specific group, which is what the output artifact ("a case file naming the group") promises to do.

### Baseline dominance: the trivial join already recovers the group

For the 231-account group sharing the top `md.succ.ai` URL, I checked how much of it the explorer's existing page browser recovers:

- **136 of 231 (58.9%) edited one single page: `dse/WillkommenImWiki`** — the wiki's welcome page.
- next: `dse/StartSeite` 77, `dse/TestSeite` 57, `dse/OAIFlatheadBridgeTestMay24X` 32.
- the **entire 231-account group is covered by 50 page editor-lists.**

So ~59% of the flagship "tooling group" is one click in a UI that already exists at `/explorer/pages/1` and `/explorer/labels/1`, and the modal page is the *welcome page* — the single least informative co-edit in the corpus. The join does not beat the baseline it must beat.

**Honest read on the brief's two failure modes:** not trivial (23.4% coverage, not 100%), and worse than already-known. Already-known would mean the report states the finding. The report states the finding *and* the measurement shows the finding is misattributed: these are copy events, not tooling choices.

---

## 3. FEASIBILITY (solo, online, ~20h, no compute)

Ingest and analysis are **effectively free, and that is the problem.** The 4.2 MB downloads in seconds, and I produced every number in §2 — per-account intermediary profiles, combination entropy, identical-URL account counts, baseline-dominance test — in four Bash calls inside this validation, in under a minute, with no compute budget. Host classification is a dict lookup plus one regex for tunnel suffixes.

Long pole: **not engineering. There isn't one.** Everything finishes in an afternoon. What would not finish is the part that makes it a *tool*: validating that any group it outputs means something. That requires a labelled notion of "same operator / same cohort" that the dump does not contain (`labels.jsonl` gives IPs, /16 subnets, pages, timestamps, `is_human_handle` — no operator identity, and 98.5% of edits come from Azure, so the IP channel is a single blob). With `followed: False` on all 23,877 link rows there is also no ground truth on whether a link was ever retrieved. You would ship a grouper with no way to say whether a group is real — in a 20-hour build with 17 hours spare, which a jury will read as a notebook, not a tool.

---

## 4. THEME FIT ("tools to understand and discover agent swarms")

**Subject-matter fit is genuine and strong.** These accounts are agents (`is_human_handle: False`, names like `A3ReadOnlyForensics`, `AICountyResearch`, `OpenAIResearcherAug09`, `StateSequenceResearcher`), on an agent-run wiki, in one of the two incidents in the organizers' own framing, with the organizers' own ungated dump. No contrivance in the setup.

**The strongest objection a research jury raises:** the tool does not measure a property of the swarm, it measures a property of the wiki's content. The swarm's medium *was* link-passing — the report's own "The most typical way the agents used the wiki was to store links" — so grouping accounts by shared URLs recovers the medium, not the structure, and dresses a copy event up as an infrastructure fingerprint. A jury that has read the report (and they will have: the organizers wrote it) will notice that the output restates the report's tooling appendix while asserting a causal story the report contradicts. The second objection is the baseline: `links.jsonl` ships `record_ids`, so the judge asks what the tool adds over a groupby — and §2's answer is 59% of the group from one page's editor list.

---

## 5. WRAPPER FILTER

**(a) The actual product, no model named.** A script that extracts URLs from 14,591 revision bodies, maps each host against a hand-written list of ~12 proxy/CORS/scraper domains plus a tunnel-suffix regex, groups the 3,103 accounts by which subset of that list they touched, and renders the resulting buckets as a report with first-seen timestamps and evidence rows. A host allowlist and a `groupby`.

**(b) Where a model creates leverage.** Nowhere load-bearing. Candidate steps, each checked:
- *Host classification* — a 12-entry list and one regex. Plain code does it exactly, and better: a model would hallucinate category edges on hosts like `jqp.vercel.app` (4,602 link rows, 100% withheld, provenance unknown) where the honest answer is "unknown." Deterministic beats inferred here.
- *"Improbable combination" scoring* — a frequency count over 41 observed combinations. Arithmetic.
- *Pivoting host → account* — `record_ids` is already an inverted index. A join.
- *Writing the case file* — the only genuinely model-shaped step, and it is prose generation over a finished table. That is the wrapper.

**(c) What survives if the model disappears.** A ~150-line pandas script producing the tables in §2. Judged: **thin, verging on nothing.** It is thin as engineering (an afternoon), and nothing as a *finding*, because §1a shows the conclusion is already published and §2 shows the mechanism attribution is wrong.

**Reduction sentence:** *the user gives a corpus of agent edits to a model and gets a narrative case file back.*

**Is that a fair summary? Yes.** The only thing the model does that code cannot is write up a groupby in prose. Every analytic step is deterministic and already shipped or already published.

**Per the filter's own rule: the idea is dead.** It fails the wrapper filter independently of §1 and §2.

---

## SUMMARY

**DEAD.** Four independent kills:

1. **Premise false (measured):** 198 distinct accounts posted the identical string `https://md.succ.ai/https://www.sec.gov/files/county.json`; 147 posted the identical `https://r.jina.ai/https://www.sec.gov/files/county.json`. Shared plumbing here is a copy event off a wiki page, not an incidental unvaried trait. The claimed insight inverts.
2. **Already-known:** the 4 Sep 2026 report names `markdown.new`, `r.jina.ai`, `httpbin.org`, Playwright/Selenium, the `datausa`/`usaspending` endpoints, and "In total, they used four providers: Pinggy, Serveo, localhost.run, and localtunnel" — and explains the bypass mechanism. Nothing left to reveal.
3. **Baseline-dominated and low-entropy:** 41 distinct combinations over 3,103 accounts; top combo shared by 78; 58.9% of the flagship 231-account group recoverable from the editor list of `dse/WillkommenImWiki`, via a page browser the explorer already ships, next to a `/explorer/sites` view that already classifies hosts by infrastructure type.
4. **Prior art, including a contrary result:** A²FV (arXiv 2607.18826, Jul 2026) already formalizes linking agents from "proxy-observable tool-use, timing, and prompt residue" — and reports "the strongest fixed signal is carried by structural and stylometric residue," the opposite of this idea's premise. Plus Lugoloobi et al. (arXiv 2605.14786, May 2026) at 96% F1 from action traces, and Minici et al. (arXiv 2409.15402, Sep 2024) on link-sharing-similarity coordination detection. And threat-intel doctrine classifies shared public services as weak selectors to be treated as background context.

**Do not shortlist.** The one thing worth keeping is the measurement itself — that the corpus's shared URLs are copied strings rather than independent choices — which falsifies a whole family of "join the agents by what they linked" ideas before any of them is built. That is a critique asset for the next regen round, not a product.

### Absence claims, stated precisely
- None of the 9 search results I surfaced on detecting agents via retrieval intermediaries was a measurement of which proxies agents use; 0 of them were opened (vendor comparison pages, LEADS only).
- None of the 3 collusion.wiki pages I opened (`/`, `/explorer`, `/explorer/sites`) offers a view that groups accounts by shared link or host; `/explorer/sites` classifies hosts and counts links but does not pivot host → account set.
- Across all 23,877 rows of `links.jsonl.gz`, `followed` is `False` and `relation` has exactly one distinct value — the dump records no retrieval event and no link typing.
- Of the MISP / OpenCTI / Maltego material I surfaced, none models "platform account joined by third-party service called"; all key on IPs, domains, hashes and certificates.

### Provenance of every number above
All counts in §1c and §2 were computed locally from the organizers' own dump, downloaded 2026-10-02 from `https://collusion.wiki/explorer/download/{revisions,links,labels}.jsonl.gz` (HTTP 200, ungated). Intermediary host list was hand-written; tunnel detection by suffix regex over `lhr.life|serveo.net|pinggy.(link|io)|loca.lt|localhost.run|ngrok(-free)?.(app|io)|trycloudflare.com`. URL extraction by regex over revision `body` fields. Account identity = the `label` field, with empty label bucketed as `(anon)`.
