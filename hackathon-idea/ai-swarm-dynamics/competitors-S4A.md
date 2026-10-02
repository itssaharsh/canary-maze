# Competitor & prior-art scan — "Swarm Ledger" (S4A)

Subagent C. Scan date 2026-10-02. ~17 lookups. Live pages marked "2026-10 (accessed)".
Verdict up front: **SURVIVING WEDGE, with a tarpit risk on one input (log fields), and a serious prior-art hit on the mechanism claim.**

---

## 0. HEADLINE: is there public, real log data with recent AI-agent traffic?

**Yes, one genuinely usable real dataset — but it is stripped of exactly the keys the pitch leans on.**

| Source | Real? | Recent? | Has AI-agent traffic? | Fields | Verdict |
|---|---|---|---|---|---|
| [Zenodo 18895701](https://zenodo.org/records/18895701) — "Online Shop Server Logs for Bot Traffic and Web Usage Analysis (Dec 2025) Anonymized" | real | yes, logs from **Dec 2025**, published **2026-03-06** | not labelled; UA pseudonymised so crawler names are unreadable | pseudonymised client IP, RFC1413, auth user, timestamp, method + sanitised URI, status, size, referer (query stripped), **pseudonymised User-Agent**. No TLS/JA4. | **BEST available.** CC BY 4.0, 178,939 requests, 28.6 MB plain text |
| [Kaggle web-server-access-logs](https://www.kaggle.com/datasets/eliasdabbas/web-server-access-logs) (nginx, 3.5 GB, online shop) | real, raw IPs + raw UAs | **no — predates 2025**, so no AI-crawler era traffic | no | full combined log | good for scale/plumbing, useless for the AI-agent story |
| [arXiv 2606.30119](https://arxiv.org/abs/2606.30119) honeypot — 1,383 visits, 2026-01-28→2026-02-24, nginx logs + browser fingerprints, 6 LLM web agents | real | yes | **yes, actual LLM web agents** | network + HTTP + browser fingerprints + nginx logs | the arXiv abs page **discloses no public dataset release**; volume tiny (1,383 visits) |
| [HF mindweave/web-server-logs](https://huggingface.co/datasets/mindweave/web-server-logs) | **synthetic** | n/a | simulated bot patterns | 50,000 requests, 3 servers, 12 months | fallback only |
| Zenodo [19731615](https://zenodo.org/records/19731615) / [19815504](https://zenodo.org/records/19815504) — SSH botnet honeypot, 145,425 events, 2025-05-11→2025-11-14, v2 Apr 2026 | real | yes | real botnets, **not HTTP** | SSH commands/payloads | wrong layer: no paths, no UAs, no TLS |

**The decisive quote**, from Zenodo 18895701 (2026-03-06): "IP addresses and User-Agent strings were replaced with stable pseudonyms to preserve session-level behavioural consistency while ensuring privacy protection."

What that means for the demo, precisely:
- **STILL WORKS on real data:** path-sequence shingles, inter-request timing lockstep across distinct (pseudonymous) clients, co-occurrence clustering, and `swarm_id` persistence across days — because the pseudonyms are *stable*.
- **DEAD on real data:** ASN + /24 join keys (no raw IPs → no ASN or /24 lookup), JA4/TLS, HTTP/2 SETTINGS, header order, Web Bot Auth `keyid` — none are present in any public HTTP log release I found. The money line "they spoofed their user-agent but the JA4 matched" **cannot be shown on public real data**, and the UA is pseudonymised so you cannot even print "GPTBot".
- No public release I found contains raw IPs + raw UAs + TLS fingerprints + recent AI-crawler hits together. None of the 5 datasets I opened or saw described provides that combination.

**Answer to give the judge:** yes, it runs on real traffic (CC BY 4.0, Dec 2025, 179k requests) for the behavioural + persistence half; the fingerprint half needs either the builder's own server (with `log_format` extended) or synthetic injection. Strongest demo = real Zenodo logs as the base + builder's own live log tail + a synthetic JA4-spoof scenario clearly labelled as such.

---

## 1. `startup` — commercial products

Cloudflare AI Crawl Control + signed agents: **not re-fetched, per instruction.**

### CLOSEST COMMERCIAL MATCH ON MECHANISM — WebDecoy
<https://webdecoy.com/ja4-fingerprint-format/> (article dated 2026-08-02; 2026-10 accessed)
Verbatim: "WebDecoy uses JA4 as a correlation key inside a persistent actor identity"; "Fingerprints are excellent as a correlation key (they persist while an actor rotates IPs)"; "only ever enforces on composite signatures that combine the fingerprint with network and path scope"; "fingerprints identify software. Actors identify attackers".
**Answer to the one question: YES — it claims a persistent actor identity built by correlating JA4 + network + path scope, not per-request classification.** This is the idea's framing already in a vendor's marketing.
**Differences / wedge:** inline AI bot-detection-and-mitigation platform (must sit in front of your traffic); page discloses **no pricing and no self-host/log-only path**; **does not specify that actor IDs persist across days** or for how long; no append-only ledger, no per-cluster evidence rows, no human-readable case card, no exported robots.txt/nginx `map`/CDN expression targeting the cluster, and no "the same swarm is back, now on 40 ASNs" diff across runs. It is a blocking service, not an operator-owned record.

### DataDome
<https://datadome.co/bot-management-protection/multi-layered-machine-learning-a-new-requirement-for-sophisticated-bot-protection/> and <https://datadome.co/threat-research/anatomy-of-a-distributed-scraping-attack/> (2026-10 accessed)
Aggregates signals "across various levels: request, session, IP, and fingerprint, over different time windows"; threat research describes the same URL requested "from bots with the exact same signature but 10+ distinct IP addresses, all in a one-minute time frame". Separate research names proxy providers behind Bots-as-a-Service (<https://datadome.co/threat-research/how-to-identify-proxy-providers-via-bots-as-a-service/>).
**Answer: PARTLY — it does cross-IP correlation inside a detection window, but I found no evidence of a durable, customer-queryable per-operator entity with a stable id across days.** Attribution happens inside DataDome's engine to decide block/allow; the output the customer gets is classification + analytics.
**Differences:** SaaS, inline, requires being a customer; window-scoped correlation (minutes) vs cross-run persistence (days/weeks); no operator-facing ledger or ruleset export targeting a cluster.

### Netacea
<https://netacea.com/intent-analytics/> (2026-10 accessed)
Verbatim-ish from the page/guide: a "proprietary User ID to assign an 'identity' to each visitor without ingesting PII"; "attack signals analyzed in real time are combined with verified signals already detected from across the Netacea customer network to create attacker fingerprints"; "the same adversaries and botnets appear repeatedly" across the protected customer base.
**Answer: PARTLY — closest commercial claim to "the same actor is back", but the identity is per-visitor + vendor-side cross-customer threat intel, not a per-operator cluster record the operator owns.** Server-side log ingestion exists, but as a Netacea customer.
**Differences:** vendor-held identity, no self-host, cross-customer intel is their moat not your ledger, no cluster-targeting ruleset export.

### Kasada
<https://www.helpnetsecurity.com/2023/12/20/kasada-bot-defense-platform/> (2023-12-20) — "analytics for vital attack insights, including detailed classification, drilldown, filtering". Classification-led; no evidence of a persistent operator entity. **This is a LEAD, not evidence — I did not open Kasada's own site.**

### Not checked (budget)
HUMAN Security, Imperva/Thales, Fastly, Akamai, Castle, Arkose, Fingerprint.com — **not checked: lookup budget went to depth on WebDecoy/DataDome/Netacea, the PayPal patent, and the dataset question, as instructed.** Note for the caller: Fingerprint.com's `visitorId` is a per-browser/device identity requiring a client-side agent, so it is structurally not operator-level-from-logs — but that is my reasoning, **not verified this run**.

### PRIOR ART — the most serious hit of the whole scan
**PayPal, US12034731B2, "Evaluating access requests using assigned common actor identifiers"** — <https://patents.google.com/patent/US12034731> — filed **2021-01-29**, granted **2024-07-09**.
Abstract, verbatim: "Techniques are discussed for grouping access requests made to a computer system using a log of access requests that includes a plurality of log entries of that include (a) a plurality of traffic indicators of the corresponding access request and/or (b) a plurality of identity indicators of a respective remote computer system that made the corresponding access request. The plurality of log entries is analyzed using a plurality of network analysis rules that are useable to group log entries according to traffic and/or identity indicators. Based on the analyzing, a plurality of groups of log entries are identified, and each group of log entries is assigned a corresponding common actor identifier (common actor ID). The determination of whether to grant a particular access request uses one or more assigned common actor IDs."
Claim 1, verbatim: "based on the analyzing, identifying, with the computer system, a plurality of groups of log entries, wherein each group of log entries is assigned a corresponding common actor identifier (common actor ID)". The actor-ID table stores information "over a period of time (e.g., over the last 12 months)".
**This is the idea's mechanism, as a granted patent: logs → groups → stable per-actor id → persisted for months.**
**Differences:** purpose is access-grant / fraud decisioning at login, not AI-crawler or web-abuse attribution; no operator-facing artifacts (no ledger rows + evidence, no case card, no robots.txt/nginx/CDN export); nothing about JA4, HTTP/2 SETTINGS, header order or Web Bot Auth; and it is a patent, not something an operator can run.
**Consequence for the pitch: drop any claim that "nobody answers are these 9,000 requests one actor". Someone patented answering it in 2021.** The defensible claim is the *operator-facing product* (own your ledger, log-only, no CDN) and the *spoof-resistant key set*, not the concept.
Also surfaced, **LEAD not opened:** US11652844B2 "Utilizing clustering to identify IP addresses used by a botnet" <https://patents.google.com/patent/US11652844>.

---

## 2. `oss` — open source, split into fork buckets

GitHub API note: `q=bot+detection+access+log+clustering&sort=stars` returned **`"total_count": 0`** (2026-10 accessed). That is itself a datapoint: no repository describes itself with those words together.

### MECHANISM — do NOT fork as the core (forking = reskin, nothing left to credit)
| Repo | Stars/Forks | Lang / Licence | Created / Pushed | What it is |
|---|---|---|---|---|
| [mshaheerjunaid/Panopticon](https://github.com/mshaheerjunaid/Panopticon) | 1 / — | Python / **MIT** | 2026-08-11 / 2026-08-11 | "Behavioural abuse detection that finds coordinated attacks by clustering on behaviour and JA4 TLS fingerprint instead of IP" |

Panopticon is the only OSS project I found whose self-description *is* this idea. But: 1 star, created and last pushed the same day, no community. Treat it as a **reference implementation to read, and a naming collision to be aware of**, not a competitor. **Fork base: weak** — unknown completeness, single-day history, and forking it is exactly the reskin trap.

### PLUMBING — fork with pure upside
| Repo | Stars/Forks | Lang / Licence | Created / Pushed | Why it's plumbing | What a solo builder must ADD |
|---|---|---|---|---|---|
| [Query-farm/vgi-tlsfp](https://github.com/Query-farm/vgi-tlsfp) | 0 / — | Rust / **MIT** | 2026-06-30 / 2026-09-22 | "Compute TLS fingerprints in DuckDB with SQL — JA3, JA3S and JA4 (TLS-client) for clustering C2 and bot infrastructure" | log parser, the non-TLS join keys (ASN//24, path shingles, timing lockstep, Web Bot Auth keyid), `swarm_id` minting + cross-run persistence, append-only ledger, case card, ruleset emitters. **Best technical fit** — gives you JA4 inside DuckDB, i.e. the log-only single-binary SQL shape the product wants |
| CrowdSec (`crowdsecurity/crowdsec`) | large (not re-fetched per instruction) | Go / MIT — **from prior knowledge, NOT verified this run** | — | nginx/Apache/Caddy parsers, acquisition + file tailer, GeoIP/AS enrichment, bouncers for enforcement | the entire clustering + identity layer (see below) |
| Anubis (`TecharoHQ/anubis`) | 22,995 / 743 (given) | Go | created 2025-03-17 | proof-of-work gate — a **workaround**, not attribution | everything; only useful as the "what people do instead" baseline |

**CrowdSec — the flagged question, answered.** Sources: <https://docs.crowdsec.net/docs/cscli/cscli_decisions_add/>, <https://docs.crowdsec.net/u/user_guides/decisions_mgmt/> (2026-10 accessed). `cscli decisions add` takes `--ip`, `--range`, or a custom `--scope username --value foobar`, with **default scope "Ip"**; decision listings carry COUNTRY and AS fields "provided by GeoIP enrichment if present". Alerts are "records created when a scenario/AppSec rule triggers" and decisions are "remediation instructions (for example `ban`…)" (<https://docs.crowdsec.net/docs/concepts/>).
**Verdict: CrowdSec scores IPs (or a range/username *you* name), and shares IP reputation across its community. I found no documented construct that mints a persistent identifier for a GROUP of distinct IPs recurring across days.** So: **not a clone — it is the single best plumbing fork base.** Caveat on confidence: `docs/concepts/` did not enumerate scopes and `docs/scenarios/format/` **fetched empty**, so I could not read the leaky-bucket `groupby`/`distinct` reference directly; this conclusion rests on the decisions docs plus search snippets. Someone should confirm `groupby` semantics before the pitch says "CrowdSec can't do this".

**Not checked (budget):** GoAccess, Matomo, Fail2ban, nepenthes, iocaine, go-away, Nginx Bad Bot Blocker — **not checked: lookup budget; also the zero-result GitHub query suggests none self-describes as clustering into actors.** All are presumed PLUMBING (ingest, lists, gates), none presumed MECHANISM.

---

## 3. `research`

### Closest research match AND closest on segment — Logrip
**arXiv 2508.03130**, "Protecting Small Organizations from AI Bots with Logrip: Hierarchical IP Hashing", Rama Carl Hoetzlein, **2025-08-05**. <https://arxiv.org/abs/2508.03130>
Verbatim from the abstract: "Small organizations, start ups, and self-hosted servers face increasing strain from automated web crawlers and AI bots"; "leverages data visualization and hierarchical IP hashing to analyze server event logs, distinguishing human users from automated entities based on access patterns"; "By aggregating IP activity across subnet classes and applying statistical measures, our method detects coordinated bot activity and distributed crawling attacks that conventional tools fail to identify"; "Using a real world example we estimate that 80 to 95 percent of traffic originates from AI crawlers, underscoring the need for improved filtering mechanisms."
**Produces: one-shot analysis + visualisation. No persistent actor identity disclosed in the abstract; no dataset release and no code release mentioned.**
**Differences:** aggregates by **IP subnet hierarchy**, which is precisely where the pitch claims to win (an actor spread over 40 ASNs defeats subnet aggregation); no stable id across runs; no TLS/HTTP-2/Web Bot Auth keys; no ledger, case card or ruleset export.
**Use it as a citation:** it independently validates the segment ("small organizations… self-hosted servers"), the gap ("conventional tools fail to identify") and the pain ("80 to 95 percent").

### arXiv 2606.30119 — "On the Internet, Nobody Knows You're an LLM Bot: Unmasking Web Agents with Multi-Layer Fingerprinting"
Fayolle, Bouhenniche, Pélissier, Laperdrix, Maurice, Rudametkin; submitted **2026-06-29**. <https://arxiv.org/abs/2606.30119>
Integrates "network-, HTTP-, and browser-level fingerprinting techniques" into honeysites; compares six LLM-based web agents against humans. **Produces: one-shot per-visit discrimination. The abs page shows no clustering of multiple IPs into one actor and no longitudinal/cross-day identity.** Honeypot data (1,383 visits, 2026-01-28→02-24) — no public release disclosed.

### Measurement / policy — all one-shot, none produces actor identities
- robots.txt gatekeeping of misinformation vs reputable sites (2025-10-11) — measures "active blocking behavior… when HTTP requests include AI crawler user agents"
- Web crawler restrictions, AI training datasets & political biases (2025-10-10) — top-1M robots.txt census
- Generative AI and the Future of the Digital Commons (2025-08-08) — position paper
- "Somesite I Used To Crawl" (2024-11-22) — 203-artist user study on efficacy of blocking tools
- terms.txt consent/compensation protocol (2026-09-10); Pay-Per-Crawl Pricing / LM-Tree Agent (2026-04-01) — protocol + economics
**None of these clusters requests into operators.** The literature is about *policy declarations and census*, not *actor attribution*.

---

## 4. `platform` — the non-CDN segment (the claimed wedge)

**Of the four commercial products I opened (WebDecoy, DataDome, Netacea, Kasada), every one requires being their customer with traffic flowing through or into their platform; none advertises a self-hostable or log-only operator-attribution path.** Cloudflare's path (given) is CDN-gated by construction.
The only self-hostable / log-only options I found anywhere: Logrip (academic, subnet-based, no code release mentioned), CrowdSec (IP-scoped), Panopticon (1-star stub), vgi-tlsfp (a fingerprint function, not a product).
**So the segment is real and thin. That is the wedge.** Caveat: HUMAN, Imperva/Thales, Fastly, Akamai, Castle and Arkose were not opened, so write this as "none of the four products I opened offers a log-only path", not as a fact about the field.

**Structural obstacle to flag honestly (this is the tarpit risk):** JA4, HTTP/2 SETTINGS and header order are **not in a default nginx/Apache access log**. They need `log_format` changes, a TLS-fingerprint module, Caddy, or a CDN export — and no public archived log set has them. An operator can get them going forward on their own server; they cannot get them retroactively, which blunts "the keys are already in the log". The keys that *are* already in every log are ASN//24 (needs raw IP), path-sequence shingles and timing lockstep.

---

## 5. `hackathon` — prior projects

No prior edition of this event and no prior hackathon by the hosts (given). Apart Research sprint search (2026-10 accessed):
- [Defensive Acceleration Hackathon, 2025-11-21→23](https://apartresearch.com/sprints/def-acc-hackathon-2025-11-21-to-2025-11-23) — **2nd place: "Comparative LLM methods for Social Media Bot Detection"**
- An Apart honeypot project identified LLM agents via prompt-injection traps and timing analysis, "out of over 7.5 million attack attempts", classifying agents "in under 1.5 seconds"
- Other sprints surfaced (AI Manipulation 2026-01-09→11, Secret Loyalties 2026-07-24→26, Secure Program Synthesis 2026-05-22→24) — none on web-traffic attribution
**Nothing found on operator attribution from access logs.**

### `closest_past_winner`
```json
{
  "name": "Comparative LLM methods for Social Media Bot Detection",
  "event": "Apart Research — Defensive Acceleration Hackathon, 2025-11-21 to 2025-11-23",
  "place": "2nd",
  "url": "https://apartresearch.com/sprints/def-acc-hackathon-2025-11-21-to-2025-11-23",
  "how_it_differs": "social-media account classification with LLMs; no HTTP logs, no join keys, no cross-run operator identity, no operator artifacts. Shares only the words 'bot detection'.",
  "searches": [
    "apartresearch.com hackathon winners bot detection web scraping agent traffic forensics attribution project",
    "cluster requests into one operator persistent bot actor identity across days access log attribution JA4"
  ]
}
```

---

## 6. `workaround` — how it's done today, with evidence

The given evidence (mid-incident log grepping; Anubis proof-of-work 22,995 stars / 743 forks, created 2025-03-17; hand-maintained robots.txt and firewall rules; ignored rate limits; a $25 freelance "AI crawler access audit") holds, and the scan adds two things:
1. **Academic confirmation that the tools fail:** Logrip, 2025-08-05, verbatim — "distributed crawling attacks that conventional tools fail to identify".
2. **A visible cottage industry teaching exactly the wrong method** — grep your logs for known AI user-agent strings. Live pages, 2026-10 accessed: <https://www.digitalapplied.com/blog/server-log-ai-agent-detection-beyond-ga4-2026> ("Server Logs: Finding the AI Agents That GA4 Can't See"), <https://www.openshadow.io/guides/monitor-ai-bot-traffic>, <https://thegeolab.net/10-ai-crawlers-log-identification/> ("10 AI Crawlers… How to Identify Them in Your Logs"), <https://webizm.com/en/resources/how-to-analyze-ai-bot-traffic-in-server-logs/>, <https://aicrawlercheck.com/blog/monitor-ai-bot-traffic-analytics>, <https://aisearch.similarweb.com/blog/log-file-analysis/>, <https://presenc.ai/research/ai-crawler-user-agents-complete-list> (a maintained UA list).
**This is the strongest demo contrast available:** the whole published state of the art for a non-CDN operator is "grep for GPTBot|ClaudeBot|PerplexityBot", which is defeated by one spoofed header.

---

## 7. Clone / tarpit / wedge

**Not a clone. Not a tarpit on demand. A surviving wedge with a tarpit risk on one input.**

- **Not a CLONE:** no product I opened gives a non-CDN operator a **log-only, self-hostable, append-only per-operator record with a stable id across runs, plus an exported ruleset that targets the cluster rather than the user-agent**. WebDecoy comes closest on mechanism but is an inline mitigation service with no disclosed self-host, pricing or cross-day persistence.
- **Mechanism novelty is GONE, though.** "Cluster log lines into a common actor and give it a persistent id" is a granted PayPal patent (US12034731B2, 2024-07-09, persisted ~12 months), is WebDecoy's marketing language (2026-08), is DataDome's windowed cross-IP correlation, and is a 1-star GitHub repo's one-line description. **The insight line "nobody answers whether these 9,000 requests are one actor" is falsifiable in one search and must be rewritten.**
- **TARPIT RISK, and it is about data, not rivals:** the spoof-resistant join keys (JA4, HTTP/2 SETTINGS, header order, Web Bot Auth `keyid`) are absent from default access logs and from every public log release found; the one good real dataset pseudonymises both IPs and user-agents, killing ASN//24 as well. The structural obstacle is log fields. Nobody has solved it because it mostly cannot be solved retroactively.
- **Where the wedge actually lives:** (a) the segment — self-hosted/small operators, validated independently by Logrip's 80-95% figure and "conventional tools fail"; (b) the artifacts — ledger + evidence rows + case card + cluster-targeting ruleset export, which **none** of the four products I opened produces for the operator; (c) persistence-as-a-feature — "the same swarm is back and it is now using 40 ASNs" is a diff across runs, and no opened competitor shows that diff to the customer; (d) ownership — your ledger, your logs, no vendor in the path.

**The single strongest existing alternative a judge would name:** Cloudflare AI Crawl Control, if the judge is a Cloudflare user. **A technically sharp judge will instead name CrowdSec** — free, self-hosted, already parsing the same nginx logs, crowd-sourced reputation — and ask why a `swarm_id` beats a CrowdSec decision. Have that answer ready: CrowdSec's unit is an IP (default scope "Ip"); Swarm Ledger's unit is a cluster that outlives every IP in it. The other name to be ready for is **WebDecoy**, because it already says "fingerprints identify software. Actors identify attackers."
