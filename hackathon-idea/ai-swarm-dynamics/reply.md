Mode hackathon · context GENERAL · depth full · AI Swarm Dynamics Hackathon (Oct 3–4, you supplied the link) · 12 problems across 9 user groups · **2 of 3 shortlisted ideas survived**, because the independent critic downloaded the organizers' own dump and falsified the third on their data. Most of the evidence is moderate-to-strong and opened; every criterion below is `assumed`, because the organizers publish no rubric.

## 1. Judging intelligence in brief

- **No criteria exist.** Home page: "~3-5 judges (members of the AI Village staff and experts in the field)". Logistics: "A panel of Grove Research and AI Village staff will review submissions", decisions roughly a week later. *(High — organizer-stated.)*
- **The deadline precedes the demos, and you're online.** Your write-up and repo are the whole entry. Stop building around 15:00 Sunday and spend two hours writing. *(High.)*
- **Treat the "optional" results write-up as mandatory.** The panel is research staff at two research orgs, and AI Village's own Shoshannah Tekofsky has said "We have more data than we can possibly process ourselves though." *(Medium — inference from a sourced quote.)*
- **Two of their seven suggestions are already shipped products:** agenthotline.ai is live with an MCP `report_safety_incident` function; trajectory analysis is Transluce's Docent. The emptiest slot is web forensics beyond transcripts. *(Medium.)*
- **Ship a committed data sample:** no gallery, no voting, no rating UI, and a judge may never get dataset approval. *(Medium.)*

## 2. Canary Maze

**Concept:** a site that issues every automated visitor its own secret, then records who else comes asking for it — turning "these clients look similar" into "this client fetched a URL only that context was ever shown, four minutes earlier."
Problem: validated (strong) · Wedge: untested

**Problem:** an operator cannot establish that two automated clients coordinated. Passive detection compares traffic characteristics, and those are controlled by the client — Cloudflare documented an undeclared crawler reaching robots.txt-blocked, newly purchased, unindexed domains at "3-6m daily requests" behind a desktop Chrome user-agent, rotating "different ASNs in attempts to further evade website blocks."

**User:** the operator of a site or public API, at the moment they're asked to prove what happened rather than just block it.

**Why it matters:** every available answer blocks, counts, guesses or wastes; none records. The two published routes are Cloudflare's (buy domains, ask a chatbot) and Duke's (wait two months). Neither leaves a reader records to check.

**Core workflow:** middleware classifies each request human/automated → for automated ones, mint a canary URL and fact-token as HMAC(path, context, salt) and write a mint row → check every later request against the mint table → a request for a secret by a *different* context becomes a sighting edge with both raw request rows → render a propagation graph and export a bundle that verifies with the server switched off.

**AI role:** matching, on an optional side path only — when a client restates a planted fact in its own words, exact and fuzzy matching both miss it. Those laundered sightings go in a separate lower-confidence table that never enters the proof graph. The verbatim path uses no model.

**Non-AI product:** the HMAC mint, the middleware, both ledgers, the graph, the bundle and its offline verifier — the entire proof path.

**Data loop:** a propagation history that cannot be backfilled, because a sighting only exists if the secret was already being served.

**Hard part:** the serving layer, not the ledger. A secret issued to context A must still return 200 for B, which means a stable unbounded per-context URL space plus domain, DNS, TLS and sitemap. The glamour is the graph; the weekend goes to DNS.

**Technical implementation:** fork Pyison (MIT, 125 stars) for the maze and serving layer; write the mint, salt rotation, both SQLite ledgers, the context deriver, the sighting detector, a static SVG graph and a Merkle-rooted bundle writer.

**Sponsor fit:** none. This event offers no sponsor API, the $200 compute reimbursement is in-person only, and this idea touches none of the four offered datasets — which is a real weakness against the "real results" criterion and is stated as such.

**Judging criteria alignment** (all `assumed`): execution — disable the model, re-run, show a byte-identical proof graph. Impact — it closes the gap the investigators name first, that activity "can itself modify or delete relevant data". Real results — the seeded replay is built, not waited for. Originality — **cite the Duke paper in the first minute**; it already mints per visitor and keeps the ledger, so your contribution is the sighting channel, not the minting. Presentation — one sentence, one graph, one bundle. Theme — answers their suggestions 5 and 6.

