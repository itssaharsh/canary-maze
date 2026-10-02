# discovery.md — problem discovery and validation
Subagent D · hackathon mode · depth: full (halved research budget) · written 2026-10-02
Build window: Sat 2026-10-03 10:00 PT → Sun 2026-10-04 17:00 PT (~31h elapsed, ~20 working hours)

---

## 1. Requester information

**My context contained nothing about who requested this, their team, or their past
projects — and I did not look.** I made no memory/profile calls, did not search for
the event, its gallery, its hosts or its sponsors, and chose every problem on the
evidence only. The only identity-ish item present in my context was a bare email
address attached automatically by the harness as account metadata; I ignored it and
did not use it in any query or source.

---

## 2. The defaults (full list in `defaults.md`)

22 pre-registered defaults: **D1** swarm discovery crawler · **D2** better transcript
summarizer · **D3** agent trajectory visualizer · **D4** standard question battery ·
**D5** AI whistleblowing channel · **D6** information-spread tracer · **D7** OSINT /
forensics tracer · **D8** incident aggregator dataset *(D1–D8 are the organizer's own
suggestions — the most converged ideas in the room)* · **D9** generic multi-agent
observability dashboard · **D10** chat-with-the-corpus RAG · **D11** agent-text
detector · **D12** multi-agent simulation sandbox · **D13** embedding/UMAP cluster map
· **D14** LLM-judge intent scorer · **D15** anomaly detector over agent logs ·
**D16** agent passport / on-chain attestations · **D17** browser extension labelling
agent posts · **D18** auto-written incident report · **D19** MCP server over the corpus
· **D20** Slack/Discord digest bot · **D21** agentic SOC triage · **D22** swarm
red-team harness.

**The reduction sentence to beat, pre-registered:** *"the user gives 170k agent
transcripts to a model and gets a summary / a list of suspicious clusters back."*

Generation rule I held to: **every seed in this run came from a user group's own
vocabulary, never from the theme's vocabulary.** I never searched "agent swarm
tool"; I searched what maintainers, patrollers, instance admins and site operators
actually type. (One exception, declared: I ran one `agent swarm` HN query to find
operators' own complaints, and it produced the single best quote in the ledger, E14.)

---

## 3. Audience map — each group's own words and watering holes

| # | Group (their self-description) | Words they actually use | Watering holes |
|---|---|---|---|
| G1 | **Open-source maintainer** — "I maintain X in my free time" | "triage", "slop", "drive-by PR", "security report", "bug bounty", "HackerOne", "I stopped accepting PRs", "avalanche" | maintainer blogs (daniel.haxx.se), HN, GitHub issues, project mailing lists |
| G2 | **Wiki patroller / cleanup volunteer** — "I patrol recent changes" | "revert", "new page patrol", "sockpuppet investigation", "signs of AI writing", "LLM-generated", "copyvio", "hallucinated citation", "tag it" | Wikipedia WikiProject pages, Village Pump, maintenance categories, de/fr/other-language equivalents |
| G3 | **Instance admin / forum moderator** — "I run a small instance", "I'm an admin of a 2,000-user forum" | "spam wave", "defederate", "greylisting", "mod queue", "sign-up API endpoint", "honeypot field", "temp email domains", "suspend" | mastodon/mastodon GitHub issues, meta.discourse.org, fediverse admin threads |
| G4 | **Site / API operator** — "my origin", "my bandwidth bill" | "rate-limited", "robots.txt", "user-agent", "scraper", "rinsing my API", "cat and mouse", "externalising your costs", "autoscaling bill" | HN, Wikimedia Diff, Read the Docs blog, Anubis issues, status pages |
| G5 | **Platform anti-abuse / T&S engineer** — "Safety Processing", "Platform Integrity" | "coordinated inauthentic behaviour", "actor clustering", "enforcement", "signals", "false positive rate" | company job boards (Greenhouse/Lever), T&S conference talks, transparency reports |
| G6 | **Engineer running multi-agent systems** — "I chain 5 agents" | "trace", "replay", "hand-off", "malformed state", "authority boundaries", "I get paged", "false positives" | HN, GitHub repos/issues for agent runtimes, observability vendors' docs |
| G7 | **Package-registry admin** — "PyPI admins" | "malware report", "takedown", "free-form email report", "trusted reporter", "scales poorly" | pypi/warehouse issues, registry blogs |
| G8 | **Operator of an agent-populated venue** — "agents claim beats, file signals" | "bot farm", "signals", "coordinated accounts", "must explain" | the venue's own repo/issues (aibtcdev/agent-news) |
| G9 | **Incident investigator / researcher** — reconstructing what happened | "provenance", "reproducible", "case file", "chain of custody", "we can't tell if it's the same swarm" | incident databases, post-mortems, HN threads on specific incidents |

**Non-US / non-specialist coverage.** Reached: a Dutch forum admin on meta.discourse
(E16), a UN body's statistics API operator (E14, UNCTADstat — Geneva), the
fediverse admin population (Europe-weighted, consumer-adjacent, E11–E13), and an
individual self-publishing author whose book income went to zero (E7,
consumer-adjacent). **Not reached:** a non-English-language wiki patroller — I tried
`de.wikipedia.org/wiki/Wikipedia:WikiProjekt_KI-Inhalte` and it 404'd (no such page
under that name), and I did not have budget to find the correct German/French page.
That is a real gap: German-language patrollers are the group closest to one of the
two incidents in the theme and I have **zero** opened evidence from them.

---
## 4. The full problem pool — 12 candidates across 9 user groups

Lens accounting (by **triggering** lens): L1 painful workflow 3/12 · L2 money on a worse
fix 1/12 · L3 bad incumbent 1/12 · L4 rules/deadlines 1/12 · L5 newly possible 2/12 ·
L6 back office 1/12 · L7 underserved 2/12 · capability lens 1/12. No lens exceeds half;
rules trigger 1/12; capability lens 1/12. 5 of 12 are AI-shaped (L8 secondary) — under
half, so the search was not technology-led.

---

### P1 — KEEP · Maintainer cannot tell a campaign from a coincidence
- **User + moment:** a volunteer open-source maintainer, at the moment a new PR or
  security report lands in a queue they work through on their own time.
- **Job:** decide, in under a minute, whether this submission deserves human review.
- **Pain:** the decision is made one submission at a time with no view of the batch.
  A plausible-looking report costs the reviewer 30 minutes to 3 hours and pulls in
  3–4 people; producing it costs the sender nothing. Maintainers cannot see that the
  item in front of them is #14 of 112 opened by one operator in six hours.
- **Frequency:** curl: ~2 security submissions/week, ~20% AI slop in 2025 (E1).
  Maintainers describe "thousands of AI generated pull requests and bug reports" (E3).
- **Intensity:** from curl's own figures — ~21 slop reports/yr × 3–4 people ×
  0.5–3 h each ≈ **30–250 volunteer person-hours a year on one 7-person team**
  *(my arithmetic from their numbers, marked as inference, not their claim)*.
  Second-order cost: curl considered dropping monetary bounty rewards (E1); one
  maintainer closed his project to pull requests entirely (E2).
- **Current workaround:** read everything; then policy changes — stop paying bounties,
  stop accepting PRs, close to contributions.
- **Spend:** curl's bounty programme has paid "over 90,000 USD" since 2019 for 81 real
  vulnerabilities (E1) — real money whose signal-to-noise is now the problem.
- **Lenses:** L1 (triggering), L2, L8
- **Evidence:** **VALIDATED** — E1 (curl, primary, with numbers) + E2/E3/E4 (three
  further independent maintainers) = 4 orgs/individuals, 2025-07 → 2026-09.
- **Prior-art probe:** GitHub issue search for AI-spam tooling returned only two
  near-empty issues, both 0 reactions (E5) — no maintainer-side batch/campaign tool
  surfaced. Platform-side spam filters exist but operate per item, not per campaign.
  **Gap: nothing opened groups incoming submissions into campaigns for the maintainer.**
- **Counter-evidence:** some maintainers have "solved" it by exiting (E2) — a solved
  problem by subtraction, which caps willingness to adopt yet another tool.
- **Missing voices:** paid maintainers at foundations; maintainers on GitLab/Codeberg;
  any non-English project.

### P2 — KEEP · Wiki patroller sees edits, not editors-in-concert
- **User + moment:** a WikiProject AI Cleanup volunteer, at the moment they open a
  diff flagged as possibly machine-written.
- **Job:** decide whether to tag, revert, or escalate — and whether the same hand is
  at work on other articles.
- **Pain:** the project's own page says identification "is difficult in most cases
  since the generated text is often indistinguishable from human text" (E6). The
  tooling is a maintenance category and a template; the grouping of related edits is
  done in a volunteer's head.
- **Frequency:** flagged-article category grew from 1 article (March 2025) to 1,155 in
  September 2026 alone; 7,619 total across 19 monthly subcategories (E7).
- **Intensity:** 7,619 flagged articles against 300+ listed participants ≈ **25
  articles of cleanup each** *(my arithmetic, inference)*. Each is a sourcing audit.
- **Current workaround:** manual tagging, user warnings, source-authenticity checks by
  hand; a 300-person volunteer project standing in for a tool (E6).
- **Spend:** unpaid volunteer labour at scale — the classic underserved-group signal.
- **Lenses:** L7 (triggering), L1, L4 (secondary: EU AI Act Art. 50 marking duties
  from 2026-08-02, E8)
