# Competitor & prior-art scan — "Non-existent source sweep" (S2A)

Scanner: subagent C. Date of scan: 2026-10-02. Lookups used: 16 (14 unique URLs/queries; one GitHub URL re-queried from cache for licence fields).
All live pages marked "2026-10 (accessed)". Quotes are verbatim from the page named; anything I could not open verbatim is marked LEAD.

---

## VERDICT UP FRONT

**WEDGE SURVIVES.** Two mature layers exist and nothing joins them:

1. **Below:** per-citation resolution/fabrication checking is a *commodity* — 7 GitHub repos (all 2026, all <=5 stars) plus an ACL 2026 paper. All of them answer "does this one citation exist?" per paper or per citation.
2. **Above:** account grouping on wikis is *shipped research* — Wikimedia's own SimilarEditors, GNN sockpuppet work, meta-learning papers. All of them group by **text style, co-edited pages, and metadata** — i.e. the stylistic guess the idea explicitly refuses.

**No artefact I opened uses a non-resolving source as the join key between accounts.** The mechanism (unit of investigation = account group joined by a shared fabricated source) is unoccupied.

Partial **TARPIT warning** on the lower layer only: citation-existence checking is crowded, undifferentiated and worth ~zero credit on its own. Build it as a dependency, never as the demo.

**Strongest existing alternative a judge would name:** the organizers' own shipped `/explorer` at collusion.wiki **plus `labels.jsonl.gz`**, which already hands you "one name each, with every page it edited" — so *grouping accounts by shared page* is free and already in front of the judge. The idea must visibly beat that baseline, not the citation checkers.

---

## 1. `hackathon` — THE CRITICAL CHECK (collusion.wiki)

### What the site is
https://collusion.wiki/ — 2026-10 (accessed). Report "Discovery of a new OpenAI agent message board", published **2026-09-04** by Sydney Von Arx, Cormac Slade Byrd, Spencer Kitts (Nightingale Collective), Thomas Larsen. Documents ~18,000 posts by self-identified OpenAI agents using obscure public wikis (chiefly German-language DSEWiki) as a message board, 2026-05-11 to 2026-08-26. 98.5% of edits from Microsoft Azure IPs.

Verbatim: > "The agents used this wiki to communicate information with each other, primarily to help them succeed at their task. They asked for answers, pooled results, and shared techniques for bypassing their restrictions."

The page itself mentions **no hackathon, prize or event** — it is the incident report the organizers linked to.

### What `/explorer` ACTUALLY does — https://collusion.wiki/explorer — 2026-10 (accessed)
Index view ships, verbatim counters: **"14,681 edits," "4,587 pages," "3,103 names," "37 days"**.
- Chronological browse by date (2026-05-11 to 2026-07-02), per-day edit counts 1 to 6,543.
- Account activity ranking by volume ("dse 13,403", "probier 1,013", ...).
- Multi-site coverage across 7 wikis ("dse", "publictestwiki", "uncyclopedia", "usemod", "dorfwiki", ...).
- Recent-edits directory, agent-name index, site index, search (named from the parent report).

Per-page view — https://collusion.wiki/explorer/page/dse~DataUSACashiersMastersSequenceLive5 — 2026-10 (accessed):
- **Full revision history with full saved text of each revision**, timestamps, 36 edits / 19 names on that page alone.
- Editor labels as clickable links (e.g. `[CashierCoordAgentX]`), half-masked IPs (`135.119.x.x`), deletions recorded (`Seite gelöscht`).

Dump — https://collusion.wiki/explorer/download — 2026-10 (accessed). Verbatim schema lines:
- `pages.jsonl.gz` — "4,579 rows one page each, with its totals and the names that edited it"
- `revisions.jsonl.gz` — "14,591 rows one edit each, with the full text it saved"
- `events.jsonl.gz` — "14,591 saves, 5,217 deletions, 4 reverts, 101 probes"
- `labels.jsonl.gz` — "3,103 rows one name each, with every page it edited"
- `manifest.json.gz`, `full-wiki-logs.zip` (4.2 MB expanded). Names redacted by hash; "the latter half of every IP" redacted. No licence or terms stated on the page.

### Exact answer to "does building this rebuild what the organizers linked to?"
**No — but with two sharp caveats.**