**Demo flow:** mint table (secret X → context A, 11:04) → sighting table (X requested by context B, 11:08) → the graph → the live organic log beside it with its real count, labelled, not blurred.

**Wow moment:** stop the server, run the verifier on the bundle file alone, and the claim still stands.

**MVP scope:** IN — per-context minting, both ledgers, sighting detection, graph, bundle + verifier, human-exclusion gate, and the seeded two-client replay as the *primary* deliverable. OUT — semantic matching (ships disabled), any claim that two contexts are two actors, any dependence on an organic sighting arriving.

**Differentiation:** Duke verifies through 22 model products after two months and proves scraper→model ingestion; this reads the request log in minutes and proves a secret moved between contexts. Canarytokens is one token per asset, planted by hand.

**Risks:** a sighting does **not** establish two actors — one actor label in the organizers' dump spans 741 IPs, so intra-actor rotation presents as a sighting, and the earlier claim that false positives were bounded by HMAC collision was wrong. Also: the prior art is closer than it looked; an organic sighting may never fire in 31 hours; tokens can be stripped; minting for humans would be tracking.

**What can be built during the event:** Sat 10:00–13:00 domain/DNS/TLS/sitemap and a stable per-context URL space. 13:00–16:00 mint, ledgers, human gate. 16:00–19:00 sighting detector, seeded replay, graph. Sun 10:00–12:00 bundle + verifier. 12:00–14:00 paste minted URLs into public model products, record which fetchers return. 15:00–17:00 write-up.

## 3. Batch Card

**Concept:** a tool that answers what a maintainer cannot answer alone, and what GitHub says its own cap does not answer: did this submission arrive on its own? One collapsed card — "submission 14 of 112 opened by 9 accounts in 6h across 40 repos" — and never a word about who wrote it.
Problem: validated (strong) · Wedge: untested

**Problem:** a maintainer decides one submission at a time with no view of the batch. curl measured it: "20% of all submissions" machine-generated slop, valid findings down to "about 5% of the submissions in 2025", each report engaging "3-4 persons" for "30 minutes, sometimes up to an hour or three. Each."

**User:** a volunteer maintainer, at the moment a submission lands in the queue they work through in their own time.

**Why it matters:** the platform owner wrote the gap down. GitHub's own post says its cap "does nothing when someone opens pull requests across hundreds of repositories at once", with cross-repository controls still only being explored.

**Core workflow:** read public events for the window → compute a normalised minhash against a cross-repository index, the author's burst profile, and structural tells (branch pattern, section headers) → assert a batch only when ≥N members share a *deterministic* key → render one collapsed card and persist a batch record.

**AI role:** classification and matching — two submissions from one template arrive differently worded every time, which minhash misses. A batch is never asserted on a model match alone.

**Non-AI product:** the index, the key extractors, the burst profiler, the batch records, the card, the rules and every batch's outcome history.

**Data loop:** recurring campaign shapes accumulate into the key list the deterministic gate fires on.

**Hard part:** reconstructing cross-repository bursts from the public events API inside its rate limits, and the restraint — the gate must be tight enough that the card is never wrong about the shape even when the model is wrong about the text.

**Technical implementation:** **cut the GitHub App.** A third-party App sees only installed repos, so on a solo weekend there is no "cross"; the public events API and event archive give the same profile with no install and no cold start.

**Sponsor fit:** none, for the same reasons as above; it uses none of the four offered datasets.

**Judging criteria alignment** (all `assumed`): execution — disable embeddings, batches still assert. Impact — rests on GitHub's stated gap, **not** on expressed demand. Real results — replay the documented campaign window and check against an independent published account. Originality — 14 open-source projects and 4 commercial products all score an item or an author; none indexes across repos. Presentation — one card, one number, naming nobody. Theme — see the risk below.

**Demo flow:** replay the real window → the card appears → the vendor write-up of the same campaign beside it, which took three weeks → state the honest split.

**Wow moment:** the card never says "AI" or "slop" and never names an author. It states a shape — and one in five written policies currently tells a volunteer to ban the user instead.