- **Evidence:** **VALIDATED** — E6 (project's own account of its own operations) +
  E7 (the platform's own counts) + E8 (independent rule). Note E6/E7 are both
  Wikipedia-hosted; I count them as one org's self-account plus one platform
  measurement and lean on E8 and E15 for independence.
- **Prior-art probe:** 11 open-source coordinated-inauthentic-behaviour tools exist
  (E9) — **every one of them scores human-social-media signals** (textual, temporal,
  behavioural, network); 10 of 11 have 0 stars and the 11th has 1. A GitHub repo
  search for model/prompt fingerprinting returned **0 repositories** (E10).
  **Gap: nothing opened joins edits on artifact-level keys a machine leaves behind.**
- **Counter-evidence:** the 300-person project is itself a working social workaround;
  Wikipedia is hostile to automated enforcement, so any tool must stop at evidence.
- **Missing voices:** non-English patrollers (my `de.wikipedia` fetch 404'd);
  Wikimedia Foundation T&S staff.

### P3 — KEEP · Instance admin can act on accounts, not on waves
- **User + moment:** a fediverse instance admin at 3am, when dozens of accounts appear
  and start posting across hundreds of servers.
- **Job:** stop the wave without cutting off legitimate neighbours.
- **Pain:** tooling is per-account and per-instance. The admin's own words: "spammer
  creates dozens of accounts per minute across hundreds of servers" (E11). The only
  blunt instrument that scales is defederating an entire server.
- **Frequency:** waves; one user documented 78 spam messages from unique accounts in
  12 hours (E12).
- **Intensity:** reactive manual suspension; collateral damage from defederation —
  real users lose contact with real communities.
- **Current workaround:** defederate whole instances; hand-written keyword filters;
  requests for email-style server reputation / greylisting (E13).
- **Spend:** none visible in money; the spend is admin attention and lost federation.
- **Lenses:** L3 (triggering — long-open high-reaction issues on the leader), L1
- **Evidence:** **VALIDATED** — E11 (31 reactions, open since 2024-02), E13 (25
  reactions, open), E12 (26 reactions) — three independent requesters on the
  incumbent's own tracker, plus E16 from a different platform's admins (Discourse).
- **Prior-art probe:** the incumbent (Mastodon) has left the instance-wide filtering
  request open for ~2.5 years (E11) — that is the probe result: the leader has not
  shipped it. Commercial anti-spam does not speak ActivityPub.
  **Gap: no cohort-level action primitive in the admin's own tool.**
- **Counter-evidence:** these issues predate the agent era (2024) — the wave problem
  is older than agent swarms, so "why now" must be about *volume and plausibility*,
  not about the existence of the problem.
- **Missing voices:** large-instance admins with paid staff; Bluesky moderators.

### P4 — KEEP · Site operator cannot tell one swarm from many strangers
- **User + moment:** the operator of a site or public API, in the hour a traffic
  anomaly is burning money, deciding what to block.
- **Job:** attribute the traffic to an actor so the response fits the cause.
- **Pain:** stated exactly by a statistics-API operator: the agents "did get
  rate-limited ('please stop rinsing my site') and continued rinsing the API with
  requests regardless", and he cannot tell "whether it's the same swarm, let alone
  the same agents" (E14). Another operator: agents now match real-browser traffic
  characteristics, so the usual tells are gone (E15).
- **Frequency:** Read the Docs sees "misconfigured data scrapers weekly" (E17).
- **Intensity:** Wikimedia — multimedia bandwidth **+50% since January 2024**; bots
  are ~35% of pageviews but **"at least 65% of this resource-consuming traffic"**
  (E18). Read the Docs took an autoscaling-targeted attack designed to hit non-CDN
  URLs (E17). An individual author's book income went "from being enough for me to
  live off (2024) to zero (2026)" while traffic rose, all of it crawlers (E19).
- **Current workaround:** proof-of-work gates (Anubis: 22,995 stars, 743 forks, 379
  open issues, created 2025-03-17, E20), hand-maintained robots.txt and firewall
  rules, rate limits that are simply ignored (E14).
- **Spend:** third parties have built an install-guide repo, a managed-hosting CLI and
  a Helm chart around Anubis (E21) — independent effort on the workaround; and a
  freelancer sells "AI crawler access audits" starting at **$25** (E22).
- **Lenses:** L1 (triggering), L5
- **Evidence:** **VALIDATED (strongest in the pool)** — five independent
  organisations/individuals: UNCTAD (E14), Wikimedia Foundation (E18), Read the Docs
  (E17), Techaro/Anubis adopters (E20/E21), an individual publisher (E19).
- **Prior-art probe (2 lookups):** Cloudflare **AI Crawl Control** shows *which named
  AI services* access your content, robots.txt compliance and allow/block policies
  (E23); **Cloudflare signed agents** (GA 2025-08-28) cryptographically verifies a
  short allowlist — ChatGPT agent, Goose, Browserbase, Anchor Browser, Cloudflare
  Browser Rendering (E24). Neither page I opened describes attributing *undeclared*
  requests to a common operator or correlating several agents acting together.
  **Gap: the declared tier is solved; the undeclared tier — which is all of it that
  matters — has no attribution primitive, and nothing exists for a non-CDN operator
  holding only their own log file.**
- **Counter-evidence:** this is a very well-funded field (Cloudflare, DataDome, HUMAN);
  the obvious answer "buy bot management" is available to anyone behind a big CDN.
  Segment that survives: operators not behind one, and operators who need *evidence*
  rather than *blocking*.
- **Missing voices:** CDN/bot-management staff; the agent operators themselves.

### P9 — HYPOTHESIS (keep, flagged) · Agent-venue operator cannot audit its own agent population
- **User + moment:** whoever runs a venue whose *members are agents*, when a
  participant alleges a bot farm.
- **Job:** establish whether N accounts are N independent operators or one.
- **Pain:** on an agent-run news network, a participant filed: seven accounts
  "submitted exactly 10 signals each on April 17, 2026, all using the same AI model",
  and asked what safeguards exist against coordinated accounts (E25). The venue has
  61 open issues and 24 forks (E26).
- **Frequency:** unknown — one opened instance.
- **Intensity:** unknown; reputational for the venue.
- **Current workaround:** a human noticing a suspicious pattern and filing an issue.
- **Spend:** none opened.
- **Lenses:** L5 (triggering), L3
- **Evidence:** **HYPOTHESIS** — one opened item, specific and quantitative, 0
  reactions, speaking only for its author. I spent one extra lookup (E26) and found no
  second independent venue. Phrased to fail: *"operators of agent-populated venues
  will adopt a coordination audit if it needs no change to agent code."*
- **Prior-art probe:** inherits P2's probe (E9, E10). Nothing venue-side opened.
- **Counter-evidence:** the venue is tiny (1 star); may be a toy. Do not build *for*
  it — it is a **demo venue**, not a market.
- **Missing voices:** every other agent marketplace; none opened.

### P5 — KILLED (`crowded` + `no segment evidence`) · Platform T&S actor-clustering
- **User + moment:** a Safety Processing engineer clustering actors behind coordinated
  agent activity.
- **Evidence found:** 11 open safety/security engineering roles at one platform
  (E27) — spend, but a single employer, and no first-person account from this
  segment that I could open.
- **Kill reason:** (a) **one org only**, so not validated; (b) the field is the
  best-funded one adjacent to this theme (commercial CIB detection, bot management)
  and I opened no page showing a gap these teams feel; (c) they build in-house.
  Lookups spent: E27, E9, E23, E24.

### P6 — KILLED (`crowded`) · Debugging your own multi-agent system
- **User + moment:** an engineer whose 5-agent chain broke in the middle.
- **Evidence found (genuinely good):** "you chain 5 agents together, something in the
  middle breaks... you have no idea what happened" — and he built Binex (E28);
  another built a Flight Recorder for replay (E29); another named the real failure as
  "Agent A correctly doing its job, but passing slightly malformed state to Agent B"
  and said standard observability shows execution paths, not "authority boundaries"
  (E30).
- **Kill reason:** **the market answered in 2026.** A repo search for multi-agent
  observability created since 2026-01-01 returns, among others, `open-multi-agent`
  (6,972 stars, "durable approvals and verifiable run records"), `kiwiq` (2,201),
  `databuff` (691), `agents-observe` (688), `Octopoda-OS` (487, "loop detection,
  hash-chained audit trails") (E31). Two of my three evidence items are *people who
  already shipped the product*. No visible gap I could validate in 20 hours.

### P7 — KILLED (`single source`, demoted) · Alert fatigue at swarm scale
- **User + moment:** an on-call engineer with a 10k-agent fleet.
- **Evidence:** one comment — "when you have a 10k agent swarm you'd be getting a page
  every few minutes. Most of them would be false positives" (E32).
- **Kill reason:** one opened item, speaking for its author only; and it sits inside
  P6's crowded field. Not worth a second lookup against that prior art.

### P8 — KILLED (`stale evidence`) · Package-registry abuse-report triage
- **User + moment:** a registry admin reading a free-form malware report email.
- **Evidence:** registry staff's own words — reporting "is performed by sending an
  email to the PyPI maintainers... This scales poorly, as the report itself is
  free-form, requires interpretation on the behalf of administrators" (E33); an
  earlier staff issue documenting 78 spam accounts from distinct IPs (E34).
- **Kill reason:** the two best items are from **2022-11 and 2018-02** — far outside
  the 24-month window — and I did not have budget to verify whether the registry has
  since shipped the reporting API it proposed. Killing rather than guessing.

### P10 — KILLED as a standalone (`obligation ≠ pain`), retained as a why-now
- **The rule, verified:** EU AI Act Article 50 — providers must ensure synthetic
  output is "marked in a machine-readable format and detectable as artificially
  generated or manipulated", deployers must disclose artificially generated content,
  and users must know when they are interacting with AI; **obligations apply from
  2 August 2026** (E8).
- **Kill reason:** a rule proves an obligation, not pain. The behaviour items I have
  (E6/E7 volunteers labelling by hand, E16 admins hand-building honeypots) belong to
  P2 and P3, so Article 50 is carried as a **forced-change why-now** on those, not as
  its own problem. Keeps rules/deadlines at 1/12 of the pool.

### P11 — KILLED as a standalone (`folded into P4`) · The two-tier agent-identity world
- **The change, verified:** Cloudflare signed agents GA 2025-08-28, covering five
  named agents via Web Bot Auth HTTP message signatures (E24); the Web Bot Auth
  *architecture* draft reached v05 on 2026-03-02 and has since **expired and been
  replaced** by `draft-meunier-webbotauth-httpsig-protocol` (E35).
- **Kill reason:** it is the enabling change behind P4, not a separate user problem.
  Folded in as P4's why-now, including the honest read that the protocol is still in
  flux.

### P12 — KILLED as a standalone (`merged into P3`) · Small-forum admin, consumer-adjacent
- **User + moment:** the admin of a ~2,000-user hobby forum, the morning after a
  signup.
- **Evidence:** one admin reports automated signups at ~one per day using temporary
  email domains, accounts that post within hours (E16); another admin explains the
  mechanism — "those spam bots are using automated post requests to the sign up api
  endpoint" — and describes an unselectable dropdown value accidentally working "like
  a honeypot" (E36).
- **Kill reason:** real, consumer-adjacent and non-US (Dutch admin), but the job is
  the same job as P3 at a tenth of the volume. **Merged into P3 as its low-end
  segment** rather than counted twice. Its value: it proves the cohort-action job
  exists on a second, unrelated platform (independent org for P3's validation).

---
## 5. Evidence ledger

All items were opened. `how: opened` throughout. HN comment IDs link as
`news.ycombinator.com/item?id=<id>`. Dates: articles/issues by publication or creation;
live pages as "2026-10 (accessed)".

| ID | Type | Text (paraphrase unless in quotes) | Strength | Speaker | About | Org | URL | Date | Segment | Source type |
|---|---|---|---|---|---|---|---|---|---|---|
| E1 | FACT + EVIDENCE | In 2025 curl received ~2 security submissions/week; "20% of all submissions" were AI slop and valid vulnerabilities fell to "about 5% of the submissions in 2025". Base = all security submissions. 7-person security team; each report engages "3-4 persons" for "30 minutes, sometimes up to an hour or three. Each." Bounty has paid "over 90,000 USD" for 81 vulnerabilities since 2019. Considering dropping monetary rewards. | STRONG | Daniel Stenberg (curl lead) | curl's own security-team operations | curl | https://daniel.haxx.se/blog/2025/07/14/death-by-a-thousand-slops/ | 2025-07-14 | exact | maintainer blog (primary) |
| E2 | EVIDENCE | A maintainer stopped accepting pull requests outright: "When you waste time trying to deal with 'AI' generated pull-requests, in your free time, you might change your mind." | MODERATE | stevekemp | his own project | independent maintainer | https://news.ycombinator.com/item?id=47414995 | 2026-03-17 | exact | forum comment |
| E3 | EVIDENCE | "What they do want, however, is to not have to spend time on the thousands of AI generated pull requests and bug reports." | MODERATE | matsemann | maintainers generally | independent | https://news.ycombinator.com/item?id=49776083 | 2026-09-20 | exact | forum comment |
| E4 | EVIDENCE | "the developers increasingly need to get through an avalanche of AI-generated pull requests rather than, say, code new features." Related: Krei-se on being unable to ask questions of an absent contributor (id 48944580). | MODERATE | tarkin2 | OSS ecosystem | independent | https://news.ycombinator.com/item?id=48416962 | 2026-06-05 | neighboring | forum comment |
| E5 | FACT | A GitHub issue search for AI-generated-spam tooling returned two issues only, both 0 reactions (`Obsesion3D/FullBlending` #1, 2026-06-28; `ainergiz/xfeed` #140, 2026-01-03, a *request* for AI-spam detection that does not exist yet). | WEAK (absence) | GitHub search index | public issue corpus | — | https://api.github.com/search/issues?q=AI+generated+spam+in:title+is:issue+is:open+sort:reactions-desc | 2026-10 (accessed) | — | code-host API |
| E6 | EVIDENCE | WikiProject AI Cleanup, founded December 2023, lists 300+ participants; tasks are manual (tag, remove, warn, verify sources). Its own assessment: identifying AI-assisted edits "is difficult in most cases since the generated text is often indistinguishable from human text." | MODERATE | the WikiProject itself | its own operations | Wikipedia community | https://en.wikipedia.org/wiki/Wikipedia:WikiProject_AI_Cleanup | 2026-10 (accessed) | exact | community project page |
| E7 | FACT | "All articles: 7,619" in Category:Articles containing suspected AI-generated texts; 19 monthly subcategories from March 2025 (1 article) to October 2026; September 2026 alone holds 1,155. Count stated as of 2026-06-23 on the page, with subcategories extending later — so 7,619 is a floor. | MODERATE | Wikipedia maintenance category | flagged article volume | Wikipedia community | https://en.wikipedia.org/wiki/Category:Articles_containing_suspected_AI-generated_texts | 2026-10 (accessed) | exact | platform measurement |
| E8 | FACT | EU AI Act Art. 50: synthetic output must be "marked in a machine-readable format and detectable as artificially generated or manipulated"; solutions must be "effective, interoperable, robust and reliable as far as this is technically feasible"; deployers must disclose artificially generated content; disclosure "at the latest at the time of the first interaction or exposure". **Obligations apply from 2 August 2026.** | FACT (rule text) | EU legislator (via AI Act explorer) | providers and deployers in the EU | EU | https://artificialintelligenceact.eu/article/50/ | in force 2026-08-02; accessed 2026-10 | neighboring | regulation |
| E9 | FACT | 11 open-source coordinated-inauthentic-behaviour tools, created 2025-08 → 2026-08. All score human-social-media signals (textual/temporal/behavioural/network, Leiden community detection, Sentence-BERT similarity). Stars: one has 1, the other ten have 0. | MODERATE (prior art) | GitHub search index | the CIB-tooling field | — | https://api.github.com/search/repositories?q=coordinated+inauthentic+behavior+detection&sort=stars&order=desc | 2026-10 (accessed) | — | code-host API |
| E10 | FACT | A repo search for LLM provenance / model-fingerprint tooling returned `total_count: 0`, `incomplete_results: false`. **Absence claim, correctly scoped: zero repositories matched these terms — not proof no such tool exists.** | WEAK (absence) | GitHub search index | — | — | https://api.github.com/search/repositories?q=LLM+provenance+fingerprint+detect+which+model | 2026-10 (accessed) | — | code-host API |
| E11 | EVIDENCE | Mastodon #29256, open, 31 reactions: admin reports a "spammer creates dozens of accounts per minute across hundreds of servers" and asks for instance-level keyword/phrase/URL filtering so they need not defederate whole instances. | MODERATE | instance admin | their own instance | independent admin | https://github.com/mastodon/mastodon/issues/29256 | 2024-02-17 | exact | incumbent issue tracker |
| E12 | EVIDENCE | Mastodon #29723, 26 reactions: a user received "seventy-eight" spam messages from unique bot accounts in 12 hours. | MODERATE | affected user | one targeted account | independent | https://github.com/mastodon/mastodon/issues/29723 | 2024-03-22 | neighboring | incumbent issue tracker |
| E13 | EVIDENCE | Mastodon #29266, open, 25 reactions: proposes greylisting for new servers, "spam attack is getting increasingly worse", asks for email-style server reputation. | MODERATE | instance admin | the fediverse | independent admin | https://github.com/mastodon/mastodon/issues/29266 | 2024-02-18 | exact | incumbent issue tracker |
| E14 | EVIDENCE | Operator of the UNCTADstat API: agents "did get rate-limited ('please stop rinsing my site') and continued rinsing the API with requests regardless"; he cannot tell "whether it's the same swarm, let alone the same agents"; what he observes are "the actions of someone, or something, that won't take 'no' for an answer". | MODERATE | roarch | a UN statistics API's own traffic | UNCTAD (non-US, Geneva) | https://news.ycombinator.com/item?id=49868377 | 2026-09-27 | exact | forum comment |
| E15 | EVIDENCE | "Agents are very good at comparing traffic characteristics from a real browser and a headless/automation browser and getting it to behave in the same manner"; scraping prevention is "a cat and mouse game" currently favouring agents. | MODERATE | carsoon | detection practice | independent | https://news.ycombinator.com/item?id=49930215 | 2026-10-02 | exact | forum comment |
| E16 | EVIDENCE | Forum admin: automated spam signups at ~one per day across forums with ~2,000 users, using temporary email domains, with topic/reply posting within hours. | MODERATE | guidoleenders (admin) | their own forums | independent admin (NL) | https://meta.discourse.org/t/292707 | 2024-01-24 | exact | vendor community forum |
| E17 | EVIDENCE | Read the Docs engineer: they see misconfigured data scrapers **weekly**; one attack was deliberately engineered to exploit autoscaling by targeting non-CDN URLs (404s/302s), causing financial damage. | MODERATE | davidfischer (Read the Docs) | their own infrastructure | Read the Docs | https://news.ycombinator.com/item?id=49630503 | 2026-09-09 | exact | forum comment (employee) |
| E18 | FACT + EVIDENCE | "Since January 2024, we have seen the bandwidth used for downloading multimedia content grow by 50%." Bot pageviews ≈ **35% of total pageviews**, but "at least 65% of this resource-consuming traffic" (i.e. of expensive, non-cached traffic) is bots. Framing: "our content is free, our infrastructure is not: We need to act now." | STRONG | Wikimedia Foundation SRE/engineering (Mueller, Danis, Lavagetto) | Wikimedia's own infrastructure | Wikimedia Foundation | https://diff.wikimedia.org/2025/04/01/how-crawlers-impact-the-operations-of-the-wikimedia-projects/ | 2025-04-01 | exact | org's own engineering blog (primary) |
| E19 | EVIDENCE | Self-publishing author: "income from my book sales went from being enough for me to live off (2024) to zero (2026)" while site traffic rose, nearly all of it AI crawlers generating no ad revenue. | MODERATE | runarberg | his own income | individual publisher | https://news.ycombinator.com/item?id=49927533 | 2026-10-01 | exact (consumer-adjacent) | forum comment |
| E20 | FACT | Anubis — "Weighs the soul of incoming HTTP requests to stop AI crawlers" — 22,995 stars, 743 forks, 379 open issues, created 2025-03-17, last push 2026-09-30, MIT. | STRONG (effort on a worse fix) | repo metadata | adoption of a PoW crawler gate | Techaro | https://api.github.com/repos/TecharoHQ/anubis | 2026-10 (accessed) | exact | code-host API |
| E21 | EVIDENCE | Third parties have built an Anubis install guide for Nginx Proxy Manager (`teodorgross/anubis-autoinstall`, 2025-07), a managed-hosting CLI (`tsueri/nine-manage-anubis` for nine.ch Managed Servers, 2026-08, 9 open issues), and a Traefik/K8s Helm chart with "optional Anubis bot protection" (2026-09). | MODERATE (same workaround at several independent orgs) | three independent authors incl. a Swiss hosting provider | their own deployments | independent / nine.ch (non-US) | https://api.github.com/search/repositories?q=anubis+bot+protection&sort=stars&order=desc | 2026-10 (accessed) | exact | code-host API |
| E22 | EVIDENCE | A freelancer advertises AI-crawler access audits — which bots (GPTBot, ClaudeBot, PerplexityBot, Google-Extended) are permitted via robots.txt — "starting at $25". | MODERATE (money changing hands) | bzcomak | their own service | independent | https://news.ycombinator.com/item?id=49922924 | 2026-10-01 | exact | forum comment |
| E23 | FACT | Cloudflare AI Crawl Control: "See which AI services access your content", robots.txt-compliance tracking, per-crawler allow/block policies, Pay Per Crawl (private beta). Available on all plans. **The documentation I opened does not describe attributing requests to an operator, nor correlating several agents acting together.** | FACT (prior art + absence, scoped to the page opened) | Cloudflare docs | Cloudflare's product | Cloudflare | https://developers.cloudflare.com/ai-crawl-control/ | 2026-10 (accessed) | — | vendor docs |
| E24 | FACT | Cloudflare "signed agents" announced **2025-08-28**, extending verified bots; agents sign requests via Web Bot Auth HTTP message signatures which Cloudflare validates. Named at launch: ChatGPT agent, Goose (Block), Browserbase, Anchor Browser, Cloudflare Browser Rendering. Security-rules integration "coming soon". | FACT (dated platform change) | Cloudflare | their own launch | Cloudflare | https://blog.cloudflare.com/signed-agents/ | 2025-08-28 | — | vendor blog (vendor claim) |
| E25 | EVIDENCE | On an agent-run news network, a filed report alleges seven accounts "submitted exactly 10 signals each on April 17, 2026, all using the same AI model", with simultaneous activation, and asks what safeguards exist against automated account coordination. | MODERATE (single, specific) | a participant | seven accounts on that venue | aibtcdev | https://github.com/aibtcdev/agent-news/issues (closed issue, 2026-04-18) | 2026-04-18 | exact | venue's own tracker |
| E26 | FACT | `aibtcdev/agent-news`: "AI agent intelligence network. Agents claim beats, file signals, compile briefs inscribed on Bitcoin." 1 star, 24 forks, 61 open issues, created 2026-02-26, last push 2026-09-09, TypeScript. | WEAK | repo metadata | the venue's scale | aibtcdev | https://api.github.com/repos/aibtcdev/agent-news | 2026-10 (accessed) | exact | code-host API |
| E27 | EVIDENCE | One platform's public board lists 11 open engineering roles in safety/security/platform integrity (incl. "Senior Software Engineer, Safety Processing", "Staff Software Engineer, Safety Experience", "Engineering Manager, Machine Learning (Safety)"). | MODERATE (spend, single employer) | Discord job board | that employer's hiring | Discord | https://boards-api.greenhouse.io/v1/boards/discord/jobs | 2026-10 (accessed) | neighboring | job board API |
| E28 | EVIDENCE | "debugging multi-agent pipelines was driving me crazy" — "you chain 5 agents together, something in the middle breaks... you have no idea what happened"; built Binex, a runtime with trace/debug/replay/diff. | MODERATE (self-built workaround) | alexli1807 | his own pipelines | independent | https://news.ycombinator.com/item?id=47315314 | 2026-03-09 | exact | forum comment |
| E29 | EVIDENCE | "Every time I fixed a bug, I had to re-run the entire pipeline" — built a Flight Recorder for caching and replay. | MODERATE (self-built workaround) | whitepaper27 | his own pipelines | independent | https://news.ycombinator.com/item?id=47444309 | 2026-03-19 | exact | forum comment |
| E30 | EVIDENCE | Hardest failure is "Agent A correctly doing its job, but passing slightly malformed state to Agent B"; standard observability shows execution paths, not "authority boundaries" between agents. | MODERATE | chirdeeps | his own systems | independent | https://news.ycombinator.com/item?id=47371712 | 2026-03-14 | exact | forum comment |
| E31 | FACT | Multi-agent observability repos created since 2026-01-01 include `open-multi-agent` (6,972 stars, "durable approvals and verifiable run records"), `kiwiq` (2,201), `databuff` (691, OTel-based APM with multi-agent troubleshooting), `agents-observe` (688, real-time observability of sessions and multi-agents), `Octopoda-OS` (487, "persistent memory, loop detection, hash-chained audit trails"), `opsrobot` (135), `pi-harness` (122). **All assume you instrument your own runtime.** | STRONG (prior art) | GitHub search index | the 2026 agent-observability field | — | https://api.github.com/search/repositories?q=multi-agent+observability+created:>2026-01-01&sort=stars&order=desc | 2026-10 (accessed) | — | code-host API |
| E32 | EVIDENCE | "when you have a 10k agent swarm you'd be getting a page every few minutes. Most of them would be false positives" | WEAK→MODERATE (single) | RomanKornev | hypothetical/own experience | independent | https://news.ycombinator.com/item?id=49862194 | 2026-09-27 | exact | forum comment |
| E33 | EVIDENCE | PyPI staff: malware reporting "is performed by sending an email to the PyPI maintainers... This scales poorly, as the report itself is free-form, requires interpretation on the behalf of administrators." Proposes a standardized API for trusted reporters. | MODERATE but STALE | PyPI staff (di) | PyPI's own operations | PyPI / PSF | https://github.com/pypi/warehouse/issues/12612 | 2022-11 | exact | registry issue tracker |
| E34 | EVIDENCE | PyPI staff documented attackers operating 78 spam accounts from distinct IPs; automated classification, admin review interfaces and crowdsourced reporting were all absent at the time. | MODERATE but STALE | PyPI staff (ewdurbin) | PyPI's own operations | PyPI / PSF | https://github.com/pypi/warehouse/issues/2982 | 2018-02 | exact | registry issue tracker |
| E35 | FACT | `draft-meunier-web-bot-auth-architecture` (Meunier, Major): abstract aims to "allow automated HTTP clients to cryptographically sign outbound requests, enabling HTTP servers to verify their identity with confidence". v05 last updated **2026-03-02**; the draft is **expired and archived**, replaced by `draft-meunier-webbotauth-httpsig-protocol`. | FACT | IETF Datatracker | the standard's status | IETF | https://datatracker.ietf.org/doc/draft-meunier-web-bot-auth-architecture/ | 2026-03-02 (v05); accessed 2026-10 | — | standards body |
| E36 | EVIDENCE | Forum admin on the mechanism: "those spam bots are using automated post requests to the sign up api endpoint" (bypassing front-end validators); an unselectable custom dropdown value accidentally functioned "like a honeypot". | MODERATE | Lilly (admin) | spam bots on Discourse sites | independent admin | https://meta.discourse.org/t/402557 | 2026-05-09 | exact | vendor community forum |
| E37 | FACT | "A Training-free Method for LLM Text Attribution": "Verifying the provenance of text is increasingly important for firms, educational institutions, and online platforms as Large Language Models (LLMs) produce output that is nearly indistinguishable from human-generated content." Proves Type I and Type II errors "decay exponentially with text length"; reports only "strong overall performance" — **the abstract gives no accuracy figure, no model count and no text-length threshold.** | WEAK (framing, unmeasured in the abstract) | the authors | LLM text attribution | arXiv preprint | https://arxiv.org/abs/2501.02406 | submitted 2025-01-04 | — | paper |
| E38 | EVIDENCE | Companies operating "clusters with thousands of agents" expose them to untrusted internet input, creating blind spots where an attacker could redirect swarm behaviour via prompt injection. | WEAK (opinion, no measurement) | openasocket | industry generally | independent | https://news.ycombinator.com/item?id=49857864 | 2026-09-26 | neighboring | forum comment |

**Counter-evidence summary, kept next to its problems:** P4 sits in a well-funded field
(E23, E24); P6 is already served by shipped products (E31); P3's issues predate agents
(2024) so its why-now must be about volume, not novelty; P2's community workaround (E6)
is itself effective enough that volunteers may not adopt a tool; E37 shows the academic
attribution literature does **not** hand me a usable accuracy number, so no solution
here may assume one.

**Who is missing from my sources:** non-English wiki patrollers (my one attempt 404'd);
CDN / bot-management engineers; Wikimedia Foundation T&S staff as distinct from SRE;
agent *operators* (the people running the swarms — not one source speaks for them);
large-platform T&S engineers in their own words; and anyone from the gated research
corpus mentioned in the brief, which I did not request or use.

---
## 6. Solutions for the kept problems

Note on audience group G9 (incident investigators): it is in the audience map but has
**no kept problem**. The two solutions I generated for it (S14-A below) died at Stage
4b as wrappers, and rather than lower the bar I dropped the group and let the
investigator's need be served by the evidence bundles inside S4-A and S2-A. Reported
as a thin spot rather than patched over.

---
### P4 → S4-A · "Swarm Ledger" — operator-side attribution from your own log file
- **Core workflow:** *input* your own access log (nginx/Caddy/Apache/CDN export, or a
  tailer) → *action* partition requests into candidate **operators** using join keys
  that survive user-agent spoofing (TLS/JA4 fingerprint where present, HTTP/2 SETTINGS
  and header order, Web Bot Auth `keyid` when present, ASN + /24, path-sequence
  shingles, inter-request timing lockstep across distinct IPs); assign each cluster a
  **stable `swarm_id` that persists across runs**; score each cluster for
  *coordination* (do distinct IPs traverse the same unusual path order inside a
  window?) → *output* an append-only ledger (one row per cluster per day plus the
  evidence rows that justify it), a human-readable case card, and an exported ruleset
  (robots.txt stanza, nginx `map`, CDN expression) that targets **the cluster, not the
  user-agent**.
- **Insight:** the incumbents answer "which *named* service is this" (E23, E24). Nobody
  answers "are these 9,000 requests one actor?" — which is the operator's literal
  question (E14). The keys that answer it are already in the log; what is missing is a
  product that keeps a **stable identity over time**, so the operator can say "the same
  swarm is back and it is now using 40 ASNs."
- **Replaces:** grepping logs during an incident; blanket proof-of-work gates that tax
  every human visitor (E20, E21); $25 robots.txt audits (E22).
- **Behaviour change:** point the tool at a log once a day (or install a tailer) rather
  than only reacting mid-incident.
- **Mechanism family:** detect + verify (stable identity over time).
- **Capabilities needed → simplest technology:** multi-format log parsing → Go/Python
  + a handful of regexes; clustering → union-find on exact keys plus DBSCAN on
  sequence shingles (scikit-learn); ledger → SQLite with an append-only table; rule
  export → string templates; case card → a small LLM, optional. **Not needed and
  explicitly avoided:** blockchain, AR/VR, IoT, multi-agent orchestration, fine-tuning.
- **Why-now object:**
  `kind: protocol/platform` · `date: 2025-08-28` ·
  `change: Cloudflare signed agents went GA, verifying agent identity by HTTP message
  signature for a named allowlist (ChatGPT agent, Goose, Browserbase, Anchor Browser,
  CF Browser Rendering), with the underlying Web Bot Auth architecture draft still in
  flux (v05 2026-03-02, now expired and replaced)` ·
  `threshold: coverage — exactly 5 agents became cryptographically identifiable while
  bots account for "at least 65%" of Wikimedia's resource-consuming traffic and
  multimedia bandwidth is +50% since Jan 2024; so the identifiable fraction is a
  rounding error against the volume` ·
  `who_couldnt_before: an operator not behind a large CDN, holding only their own log
  file — UNCTAD's statistics API, Read the Docs, a self-hosted docs site` ·
  `sentence: "Since 2025-08-28, cryptographic agent signing lets operators verify a
  five-agent allowlist, which splits traffic into a tiny verifiable tier and a large
  undeclared tier; earlier attempts (user-agent allowlists, IP reputation) failed
  because the identifier was self-declared, and signing removes that for the declared
  tier only — so the operator's live question moved from 'which crawler is this' to
  'is this one actor', and nothing answers it."`
  **Absorption check:** I opened Cloudflare's AI Crawl Control docs (E23) — it ships
  named-crawler visibility, robots.txt compliance and allow/block, and the page says
  nothing about operator attribution or correlating agents acting together. Cloudflare
  could add it for *their* customers; the segment it cannot serve is the operator who
  is not their customer and who needs a portable evidence record.
- **Fingerprint:** `domain:` web infrastructure / abuse · `user:` site or API operator,
  in the hour a traffic anomaly is costing money · `job:` attribute traffic to an actor
  so the response fits the cause · `mechanism:` the unit of analysis changes from
  request-and-user-agent to a persistent operator cluster with its own record ·
  `mechanism_family:` detect+verify · `buyer_or_demo:` paste a real log, watch 9,000
  requests collapse into 3 named swarms, one of which is still live.

### P4 → S4-B · "Canary Maze" — prove agents shared information, don't guess
- **Core workflow:** *input* your site plus a token mint → *action* serve per-visitor
  unique crawlable artifacts (unique canary URLs, unique fact-tokens embedded in prose,
  unique link ids), recording every mint against the fingerprint it was minted for →
  watch for **sightings**: a token being requested, referred, queried or posted back by
  a *different* fingerprint → *output* a propagation graph — "token minted for A at T0,
  fetched by B at T0+4m, by C at T0+9m" — plus an evidence bundle with raw request
  records.
- **Insight:** detection asks "do these look alike?" — which is exactly what the 11
  existing CIB tools do (E9) and exactly what is failing as agents learn to look like
  browsers (E15). Planting asks "did they talk?" A secret only one visitor could have
  learned turns a similarity guess into a **propagation fact**. This is the
  organizer's information-spread idea (default D6) at a different moment, for a
  different user, with a different mechanism: in the wild, on your own property, with
  no transcripts at all.
- **Replaces:** fingerprint-similarity heuristics; the operator's shrug in E14.
- **Behaviour change:** the operator agrees to serve a small amount of decoy surface.
- **Mechanism family:** create (manufacture the evidence) + verify.
- **Capabilities needed → simplest technology:** token mint → HMAC over
  (path, fingerprint, salt); serving → 30 lines of middleware; sighting ledger →
  SQLite; graph → a static D3/SVG render. The verbatim path needs **no model at all**.
- **Why-now object:**
  `kind: behavior (adversary side), anchored to a dated platform change` ·
  `date: 2025-08-28 (signing GA) with operator reports 2026-09-27 and 2026-10-02` ·
  `change: passive classification of automated traffic is losing — operators report
  agents matching real-browser traffic characteristics and ignoring rate limits — and
  the industry's own answer was to move to cryptographic signing, which only covers
  agents that volunteer` ·
  `threshold: accuracy relative to the cost of an error — a passive classifier's
  precision degrades to coin-flip when the client is indistinguishable from a browser,
  whereas a canary sighting has a false-positive rate bounded by the collision
  probability of the HMAC, i.e. effectively zero` ·
  `who_couldnt_before: operators who need *evidence* rather than *blocking* — a UN
  agency, a foundation, a journalist, anyone who must show a third party what happened` ·
  `sentence: "Since 2025-08-28 the industry's answer to agent identity is voluntary
  signing, and by 2026-09 operators report agents indistinguishable from browsers and
  ignoring rate limits; earlier attempts at passive fingerprint detection failed
  because the adversary controls every observable signal, which planting a secret the
  adversary does not control removes."`
  **Absorption check:** honeytokens are an old security primitive (canary tokens) but
  nothing in E23/E24 or the 11 CIB repos (E9) mints *per-visitor* tokens to measure
  propagation **between automated clients**. The risk is a security vendor extending
  canary tokens sideways; the wedge is the propagation graph and the per-fingerprint
  mint, not the token.
- **Fingerprint:** `domain:` web infrastructure / forensics · `user:` site operator who
  must show someone else what happened, at the moment they are asked to prove it ·
  `job:` establish that two automated clients shared information · `mechanism:`
  coordination stops being inferred from similarity and becomes recorded from a planted
  secret · `mechanism_family:` create+verify · `buyer_or_demo:` a live graph filling in
  as a second agent fetches a URL only the first was ever shown.

### P4 → S4-C · "Ask the log" (generated for completeness; **killed at Stage 4b**)
Feed the access log to a model, ask what the swarm was doing, print the answer.
Included because it is the default this room will produce; see §7 for its death.

### P1 → S1-A · "Batch card" — make the campaign visible at triage time
- **Core workflow:** *input* a webhook on every issue/PR opened in the repos where the
  app is installed → *action* compute (i) a normalized minhash of title+body against a
  rolling cross-install index, (ii) the author's cross-repo burst profile from the
  public events API, (iii) structural tells (identical scaffolding, identical section
  headers, the same non-resolving reference) → *output* if the item belongs to a batch:
  a label, a **batch record**, and one collapsed comment — "submission 14 of 112 opened
  by 9 accounts in 6h across 40 repos; 9 already closed as not-planned" — plus a
  maintainer-set rule (label only / require a checkbox / close with template).
- **Insight:** the quality of one submission is arguable; the **shape of the batch** is
  not. A maintainer who can see the batch spends ten seconds instead of ninety minutes,
  and never has to accuse an individual of anything. Platform tooling is per-item (E5).
- **Replaces:** reading everything (E1); quitting (E2); dropping bounty money (E1).
- **Behaviour change:** install an app and accept labels it writes.
- **Mechanism family:** inform + prevent.
- **Capabilities needed → simplest technology:** GitHub App webhooks → Octokit;
  near-duplicate detection → minhash/LSH (datasketch); paraphrase matching →
  sentence embeddings; records → SQLite; comment → a template. No fine-tuning.
- **Why-now object:**
  `kind: economics (cost of producing a plausible submission fell below the cost of
  reviewing it) — measured, not asserted` · `date: 2025-07-14 (the measurement)` ·
  `change: curl published that ~20% of its 2025 security submissions were AI slop
  while valid findings fell to ~5% of submissions` ·
  `threshold: cost per completed task — a reviewer spends 0.5–3h × 3–4 people per
  report; the sender spends ~0. By curl's own numbers that is roughly 30–250 volunteer
  person-hours a year on one 7-person team (my arithmetic from their figures)` ·
  `who_couldnt_before: a volunteer maintainer who sees one queue and cannot see that
  the same batch is hitting 40 other projects` ·
  `sentence: "Since 2025-07-14 curl has measured that ~20% of its security submissions
  are machine-generated slop while valid findings fell to ~5%, so maintainers now face
  a review budget problem rather than a quality problem; earlier attempts (per-repo
  spam filters, bounty rules) failed because the unit of judgement was the single
  report, which a cross-repo batch index removes."`
  **Absorption check:** GitHub is the incumbent and could ship this; it has the data.
  The wedge is that the index spans **installs across orgs**, and the product's job is
  to tell a maintainer "this is a campaign" — a statement a platform is institutionally
  reluctant to make about its own users.
- **Fingerprint:** `domain:` open-source operations · `user:` volunteer maintainer at
  the moment a submission lands in their queue · `job:` decide in under a minute whether
  this deserves human review · `mechanism:` the triage unit changes from one submission
  to the batch it belongs to, with the batch persisted as a record · `mechanism_family:`
  inform+prevent · `buyer_or_demo:` open a real PR in a demo repo and watch the batch
  card name the other 111.

### P1 → S1-B · "Reciprocal evidence exchange" (stretch, connect family)
- **Core workflow:** maintainers publish **signed batch fingerprints** (hashes of
  normalized bodies + burst signatures, no content, no accusations); subscribers'
  queues auto-label matches. *Output:* a shared, append-only fingerprint feed.
- **Insight:** one maintainer sees 14 of 112; ten maintainers see the campaign.
- **Replaces:** private frustration and ad-hoc Mastodon warnings.
- **Behaviour change:** maintainers agree to publish hashes (deliberately not content).
- **Mechanism family:** connect. **Network effects** are the point.
- **Why-now object:** `kind: none` — `opening:` there is no shared abuse-signal channel
  between open-source projects; the signing/attestation primitives exist (E24, E35) and
  the demand is documented (E1–E4), but nothing I opened provides the channel.
- **Honest flag:** classic two-sided first-supply problem. In a 20-hour build, supply
  must be seeded from your own installs plus public closed-as-spam archives, and that
  must be disclosed, not hidden behind a logo wall.
- **Fingerprint:** `domain:` open-source operations · `user:` maintainer, the week after
  a wave · `job:` warn peers without publishing accusations · `mechanism:` abuse signal
  becomes a shared, privacy-preserving feed instead of private knowledge ·
  `mechanism_family:` connect · `buyer_or_demo:` project B's queue labels a submission
  it has never seen, because project A saw it 20 minutes ago.

### P2 → S2-A · "Non-existent source sweep" — the fabrication is the join key
- **Core workflow:** *input* the public recent-changes stream (EventStreams) or a dump →
  *action* extract every citation added in each edit (DOI, ISBN, URL, journal+title),
  **resolve each one deterministically** (DOI resolver, ISBN lookup, HTTP HEAD, archive
  check), index the non-resolving ones by normalized string, then group **accounts that
  added the same non-existent source** → *output* a pre-filled investigation page: the
  account group, the shared non-existent sources, the diffs, the timeline, formatted for
  the community's own sockpuppet-investigation workflow.
- **Insight:** a fabricated citation is a near-perfect join key. Two accounts citing the
  same journal article that does not exist is not a stylistic guess; it is a shared
  artifact. The project itself says the *text* is indistinguishable (E6) and the 11
  existing CIB tools score text and timing (E9) — so sidestep text entirely and join on
  the fabrication, which is both checkable and shared.
- **Replaces:** manual source-authenticity checks (E6); per-article tagging that never
  aggregates into an actor.
- **Behaviour change:** patrollers start from a group case instead of a single diff.
- **Mechanism family:** detect + verify, writing into the community's real system of
  record (an investigation page).
- **Capabilities needed → simplest technology:** streaming ingest → the wiki's own
  EventStreams/API; citation extraction from messy wikitext → a small model (rules get
  the templates, not the prose); resolution → `doi.org` content negotiation, OpenLibrary,
  HTTP HEAD, with aggressive caching; index → SQLite; page generation → templates.
- **Why-now object:**
  `kind: data availability + behavior` · `date: curve measured Mar 2025 → Sep 2026;
  regulatory anchor 2026-08-02` ·
  `change: the flagged-article category went from 1 article (Mar 2025) to 1,155 in Sep
  2026, 7,619 in total, against a 300-person volunteer project; and from 2026-08-02 EU
  Art. 50 requires synthetic content to be machine-readably marked — which these edits
  are not, making unmarked fabrication the detectable residue` ·
  `threshold: coverage — 7,619 flagged articles ÷ ~300 volunteers ≈ 25 sourcing audits
  each (my arithmetic); grouping by shared fabrication collapses many articles into one
  case` ·
  `who_couldnt_before: a patroller who can check one article's sources in an evening but
  cannot ask "who else cited this book that does not exist?"` ·
  `sentence: "Since Mar 2025 the suspected-AI-text backlog grew from 1 article to 7,619
  with 1,155 added in Sep 2026 alone, so volunteer patrollers now face ~25 sourcing
  audits each; earlier attempts (AI-text detectors) failed because generated text is
  indistinguishable from human text — which resolving the citations removes, since a
  source either exists or it does not."`
  **Absorption check:** the wiki ecosystem ships citation *formatting* and link-rot
  bots; the step nobody automates is treating non-resolution as an **identity key across
  accounts**. Risk: a community bot operator builds it — which would be a good outcome
  and is a reason to ship it as a community-shaped tool, not a SaaS.
- **Fingerprint:** `domain:` knowledge-commons integrity · `user:` volunteer patroller
  at the moment they open a flagged diff · `job:` find out whether the same hand is at
  work elsewhere, with evidence a community will accept · `mechanism:` the unit of
  investigation changes from an article to a group of accounts joined by a shared
  fabricated source · `mechanism_family:` detect+verify · `buyer_or_demo:` one
  non-existent book, six accounts, one generated case page.

### P2 → S2-B · "Fabrication registry" (connect family, different user)
- **Core workflow:** publish the resolved-as-non-existent citation index as an open
  dataset + a one-call API, so *other* venues — journals, Q&A sites, package docs,
  course submissions — can check an incoming citation against fabrications already seen
  somewhere else. *Output:* a growing public registry with provenance per entry.
- **Insight:** the same fabricated sources recur across venues because they come from
  the same generators; the first venue to resolve one should pay the cost once for
  everybody.
- **Replaces:** every venue resolving the same dead DOI independently.
- **Behaviour change:** venues add one lookup to their review step.
- **Mechanism family:** connect + inform. **Accumulated history is the asset.**
- **Why-now object:** `kind: none` — `opening:` the resolution work is already being
  done ad hoc by volunteers (E6) and thrown away; nothing I opened aggregates it.
- **Fingerprint:** `domain:` scholarly/content integrity · `user:` a reviewer at any
  venue, at the moment a citation arrives · `job:` check a source cheaply · `mechanism:`
  one-off manual resolution becomes a shared accumulating record · `mechanism_family:`
  connect · `buyer_or_demo:` the same fake citation flagged on a second, unrelated site.

### P3 → S3-A · "Cohort console" — make the wave the unit of action
- **Core workflow:** *input* signup and first-post telemetry the admin already has
  (registration path — front-end form vs direct API endpoint, field values, email
  domain, timing, IP/ASN, invite source) → *action* cluster recent signups into cohorts
  on deterministic keys (same endpoint + same field-value pattern + same email-domain
  generation pattern + arrival inside a window) → *output* a cohort object: one card,
  one decision (approve / hold / suspend / require email) applied atomically to every
  member, a **reversible record** of what was done and why, and a saved cohort signature
  that auto-holds future matches.
- **Insight:** the admin's tool operates on accounts; the attacker operates on waves
  (E11, E13). Making the cohort the unit of action *is* the product — and the key is
  already named by admins themselves: the bots "are using automated post requests to
  the sign up api endpoint" rather than the validated front end (E36).
- **Replaces:** defederating whole servers (collateral damage, E11); one-by-one
  suspension; hand-built honeypot fields (E36).
- **Behaviour change:** act on cohorts and work a held queue; trust a grouping enough to
  act on it — which is why every action is reversible as a set.
- **Mechanism family:** automate + prevent, with repair (set-wise undo).
- **Capabilities needed → simplest technology:** read-only admin API or log ingest →
  HTTP; clustering → union-find on exact keys; generated-name family detection → a small
  classifier or embeddings; queue + action log → SQLite + a plain web UI. Runs as a
  sidecar; no fork of the platform.
- **Why-now object:**
  `kind: none` · `opening: the incumbent's own tracker has carried the
  instance-wide-filtering request for ~2.5 years (opened 2024-02-17, 31 reactions,
  still open) and the greylisting request alongside it (2024-02-18, 25 reactions). The
  problem is older than agent swarms; what changed is that the text each account posts
  now passes human reading, so the content-based filters admins asked for in 2024 are
  the wrong lever, and the registration-path keys they already have are the right one.`
  · `threshold: precision — a keyword filter's precision collapses when every account's
  text is generated separately; endpoint/field-pattern keys are unaffected by text
  quality` · `who_couldnt_before: an unpaid admin of a 2,000-user forum or a small
  instance who has no data team` ·
  `sentence (forced-change form does not apply; stated as an opening): "No dated
  capability change enables this — the opening is that the incumbent has left the
  cohort-action request open since 2024-02-17 while admins hand-build honeypot fields,
  so the gap is product work, not new technology."`
  **Absorption check:** Mastodon could ship it; it has not in 2.5 years. Discourse ships
  per-user spam tooling and its admins are still inventing honeypots by accident (E36).
- **Fingerprint:** `domain:` community operations · `user:` unpaid instance/forum admin
  at 3am during a signup wave · `job:` stop the wave without cutting off legitimate
  neighbours · `mechanism:` moderation's unit of action changes from the account to the
  cohort, with a reversible record · `mechanism_family:` automate+prevent ·
  `buyer_or_demo:` 40 signups collapse into 2 cohorts; one click holds 38 of them; one
  click undoes it.

### P9 (hypothesis) → S9-A · "Participation receipts" for an agent-populated venue
- **Core workflow:** *input* the venue's submission endpoint → *action* the venue issues
  a per-window nonce and requires each agent submission to carry a signature over
  (nonce, operator key, declared model id); unsigned submissions are accepted but
  marked → *output* a weekly coordination report in which accounts sharing an operator
  key or model id are grouped **by arithmetic rather than inference**, plus a public
  "declared vs undeclared" ratio for the venue.
- **Insight:** in a venue whose members are agents, you can change admission — unlike on
  the open web. The cheapest honest swarm-visibility tool makes declaring nearly free
  and non-declaration itself a visible signal. It answers the exact question a
  participant asked when seven accounts filed exactly ten signals each on the same day
  with the same model (E25).
- **Replaces:** a human noticing a pattern and filing an issue (E25).
- **Behaviour change:** agent operators must sign; the venue can require it because it
  controls admission.
- **Mechanism family:** prevent + verify + transact.
- **Capabilities needed → simplest technology:** HTTP message signatures (RFC 9421
  family, the same primitive as Web Bot Auth) → an off-the-shelf library; key registry →
  SQLite; report → SQL. **No model in the loop at all.**
- **Why-now object:**
  `kind: protocol` · `date: 2025-08-28 (signed-agents GA using Web Bot Auth HTTP message
  signatures), draft architecture v05 2026-03-02` ·
  `change: request signing for automated clients moved from a bespoke idea to a deployed
  primitive with libraries and a live standards track` ·
  `threshold: cost — signing a submission is one library call and a key, instead of a
  bespoke identity scheme, so a hobby venue can require it` ·
  `who_couldnt_before: the operator of a small agent-populated venue with no identity
  infrastructure` ·
  `sentence: "Since 2025-08-28 HTTP message signing for automated clients is a deployed,
  library-supported primitive, so a small agent-populated venue can require signed
  participation receipts at near-zero cost; earlier attempts (CAPTCHAs, email
  verification) failed because they assumed a human, which signing does not."`
- **Honest flag:** P9 is a HYPOTHESIS with one opened evidence item. Build this as a
  second surface or as the **demo venue** for S4-B, not as the main bet.
- **Fingerprint:** `domain:` agent marketplaces/venues · `user:` venue operator when a
  participant alleges a bot farm · `job:` establish whether N accounts are one operator
  · `mechanism:` coordination becomes a recorded fact at admission instead of an
  after-the-fact inference · `mechanism_family:` prevent+verify · `buyer_or_demo:` seven
  accounts resolve to one key, live, in a report the venue can publish.

### G9 → S14-A · "Swarm brief" / standard question battery (**killed at Stage 4b**)
Point it at a corpus or a venue dump, run ~20 pre-written questions, get a brief.
This is defaults D2/D4/D7 fused. See §7 for its death and why I dropped the group
rather than keep a wrapper.

---
## 7. Stage 4b — product first, AI second (run on all 10 solutions)

Two solutions died here (S4-C, S14-A). One survives only with disclosure (S1-B, `thin`).

---
### S4-A · Swarm Ledger — **SURVIVES**
1. **What is the product** (no model named): a per-day ledger of the operators hitting
   your site. Each row is a cluster with a stable id, the raw requests that justify it,
   and the join keys that produced it. It keeps: cluster rows, join-key rows, evidence
   request rows, rule exports, run history. The workflow: ingest → partition →
   recompute-and-verify → persist → export config. It changes the decision *what do I
   block, at what granularity, and is this actor back?*
2. **Where AI creates leverage:** two narrow steps — **normalization** (inferring an
   unknown custom `log_format` so a stranger's log parses with no configuration) and
   **ranking** (ordering clusters by "worth a human look" across incommensurable
   features: sequence weirdness, ASN spread, timing lockstep). Plain code covers the
   common log formats and mis-sorts the long tail — and the long tail *is* the segment,
   because the operator not behind a CDN is the one with a hand-rolled log line. Honest
   statement: **the core of this product needs no model**, which the brief treats as a
   trivial pass, not a weakness.
3. **If the model disappeared:** parsers, join-key extractors, the clustering, the
   SQLite ledger with stable ids, the rule exporters, and the accumulated day-over-day
   swarm history. → **substantial**
- **Reduction sentence:** "the user gives their access log to a model and gets a list of
  suspicious clusters back." **FAIR? NO.** Cluster membership is produced and
  *re-verified* from deterministic keys; the ledger refuses to persist a cluster the
  deterministic recomputation does not reproduce. The sentence also misses the two parts
  that matter: the identity that persists across runs, and the config it writes.
- **Wrapper shape matched:** *an AI dashboard with no workflow of its own.* **Answered:**
  its output is a server ruleset you apply and an append-only evidence record, not a chart.
- **Authenticity signals (8):**
  | signal | group | basis | in this product's terms |
  |---|---|---|---|
  | narrow_persona | workflow | evidence (E14, E17) | an operator holding only a log file, not a CDN dashboard |
  | existing_workaround | workflow | evidence (E20–E22) | replaces a proof-of-work gate that taxes every human visitor, and a $25 robots.txt audit |
  | integration | workflow | commitment | emits nginx `map`, robots.txt stanza and a CDN expression; test: generated nginx config passes `nginx -t` |
  | automation_changes_workflow | workflow | commitment | a daily run replaces mid-incident log grepping |
  | accumulated_history | compounds | commitment | `swarm_id` persists, so "the same swarm is back on 40 new ASNs" is answerable; test: day-2 run reproduces day-1 ids for overlapping clusters |
  | usage_data | compounds | commitment | join-key frequency across runs tunes the ranking |
  | deterministic_core | substance | commitment | membership recomputed from stored keys; test: corrupt the model's ranking output and membership is unchanged |
  | hard_implementation | substance | commitment | extracting header-order and HTTP/2 SETTINGS order signals out of heterogeneous logs |

### S4-B · Canary Maze — **SURVIVES**
1. **The product:** a token mint and a sighting ledger. The operator gets middleware
   that serves per-visitor canaries, a mint table, a sighting table, a propagation graph,
   and an evidence bundle (raw request records, timestamps, hashes) a third party can
   check offline.
2. **AI leverage:** **matching** laundered tokens — when an agent paraphrases the planted
   fact instead of fetching the canary URL, exact matching fails and semantic matching is
   needed. Plain code cannot match a paraphrase. **The verbatim path needs no model**,
   and laundered sightings live in a separate lower-confidence table that never enters
   the proof graph.
3. **If the model disappeared:** the mint, the HMAC scheme, the middleware, the ledger,
   the graph, the evidence bundles — everything in the proof path. → **substantial**
- **Reduction sentence:** "the user gives candidate text to a model and gets 'this
  matches your token' back." **FAIR? NO** for the product — a verbatim sighting is an
  HMAC lookup. Fair only for the optional laundered-token extension, which is
  segregated and disclosed as optional.
- **Wrapper shape matched:** none. Closest is *only differentiation is a better prompt* —
  answered: no prompt is load-bearing anywhere in the proof path.
- **Authenticity signals (8):**
  | signal | group | basis | in this product's terms |
  |---|---|---|---|
  | narrow_persona | workflow | evidence (E14) | an operator who must show a third party what happened, not just block it |
  | real_workflow | workflow | evidence (E14) | they already rate-limit and are already ignored |
  | takes_responsibility_for_outcome | workflow | commitment | it asserts a factual claim — these two clients shared a secret — and stores the record that backs it; test: bundle verifies offline |
  | integration | workflow | commitment | drop-in middleware for nginx, Express and Flask |
  | accumulated_history | compounds | commitment | the mint ledger becomes the operator's own propagation history |
  | better_with_repeat_use | compounds | commitment | more canary surface → denser graph |
  | deterministic_core | substance | commitment | false positives bounded by HMAC collision; test: run the demo with the model disabled — the verbatim graph is byte-identical |
  | distribution_or_trust | substance | commitment | the evidence bundle is designed to be checked by someone who does not trust you |

### S4-C · "Ask the log" — **KILLED at Stage 4b**
1. **The product:** an upload box and a chat pane. Records kept: none.
2. **AI leverage:** only reasoning over messy inputs, emitted as prose. The model's
   output *is* the product.
3. **If the model disappeared:** **nothing.** → **KILL**
- **Reduction sentence:** "the user gives their access log to a model and gets an
  explanation back." **FAIR — DEAD.**
- **Wrapper shapes matched:** chat with your data; AI dashboard with no workflow of its
  own; wrapper around a model API.
- **What it never owns:** identity (no stable ids across runs), action (no rules
  produced), record (nothing persists), verification (no claim can be re-checked).
- **Regenerated as:** S4-A (stable ids + config export) and S4-B (planted evidence).

### S1-A · Batch card — **SURVIVES**
1. **The product:** a cross-install batch index that puts a label and one collapsed card
   on the triage queue. Records: normalized-body fingerprints, batch rows, author burst
   profiles, per-repo rules, and the outcome history of each batch.
2. **AI leverage:** **classification/matching** — mapping two differently-worded
   submissions to the same generated template. Minhash catches copy-paste, not
   paraphrase. **Deterministic gate:** a batch is asserted only when ≥N members share a
   deterministic key (byte-identical scaffold, the same non-resolving reference, or an
   author burst from the public events API); model-only matches render as "possible" and
   never count toward N.
3. **If the model disappeared:** webhooks, the fingerprint index, batch records, labels
   written to GitHub, outcome history, per-repo rules. → **substantial**
- **Reduction sentence:** "the user gives a pull request to a model and gets 'this is AI
  slop' back." **FAIR? NO** — and deliberately so: the product refuses to judge a single
  item's authorship, because that is the claim a maintainer cannot act on socially. Its
  claim is about the batch, computed from cross-repo events and a shared index.
- **Wrapper shape matched:** *AI dashboard.* **Answered:** writes_to_system_of_record —
  it applies labels and optionally closes with a template.
- **Authenticity signals (9):**
  | signal | group | basis | in this product's terms |
  |---|---|---|---|
  | narrow_persona | workflow | evidence (E1–E4) | a volunteer maintainer with one queue and no view of the other 40 repos |
  | existing_workaround | workflow | evidence (E1, E2) | replaces reading everything, closing the project to PRs, and dropping bounty money |
  | writes_to_system_of_record | workflow | commitment | applies a GitHub label and an optional templated close; test: label lands on a real PR in a demo org |
  | integration | workflow | commitment | a GitHub App, installed per-repo |
  | domain_logic | workflow | commitment | never accuses an author; describes only the batch — the social constraint is in the product |
  | network_effects | compounds | commitment | each install enlarges the index every other install queries |
  | accumulated_history | compounds | commitment | outcome history per batch ("9 of 112 already closed as not-planned") |
  | deterministic_core | substance | commitment | N-of-deterministic-keys gate; test: disable embeddings entirely and batches still assert |
  | hard_implementation | substance | commitment | reconstructing cross-repo bursts from the public events API inside rate limits |

### S1-B · Reciprocal evidence exchange — **SURVIVES, `thin`, disclosed**
1. **The product:** a signed append-only fingerprint feed plus a subscriber client.
   Records: published fingerprints, signatures, subscriptions, match logs.
2. **AI leverage:** none — fingerprints arrive from S1-A. Passes trivially.
3. **If the model disappeared:** the feed, the signing, the client — but with no S1-A
   there is nothing to publish. → **thin** (a dependent surface).
- **Reduction sentence:** not a model product; not fair by construction.
- **Wrapper shape matched:** *two-sided marketplace with no plan for its first supply.*
  **DECLARED and answered:** supply is seeded from the builder's own S1-A installs plus
  publicly archived closed-as-spam items; this is disclosed in the write-up rather than
  hidden behind a logo wall. **Hackathon-mode survival:** the genuinely hard part — a
  publication format that shares abuse signal while publishing hashes and never content
  or accusations — is visible to a judge in 60 seconds.
- **Authenticity signals (6):** existing_workaround (workflow, evidence E2/E3 — public
  complaining is the current channel) · integration (workflow, commitment — consumes
  S1-A) · network_effects (compounds, commitment — the entire point) ·
  accumulated_history (compounds, commitment) · deterministic_core (substance,
  commitment — hash-only publication, no content leaves a repo) ·
  distribution_or_trust (substance, commitment — a signed feed verifiable without
  trusting the publisher).

### S2-A · Non-existent source sweep — **SURVIVES**
1. **The product:** a queue of *account groups* joined by a shared non-existent source.
   Each entry carries the diffs, the resolution attempts with their HTTP status and
   timestamp, and a generated investigation page. Records: citation rows, resolution
   results, group rows, case pages, and a resolution cache.
2. **AI leverage:** **extraction** (citations out of messy wikitext and free-form prose
   where no template was used) and **matching** (near-identical fabricated references
   with different punctuation and field order). Rules handle the structured subset and
   miss the prose subset — which is precisely where careless generated text lives.
   **Deterministic core:** existence. A citation is "non-existent" only when a resolver
   returns a negative, never because a model thinks so.
3. **If the model disappeared:** resolvers, the resolution cache (independently
   valuable and accumulating), the citation index, the grouping, the generated case
   pages. → **substantial**
- **Reduction sentence:** "the user gives a diff to a model and gets 'this is AI-written'
  back." **FAIR? NO.** The product never judges authorship. It asks whether a cited
  source exists in the world and groups the accounts that cite the same non-existent
  one. That substitution — authorship detection → shared-fabrication join — is the wedge.
- **Wrapper shape matched:** none. Closest is the Stage-4 watch item *"check X against
  rules and flag it"* — **answered:** the check is an external-world lookup (does this
  DOI resolve?), not a rule, and the output is a grouped case page, not a flag.
- **Authenticity signals (9):**
  | signal | group | basis | in this product's terms |
  |---|---|---|---|
  | narrow_persona | workflow | evidence (E6) | a WikiProject AI Cleanup patroller opening a flagged diff |
  | existing_workaround | workflow | evidence (E6) | replaces source-authenticity checking done by hand by 300+ volunteers |
  | writes_to_system_of_record | workflow | commitment | generates a page in the community's own investigation workflow; test: it renders and validates against the template |
  | domain_logic | workflow | commitment | evidence-only, no automated enforcement — the community forbids it |
  | accumulated_history | compounds | commitment | the resolution cache never needs re-fetching and grows monotonically |
  | usage_data | compounds | commitment | which fabrications recur, and where |
  | deterministic_core | substance | commitment | resolver verdict is the sole basis for "non-existent"; test: stub the extraction model with regex and the verdicts are identical |
  | operational_complexity | substance | commitment | polite, rate-limited, cached resolution against doi.org / OpenLibrary with backoff |
  | proprietary_data | substance | commitment (probe E10, caveated) | an accumulated index of verified-non-existent sources; a repo search for comparable tooling returned 0 results, which is a weak absence signal, not proof |

### S2-B · Fabrication registry — **SURVIVES, `thin`, disclosed**
1. **The product:** a public registry of citations verified not to exist, with provenance
   per entry, plus a one-call lookup.
2. **AI leverage:** none required; the model is upstream in S2-A. Passes trivially.
3. **If the model disappeared:** the registry and the API survive, but without S2-A
   nothing fills them. → **thin** (a dependent surface).
- **Reduction sentence:** not applicable — no model in the loop.
- **Wrapper shape matched:** *two-sided with no first supply.* **DECLARED and answered:**
  S2-A produces supply on day one, so the registry launches non-empty.
- **Authenticity signals (6):** real_workflow (workflow, evidence E6 — reviewers already
  check citations) · integration (workflow, commitment — one lookup call) ·
  accumulated_history (compounds, commitment — the asset *is* the history) ·
  network_effects (compounds, commitment) · deterministic_core (substance, commitment) ·
  distribution_or_trust (substance, commitment — provenance per entry so a sceptic can
  re-verify the negative themselves).

### S3-A · Cohort console — **SURVIVES**
1. **The product:** a held queue of signup cohorts. Each cohort is one card with one
   reversible decision applied to every member, a saved signature that auto-holds future
   matches, and an action log recording which keys justified what.
2. **AI leverage:** **anomaly detection / matching** on generated-name and field-value
   families — recognising that forty dissimilar-looking usernames came from one
   generator. Entropy heuristics flag real people, and a false suspension is expensive
   for an unpaid admin. **Deterministic gate:** a cohort is actionable only when ≥K
   members share ≥2 deterministic keys (endpoint used, field pattern, email-domain
   family, arrival window); the model only proposes additions.
3. **If the model disappeared:** the ingest, the key-based clustering, the queue, the
   atomic set-action with undo, the action log, the saved signatures. → **substantial**
- **Reduction sentence:** "the user gives signup records to a model and gets 'these are
  bots' back." **FAIR? NO.** The product is the reversible set-action and its audit
  record; the grouping is key-based, and the thing the admin buys is being able to undo
  38 suspensions in one click.
- **Wrapper shape matched:** *an agentic version of existing SaaS.* **Answered:** it adds
  a unit of action the incumbent does not have (the cohort) rather than putting an agent
  on top of the incumbent — and the incumbent has had the request open since 2024-02-17.
- **Authenticity signals (9):**
  | signal | group | basis | in this product's terms |
  |---|---|---|---|
  | narrow_persona | workflow | evidence (E11, E16) | an unpaid admin of a ~2,000-user forum or a small instance, at 3am |
  | existing_workaround | workflow | evidence (E11, E36) | replaces defederating a whole server and hand-built honeypot fields |
  | automation_changes_workflow | workflow | commitment | one decision per wave instead of one per account |
  | takes_responsibility_for_outcome | workflow | commitment | every action reversible as a set with its justifying keys stored; test: undo restores all 38 accounts |
  | accumulated_history | compounds | commitment | saved cohort signatures auto-hold the next wave |
  | feedback_loop | compounds | commitment | admin overrides retune the proposal ranking |
  | deterministic_core | substance | commitment | K-of-2-keys gate; the model cannot cause an action on its own |
  | operational_complexity | substance | commitment | read-only ingest for two unrelated platforms without write access |
  | multi_provider | substance | commitment | works against ActivityPub and Discourse, proving the cohort primitive is platform-independent |

### S9-A · Participation receipts — **SURVIVES (market is a hypothesis)**
1. **The product:** an admission endpoint that mints per-window nonces and verifies
   signatures, a key registry, and a published coordination report. Records: nonces,
   receipts, keys, and the declared/undeclared ratio over time.
2. **AI leverage:** none. No model in the loop — trivial pass.
3. **If the model disappeared:** everything survives. → **substantial** (the weakness
   here is the *market*, not the AI question).
- **Reduction sentence:** not applicable.
- **Wrapper shape matched:** *NFT / token-gated.* **DECLARED and answered:** no token, no
  chain, no gating of value — plain HTTP message signatures, and unsigned submissions are
  **accepted and marked**, never blocked.
- **Authenticity signals (7):** narrow_persona (workflow, evidence E25 — a venue
  operator facing a bot-farm allegation) · real_workflow (workflow, evidence E25 — the
  allegation was actually filed) · writes_to_system_of_record (workflow, commitment —
  the published report) · domain_logic (workflow, commitment — accept-and-mark, to avoid
  killing participation) · accumulated_history (compounds, commitment — the
  declared/undeclared ratio over time is the venue's health metric) ·
  deterministic_core (substance, commitment — signature verification, zero inference) ·
  distribution_or_trust (substance, commitment — any third party can verify a receipt).
- **Disclosed weakness:** P9 rests on **one** opened evidence item. Treat the venue as a
  demo surface, not a market.

### S14-A · Swarm brief / question battery — **KILLED at Stage 4b**
1. **The product:** an upload box, twenty prompts and a document. Records kept: none.
2. **AI leverage:** reasoning over messy inputs, emitted as prose. The model's output
   *is* the product.
3. **If the model disappeared:** **nothing** — a prompt file and a PDF exporter. → **KILL**
- **Reduction sentence:** "the user gives 170k agent transcripts to a model and gets a
  brief back." **FAIR — DEAD.** This is verbatim the reduction sentence pre-registered in
  `defaults.md` §C before any research.
- **Wrapper shapes matched:** document/thread summarizer; generic research agent; chat
  with your data; generic RAG. It is also defaults D2 + D4 + D7 fused.
- **What it never owns:** provenance (no claim is bound to a re-fetchable artifact), the
  record (nothing persists for a second investigator), the action (no one's workflow
  changes), the check (no deterministic verification of anything it asserts).
- **Regeneration attempted:** a hash-chained, re-runnable **case file** in which every
  claim is bound to a fetched artifact's retrieval hash, so a second investigator can
  re-run it and see exactly what changed. That would be `substantial` — but I judged it
  out of reach for a ~20-hour solo build *alongside* a real evidence source, and chose to
  drop audience group G9 and report the gap rather than ship half a provenance format.

---

## 8. Leads — found but NOT opened (do not count as evidence)

- `draft-meunier-webbotauth-httpsig-protocol` — the live successor to the expired Web Bot
  Auth architecture draft (E35 names it). Not opened; would firm up S9-A's protocol
  why-now.
- `arxiv.org/abs/2604.05224` "Attribution Bias in Large Language Models" (AttriBench, 11
  LLMs) — search-result title only; relevant to any attribution claim.
- `aclanthology.org/2026.acl-long.282/` CiteGuard (retrieval-augmented citation
  validation, reported ~68.1% on CiteME vs ~69.2% human) — search-result snippet only,
  **not opened**; directly adjacent to S2-A and should be read before building it.
- Read the Docs' own blog post on AI crawler costs (E17 is the engineer's HN comment; the
  primary post with dollar figures was not opened).
- `incidentdatabase.ai` taxonomies and research pages — the incidents index I fetched is
  JavaScript-rendered and returned no counts, so default D8's "already exists" status is
  **unverified**, not confirmed.
- Anubis' documented deployment list — the known-instances page I fetched did not render a
  list; named-adopter claims therefore remain unverified.
- OpenTelemetry GenAI agent semantic conventions — the page I fetched says the spec moved
  to a separate repository; the actual attribute list was not opened.
- `boards.greenhouse.io` / Lever boards for a **second** platform employer — needed to
  turn E27 into a multi-employer STRONG spend signal for P5. Not attempted (budget).
- German/French-language wiki AI-cleanup projects — my one guessed URL 404'd and I did not
  find the correct page.