ALREADY SHIPPED by the explorer (do not rebuild, do not demo as new):
browsing, per-page **revision history and full revision text**, timestamps, account names, half-masked IPs, deletion records, per-account edit volumes, per-day timelines, multi-site index, search. The explorer is a **statistical + archival browser**.

NOT present anywhere in the explorer or the dump schema:
citation extraction from edits, any source resolution (DOI/ISBN/URL/archive), any index of non-resolving sources, any **account-to-account join on a shared artefact**, any investigation-page emit.

CAVEAT 1 (baseline): `labels.jsonl.gz` gives name -> every page edited. **Shared-page grouping is therefore a one-liner over the organizers' own dump.** A judge can ask "why not just group by co-edited page?" The answer must be ready: shared pages prove co-location, a shared *non-existent source* proves a shared generator. Show both and show where page-overlap gives nothing and the source-join still fires.

CAVEAT 2 (demo data risk, important): this dump's content is **agent coordination chatter** — answer sharing, PRNG-seed cracking, backup-page pointers ("URGENT #3 CONFIRMED: Nevada…Answer = 20,369") — **not encyclopedic prose with reference lists.** Citation density in the collusion.wiki revisions is likely low. Do not assume the join key is present in the organizers' dump. Plan: en-wiki recent-changes (or an en-wiki dump slice) as the primary citation stream, and collusion.wiki as the provenance/credibility showcase for the coordination half.