**MVP scope:** IN — three signals from public event data, the gate, the batch record, the card rendered on a real PR in a demo org, the replay. OUT — the App and its install flow, any authorship judgement, any automated closing.

**Differentiation:** against GitHub's cap, 9 accounts × 40 repos × a cap of 3 is up to 1,080 compliant submissions. Against open-slop, it holds one account at a time so it can never say "nine accounts".

**Risks:** **maintainers did not ask for this** — in GitHub's own discussion, cross-repository detection "wasn't a common theme" and "No maintainers explicitly asked for batch-identifying labels"; the ground truth barely exercises the mechanism, since ~95% of the documented campaign came from one account, leaving a ~25-submission multi-account tail; and **theme fit is the weakest in the set** — that campaign is one human running six accounts with machine-generated payloads, not agents coordinating, so the write-up must say "one operator, many accounts" and never "swarm".

**What can be built during the event:** Sat 10:00–14:00 index the public event archive for the window (the long pole). 14:00–17:00 key extractors and burst profiler. 17:00–20:00 batch rule and gate; get one real batch to render. Sun 10:00–13:00 check against the published account. 13:00–15:00 card on a real PR. 15:00–17:00 write-up.

## 4. Sponsor verdicts

| Sponsor | Verdict |
|---|---|
| AI Village (The AI Digest) | Does not fit as a technology. It supplies the framing and a 177 GB gated corpus, not an API. Neither survivor analyses agent transcripts — a direct consequence of you being online with no compute reimbursement, since an inference pass over 1.14M computer-use turns is financially out of reach. |
| Grove Research | Does not fit as a technology; supplies no API or dataset. Its published interest in agent identity and authorship overlaps the provenance concern, but that is context for the write-up, not an integration. |
| Anthropic | Does not fit: the $200 reimbursement is in-person only. Both survivors are deliberately built so a deterministic core carries the result. |

## 5. Tradeoffs

| | Canary Maze | Batch Card |
|---|---|---|
| Evidence for the problem | Strong — 5 independent orgs incl. Wikimedia, a UN API, Read the Docs | Strong — curl's primary numbers, a vendor's named-account campaign, 2 more maintainers, a 281-policy survey |
| Theme fit | Answers their suggestions 5 and 6; suggestion 6 was independently the emptiest slot | Weakest in the set — one human with six accounts is not agents coordinating |
| Real results this weekend | Seeded replay is certain; organic sighting is not | Most certain of the two — a documented window in public data |
| Mechanism novelty after scanning | Narrowed to the sighting channel; Duke owns the minting | Intact at the mechanism, fashionable at the topic |
| Expressed demand | Operators say it plainly in their own words | Maintainers asked for friction, not attribution |
| What eats the weekend | DNS and a stable URL space | 24 days of event archive |
| Forkable | Pyison (MIT) for serving; mechanism is yours | Octokit pager only; index is yours |

What would change the picture: for Canary Maze, whether any organic cross-context sighting fires by Saturday evening. For Batch Card, whether the ~25-submission multi-account tail is enough to render a card a judge finds convincing.

## 6. Killed

15 logged. **Wrapper filter (2)** — "Ask the log" and the question battery, whose reduction sentence was verbatim the one pre-registered before research. **Critic, on measurement (1)** — the fabricated-citation join: 0 DOIs, 0 ISBNs, 0 cite templates across all 14,591 revisions of the organizers' dump. **Competition (1)** — log attribution, mechanism claimed by a PayPal patent. **Shortlist (4)**, **validation (6)**, **prior art (1)**.

## 7. Notes for you

Not personalised: there is no background about you in this session — empty memory directory, no project CLAUDE.md, no repo history — so I can't tell you which of these is nearer your existing stack, and I won't guess. Tell me your languages and whether you've shipped a GitHub App or run your own web server, and I'll redo this section properly. The past-project check therefore couldn't be run against real history either.

Objective pre-flight, independent of background: **request AI Village dataset access tonight** (gated, manually reviewed) even though neither survivor needs it — it's free optionality. For Canary Maze, buy the domain and get DNS and TLS live tonight if you possibly can; it's the long pole and it's the one task that is pure waiting. For Batch Card, confirm tonight that you can pull the public event archive at the rate you need.

## 8. Next steps

Run the 30-second outsider script on one person before you start building — it's in the package for each idea, and for Batch Card it settles the open `wrong_brief` question. Then I can plan the build with `prod-build`, or run another discovery round. One live thread: the critic's measurement surfaced a different join key in the organizers' own data — 8,473 URLs shared by 2+ accounts, dominated by markdown-scraping proxies (`r.jina.ai`, `pure.md`, `md.succ.ai`) — i.e. those agents shared *tooling*. That's on-theme, on a real agent wiki, on an ungated 4.2 MB download. I have it under validation and will report; it is **not** a candidate until it passes.

## 9. Gate

0 FAIL, 8 WARN. Disclosed: all six criteria are `assumed` because no rubric is published; Batch Card's `wrong_brief` is **unknown** pending the outsider test; 11 research gaps. Isolation was structural — discovery ran in a subagent that never saw the event, its hosts, its sponsors or anything about you, and your background was read only at Stage 10, after the ideas were final. Not accessible or not checked: Socket's product pages (the biggest unchecked competitive risk for Batch Card), GitLab and Codeberg, Transluce's log distribution route, non-English wiki projects (one 404), Indeed and Upwork (both 403), and the collusion.wiki dump states no licence. Package: `hackathon-idea/ai-swarm-dynamics/idea-package.md`.

## 10. Sources

Event: [swarmchasing.com](https://swarmchasing.com/) · [logistics](https://swarmchasing.com/logistics/) · [AI Village dataset](https://huggingface.co/datasets/aidigestorg/ai-village) · [collusion.wiki dump](https://collusion.wiki/explorer/download) · [SwarmTraces](https://swarmtraces.org/) · [kickoff paper](https://arxiv.org/html/2609.04170v1) · [METR incident report](https://metr.org/hugging-face-incident-report-aug-2026.pdf) · [AI Village on the incident](https://www.lesswrong.com/posts/cR3P3hvtZtpo7GdS8/ai-village-reacts-to-huggingface-incident-comparing-the) · [Grove Research](https://groveresearch.com/blog/welcome-to-delvetown/)
Canary Maze: [Cloudflare on stealth crawling](https://blog.cloudflare.com/perplexity-is-using-stealth-undeclared-crawlers-to-evade-website-no-crawl-directives/) · [Duke canary-token paper](https://arxiv.org/html/2605.13706v1) · [Canarytokens](https://docs.canarytokens.org/guide/) · [AI Labyrinth](https://blog.cloudflare.com/ai-labyrinth/) · [Web Bot Auth](https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth) · [Wikimedia on crawlers](https://diff.wikimedia.org/2025/04/01/how-crawlers-impact-the-operations-of-the-wikimedia-projects/) · [UNCTAD API operator](https://news.ycombinator.com/item?id=49868377) · [Read the Docs](https://news.ycombinator.com/item?id=49630503) · [Anubis](https://api.github.com/repos/TecharoHQ/anubis) · [Pyison](https://github.com/JonasLong/Pyison) · [Two Witnesses](https://github.com/MichelleThuo/two-witnesses)
Batch Card: [curl on slop](https://daniel.haxx.se/blog/2025/07/14/death-by-a-thousand-slops/) · [Wiz on prt-scan](https://www.wiz.io/blog/six-accounts-one-actor-inside-the-prt-scan-supply-chain-campaign) · [GitHub on its PR cap](https://github.blog/open-source/maintainers/how-pull-request-limits-are-cutting-down-the-noise/) · [GitHub maintainer discussion](https://github.com/orgs/community/discussions/185387) · [281 AI policies](https://arxiv.org/html/2609.07542) · [Socket via InfoWorld](https://www.infoworld.com/article/4132851/open-source-maintainers-are-being-targeted-by-ai-agent-as-part-of-reputation-farming.html) · [open-slop](https://github.com/marketplace/actions/open-slop) · [Greptile](https://www.greptile.com/docs/introduction) · [a maintainer quitting PRs](https://news.ycombinator.com/item?id=47414995)
Saturation: [Docent](https://docs.transluce.org/) · [agenthotline.ai](https://agenthotline.ai/) · [OECD incident on Moltbook](https://oecd.ai/en/incidents/2026-01-31-f6b5) · [Apart Research](https://apartresearch.com/)