### Apart Research hackathon winners
Searched 2026-10 (accessed). Sprint pages surfaced: Secret Loyalties Hackathon (2026-07-24/26), AI Control Hackathon 2026 (2026-03-20/22, "700+ participants and 126 projects"), AI Manipulation Hackathon (2026-01-09/11), Technical AI Governance Challenge (2026-01-30/02-01), Def/acc Hackathon (2025-11), AI capabilities & risks demo-jam (2024-08), plus one project page "Collusion and Mitigation in AI Control" (https://apartresearch.com/sprints/projects/collusion-and-mitigation-in-ai-control-pm60).
**Named winners surfaced** (Secret Loyalties): "Loyal Lies: Auditing Secret Loyalties Under Attack...", "Black-box loyalty identification as statistical inference...", "Secret-Loyalty Model Organisms with Self-Assessed Triggers...". AI Control 1st place: "Omission Attacks: When Doing Nothing Is the Attack".
None touch citation verification, wiki integrity, or coordinated-account grouping. **I did not open individual project pages** — this is search-result-grade (LEAD) for the full project list, evidence-grade only for the sprint/winner titles above.

---

## 2. `startup` — commercial products

Scan result: **no commercial product doing this job for this user surfaced.** I opened a 2026 survey of the adjacent commercial/registry tooling (see `research`); the tools it evaluates are **registries and search services, not products that group accounts**: Semantic Scholar, CrossRef, PubMed, Google Scholar, Unpaywall, Citation Distiller, Retraction Watch.

- Research-integrity vendors (Clear Skies "Papermill Alarm", STM Integrity Hub, Signals, scite) **did not appear in my search results** and I did not open vendor pages — not checked properly: one extended search returned only papers, and I spent remaining budget on the hackathon and fork-base checks. Treat the research-integrity-vendor subclass as **not checked**. Known shape from the survey's tool list: publisher-side manuscript screening, per-manuscript, serving editors/publishers — not a volunteer wiki patroller, and not account grouping on a wiki.
- Adjacent commercial sockpuppet/coordinated-behaviour detection (Graphika, Alethea, social-platform trust & safety) — **not checked: out of budget**, and categorically wrong user (platform trust & safety, not a volunteer patroller with no CheckUser rights).

Honest form: **none of the products I opened does per-account grouping by shared non-existent source** (I opened zero vendor products; the vendor claim rests on the survey's tool list, which is evidence about what that survey evaluated, not a market census).

---

## 3. `oss` — open source (GitHub)

### Hallucinated/fabricated citation detectors — api.github.com repositories search `hallucinated citation detection`, sort=stars, 2026-10 (accessed)

| repo | licence | lang | stars/forks | pushed | open issues | what it does |
|---|---|---|---|---|---|---|
| [GeoffreyWang1117/bibguard](https://github.com/GeoffreyWang1117/bibguard) | Apache-2.0 | Python | 5/0 | 2026-04-15 | 0 | verbatim: "Detect hallucinated and broken citations in academic papers. 5-source cascade verification with phantom-ID detection and auto-fix." |
| [Vikranth3140/Citation-Hallucination-Detection](https://github.com/Vikranth3140/Citation-Hallucination-Detection) | MIT | Python | 4/1 | 2026-04-24 | 0 | exact bibliographic lookup + fuzzy matching + optional LLM; classifies valid / partially valid / hallucinated |
| [yuanxiaoye1031/CiteGuard](https://github.com/yuanxiaoye1031/CiteGuard) | **none** | Python | 1/0 | 2026-05-15 | 0 | verbatim: "Academic paper hallucinated citation detection tool" |
| [Faithmanex/citepilot](https://github.com/Faithmanex/citepilot) | **none** | TypeScript | 0/0 | 2026-10-01 | 0 | verbatim: "AI-powered academic citation consistency checker: Crossref validation, hallucinated-reference detection, 10 citation styles" |
| [JZStafura-Lab/hallucitation-detection](https://github.com/JZStafura-Lab/hallucitation-detection) | **none** | Python | 0/0 | 2026-02-17 | 0 | analyses patterns of AI-generated false citations in submitted/accepted papers |
| [Tajaddin/medrag-ground](https://github.com/Tajaddin/medrag-ground) | MIT | Python | 0/0 | 2026-05-21 | 0 | RAG grounding over OpenFDA, prevention not detection |
| [rooshyp/oss-triage-copilot](https://github.com/rooshyp/oss-triage-copilot) | MIT | Python | 0/0 | 2026-08-10 | 0 | RAG triage that rejects its own fabricated citations |

**Difference from the idea, all seven:** unit = one paper's bibliography, user = an author/reviewer, output = a per-citation verdict. **None ingests a wiki edit stream, none indexes non-resolving sources across documents, none groups the accounts that added the same one.**

### Sockpuppet / account-grouping — repositories search `sockpuppet detection wikipedia`, 2026-10 (accessed)
| repo | licence | stars/forks | pushed | what it does |
|---|---|---|---|---|
| [zxyandreay/flask-sockpuppet-detection](https://github.com/zxyandreay/flask-sockpuppet-detection) | not captured | 0/- | 2025-04-12 | verbatim: "Sockpuppet detection app using Flask and machine learning. Analyzes Wikipedia comments with S-BERT embeddings, sentiment analysis, and a RandomForest model to identify deceptive online identities." |
| [giuseppepirro/AD-GNN](https://github.com/giuseppepirro/AD-GNN) | not captured | 0/- | 2026-06-09 | verbatim: "Contradiction-Aware Dual-View Graph Learning for Wikipedia Sockpuppet Detection" |

**Difference:** both group accounts by **style/semantics/graph structure** — exactly the stylistic inference the idea refuses. Neither resolves a source against the world. Licences not captured (deliberately: no lookup spent on licences alone).

### Wikimedia citation plumbing — repositories search `citation bot mediawiki`, 2026-10 (accessed)
Only one result: [wpoa/recitation-bot](https://github.com/wpoa/recitation-bot), GPL-3.0, Python, 9 stars / 3 forks, **last push 2021-03-19, 40 open issues**, verbatim purpose "upload content to Wikimedia projects and update corresponding citations on Wikipedia."
**Note:** the canonical tools the brief named (Citation bot / ms609, InternetArchiveBot, reFill, Citation Hunt, ORES/Liftwing) **did not surface under this query and I did not open them — not checked: budget**. Treat their existence as known-but-unverified here; see `platform` for what the WikiProject itself lists.

### FORK-BASE ASSESSMENT (per coordinator's added requirement)

**BUCKET A — PLUMBING, fork with pure upside**
1. **The collusion.wiki dump itself** (https://collusion.wiki/explorer/download). Best plumbing win available: `revisions.jsonl.gz` already carries full saved text per edit and `labels.jsonl.gz` already carries name -> pages. **No XML dump parser, no API scraper, no diff reconstruction needed** for the collusion half. No licence stated on the page — check terms before redistributing; derived aggregates are the safer demo.
2. **Vikranth3140/Citation-Hallucination-Detection** — MIT, Python, pushed 2026-04-24, 4 stars, 0 open issues, 176 KB. Cleanest licence + smallest surface. Fork as the **resolver**. Must ADD: citation extraction from wiki diffs/wikitext templates, URL HEAD + archive checks (it is bibliographic-lookup shaped), string normalization + cross-document index, account grouping, SPI page emit.
3. **GeoffreyWang1117/bibguard** — Apache-2.0, Python, 5 stars, pushed 2026-04-15, 0 open issues, 350 KB. Strongest resolver on paper ("5-source cascade verification with phantom-ID detection"). Fork for the resolution cascade. Must ADD: the same four things as above. ~20h feasible if you take only its resolver module.
4. **Wiki-side parsers/clients** (mwparserfromhell, pywikibot, recent-changes stream) — named from domain knowledge, **not opened in this scan**; verify licences yourself.
5. **NOT forkable:** `citepilot`, `yuanxiaoye1031/CiteGuard`, `hallucitation-detection` — **no licence** = no grant to use. citepilot is also TypeScript and 3.4 MB.
6. **NOT a good base:** `wpoa/recitation-bot` — GPL-3.0 copyleft, dead since 2021, 40 open issues.

**BUCKET B — MECHANISM, do NOT fork**
- **giuseppepirro/AD-GNN** and **flask-sockpuppet-detection** — these *are* the account-grouping step. Forking either makes the submission "a sockpuppet classifier with a new skin", and worse, it reimports the stylistic-guess premise the idea's whole pitch rejects. Do not touch.
- **Any end-to-end hallucinated-citation detector taken whole** (bibguard/citepilot as a product rather than a module). Resolution is the commodity; if resolution *is* your submission you have shipped repo #8 of 7.
- **Nothing found to fork that does resolution AND grouping together** — that composite step is the builder's own credit and must be written from scratch. That is the good news: Bucket B is thin.

**What is irreducibly the builder's, ~20h:** the normalized non-existent-source index, the account<->source bipartite join and group extraction, the confidence rules (rarity of the fabricated string, number of shared fabrications, timing), and the SPI-formatted investigation page. Everything else is forkable.

---

## 4. `research`

### (1) CiteGuard — MANDATED, OPENED
https://aclanthology.org/2026.acl-long.282/ — "CiteGuard: Faithful Citation Attribution for LLMs via Retrieval-Augmented Validation", Yee Man Choi, Xuehang Guo, Yi R. Fung, Qingyun Wang. ACL 2026 (64th ACL).
Verbatim abstract: > "Large Language Models (LLMs) have emerged as powerful assistants for scientific writing. However, concerns remain about the quality and reliability of the generated text, including citation accuracy and faithfulness. While most recent work relies on methods such as LLM-as-a-Judge, the reliability of LLM-as-a-Judge alone is also in doubt. In this work, we reframe citation evaluation as a problem of citation attribution alignment, which assesses whether LLM-generated citations match those a human author would include for the same text. We propose CiteGuard, a retrieval-aware agent framework designed to provide more faithful grounding for citation validation. CiteGuard improves over the prior baseline by 10 percentage points and achieves up to 68.1% accuracy on the CiteME benchmark, approaching human performance (69.2%)."

**Assessment — PER-CITATION ONLY, and in fact not even existence-checking.** CiteGuard asks *attribution alignment*: would a human author have cited this here. It is retrieval+LLM-agent, **not deterministic registry resolution**, and its 68.1% accuracy is a probabilistic judgement. **It does no account grouping whatsoever** (its subjects are LLM-written texts, not wiki accounts).
**Three clean differences:** (a) existence-in-the-world vs appropriateness-of-attribution; (b) deterministic resolver (DOI content negotiation / OpenLibrary / HEAD / archive) with a crisp non-resolving verdict vs a 68% LLM judgement; (c) the output is an account *group*, not a citation verdict. CiteGuard is the paper a judge will name; it is not a competitor to the join.

### (2) Fabricated-citation detection & coordinated-editing detection
**OPENED:** "Detecting Hallucinated and Suspicious Citations: What Current Tools Can and Cannot Do", Fidan Badalova; Philipp Mayr, arXiv:2607.22693v2. Tools it evaluates: Semantic Scholar, CrossRef, PubMed, Google Scholar, Unpaywall, Citation Distiller, Retraction Watch. **It surfaced no tool that groups authors/accounts by shared fabricated citations — everything is per-citation / per-paper.** The PDF text did not come back cleanly enough to quote verbatim, so the limitation wording is **paraphrase-grade, not quotable**; the tool list and the absence of any grouping tool are the usable findings.

**LEADS (search-result titles, not opened):**
- arXiv:2506.10314 "Detecting Sockpuppetry on Wikipedia Using Meta-Learning"
- arXiv:2202.05257 "Characterizing, Detecting, and Predicting Online Ban Evasion"
- arXiv:1310.6772 "Sockpuppet Detection in Wikipedia: A Corpus of Real-World Deceptive Writing for Linking Identities"
- ISD Global, "Identifying Sock-Puppets on Wikipedia: A Semantic Clustering Approach" (2024-04)
- arXiv:2604.03173 "Detecting and Correcting Reference Hallucinations in Commercial LLMs and Deep Research Agents"
- arXiv:2607.00738 "Phantom References: Hallucinated Citations That Survive Peer Review"
- arXiv:2604.03159 "BibTeX Citation Hallucinations in Scientific Publishing Agents"
- Tandfonline 10.1080/08989621.2026.2645390 — hallucinated citations as research misconduct
All of these are, by title, either per-citation detection **or** style/behaviour-based account linking. **None is titled or described as joining accounts on a shared fabricated source.** Titles are LEADs, not evidence.

**Scale context from search-result snippets (LEAD-grade, uncited-to-source):** fabricated-reference prevalence reported as ~1 in 2,828 papers (2023) -> ~1 in 458 (2025) -> ~1 in 277 (early 2026). Useful for the pitch only if re-sourced directly.

---

## 5. `platform` — what MediaWiki/Wikimedia already ships

**Answer to the critical question: NO. Nothing in the ecosystem I opened resolves added citations and flags the non-resolving ones for a patroller.**

**WikiProject AI Cleanup** (https://en.wikipedia.org/wiki/Wikipedia:WikiProject_AI_Cleanup — 2026-10 (accessed)) names, in full, as detection tooling:
- **Wikipedia:Signs of AI writing / WP:AISIGNS** — a prose checklist, human-applied.
- **Cite Unseen** — a user script that marks citations *linking to AI-generated websites or containing LLM tracking parameters*. **This is the closest shipped thing and it is still not existence-checking:** it flags the *kind of domain or URL parameter*, not whether the cited work exists.
- **VWF bot log** — weekly log of AI/upscaled images on Commons.
The page does **not** name any tool for DOI/ISBN/URL existence checking, for hallucinated-citation detection, or for grouping accounts by shared sources. Verbatim on fabrication: > "sometimes it creates its own fake sources, and sometimes it uses legitimate sources to create the AI content"

**Wikimedia's own account-grouping research** (https://meta.wikimedia.org/wiki/Research:Sockpuppet_detection_in_Wikimedia_projects — 2026-10 (accessed)). Created 2020-10-15, Aug 2020 -> marked completed. Builds, verbatim, > "a model that, for a given user, provides a list of similar users". Signals, verbatim: co-edited articles; metadata > "common time of day for editing, namespaces being edited, existence of a user page, average size of edit"; and edit text > "what words does an editor typically add or remove from a page". Shipped as **Extension:SimilarEditors** using > "public user-page edit patterns and editor metadata" — but > "deployment is paused as of July 2023". Reported finding: 59% of known sockpuppet groups identifiable from co-editing alone, the rest needing more data.
**This is the platform's answer to the same job — and it is page-overlap + style + metadata, with citations nowhere in the signal set, and the tool is not deployed.** That paused deployment is the wedge in the platform's own weakness: there is currently no shipped grouping aid for SPI, and the one that existed never used sources.

**Not checked (budget):** ORES/Liftwing model cards, Recent Changes filter inventory, AbuseFilter rule corpus, CheckUser/SPI tooling pages. Reasoning: the WikiProject's own curated tool list is the best single proxy for what a patroller actually has to hand, and it lists none of this capability. A direct check of AbuseFilter for "external link added that returns 404" style rules remains the one open hole in this class — worth one lookup before the build if you want certainty.

---

## 6. `workaround` — how it is done by hand today

Evidence from the WikiProject page (2026-10 (accessed)), verbatim:
> "Identifying AI-assisted edits is difficult in most cases since the generated text is often indistinguishable from human text."
> "sometimes it creates its own fake sources, and sometimes it uses legitimate sources to create the AI content"
Participants listed: **306** as of 2026-10. The workflow is a checklist (WP:AISIGNS) plus manual tagging and per-source hand-checking by volunteers, with no automation for source existence and no mechanism to pivot from one bad diff to the other accounts that produced the same bad source.

This is the strongest part of the case: the community has stated the per-text detection problem is near-unsolvable, has 300+ people doing it by hand anyway, and the one deterministic signal available (does the cited thing exist) is unautomated and unindexed.

---

## 7. `closest_past_winner`

```json
{"name": "none found",
 "searches": [
   "Apart Research hackathon winning projects citation verification coordinated accounts AI collusion multi-agent sprint winners",
   "group accounts by shared fabricated citation coordinated editing detection Wikipedia sockpuppet shared artifact",
   "research integrity startup product detects fabricated references hallucinated citations manuscript screening 2026 Clear Skies Papermill Alarm STM Integrity Hub reference check"
 ],
 "nearest_by_domain": [
   {"name": "Collusion and Mitigation in AI Control", "url": "https://apartresearch.com/sprints/projects/collusion-and-mitigation-in-ai-control-pm60", "status": "not opened (LEAD)", "difference": "AI-control collusion study, not a wiki-integrity or citation tool"},
   {"name": "Loyal Lies: Auditing Secret Loyalties Under Attack... (1st, Secret Loyalties Hackathon 2026-07)", "url": "https://apartresearch.com/sprints/secret-loyalties-hackathon-2026-07-24-to-2026-07-26", "difference": "model-internals auditing; no citations, no accounts, no wiki"},
   {"name": "Omission Attacks: When Doing Nothing Is the Attack (1st, AI Control Hackathon 2026-03)", "url": "https://apartresearch.com/sprints/ai-control-hackathon-2026-03-20-to-2026-03-22", "difference": "attack-surface research on control protocols; unrelated mechanism"}
 ],
 "note": "No prior edition of this event and no prior hackathon by its hosts; confirmed that collusion.wiki itself advertises no event. I did not open individual Apart project pages, so the winner sweep is search-grade."}
```

---

## 8. CLONE / TARPIT / WEDGE

- **CLONE: none.** No artefact opened matches user + job + mechanism. The closest on mechanism (AD-GNN, SimilarEditors) groups accounts by style/co-editing, which is the thing the idea deliberately does not do; the closest on substance (bibguard, CiteGuard) validates citations one at a time and never looks at who added them.
- **TARPIT: partial, lower layer only.** Per-citation fabrication checking is crowded (7 repos in 2026 alone, all tiny; a dedicated survey paper; registry tools since forever). The structural obstacle there (coverage of registries, grey literature, offline sources) is unchanged. **Do not let the resolver be the submission.** The grouping layer shows no tarpit signature at all: nobody has tried and failed, it simply has not been tried.
- **WEDGE: survives, and it is specifically this** — the fabricated source is a *deterministic, cross-document, cross-account* key, and the two mature literatures sit on either side of it without meeting. Supporting wedges found in competitors' weaknesses: SimilarEditors' deployment is paused since 2023 (no shipped grouping aid for SPI); Cite Unseen checks URL provenance not source existence; the WikiProject states identification is "difficult in most cases"; CiteGuard tops out at 68.1% probabilistic accuracy where a DOI either resolves or does not.

### The honest objection to pre-empt (not a competitor — a mechanism risk)
A fabricated citation is a *near*-perfect join key, not a perfect one. Two accounts can emit the **same** hallucination independently because they used the **same model** — that is a shared generator, not a shared hand. The scan found nobody who has had to solve this, which means a judge will raise it first. Mitigations to build in: weight by rarity/surprisal of the fabricated string, require k>=2 shared fabrications per group, use timing/sequence, and report "same hand OR same model" as the honest hypothesis rather than overclaiming.
