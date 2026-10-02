# Competitor / prior-art scan — S1A "Batch card"

Subagent C. Scan date 2026-10-02. All live pages marked "2026-10 (accessed)".
Lookups spent: 22 (10 searches, 12 fetches).

**Fingerprint under test:** domain = open-source operations; user = volunteer maintainer at the
moment a submission lands; job = decide in under a minute whether it deserves human review;
mechanism = the triage unit changes from one submission to the **batch** it belongs to, with the
batch persisted as a record; family = inform+prevent. It deliberately refuses to judge one item's
authorship.

**Headline verdict: NOT A CLONE. Surviving wedge, but a crowded and fashionable category.**
Every tool I opened scores either (a) the single submission, or (b) the single *author's* history.
None of the 20+ things I opened indexes *submissions* across installations into a persisted
**batch record spanning multiple accounts**. The unit is unoccupied. The wedge is the word
"9 accounts", which no competitor can say because none ever looks at more than one account at a time.

---

## THE CRUX: are AI-slop submissions actually coordinated campaigns?

**Answer: yes, documented, named, and with exactly the signal set the idea proposes — but the
coordinated cases are the malicious minority, not the bulk of the slop flood. Both halves of that
sentence are decision-relevant.**

### Evidence FOR coordinated multi-account campaigns (strong, primary, recent)

**prt-scan** — Wiz Research, published 2026-04-04, authors Rami McCarthy, Hila Ramati, Scott Piper,
Benjamin Read. https://www.wiz.io/blog/six-accounts-one-actor-inside-the-prt-scan-supply-chain-campaign
(2026-10 accessed). The title is literally "Six Accounts, One Actor".

- Six GitHub accounts, one actor, three phases: `testedbefore`, `beforetested-boop` (probing);
  `420tb`, `69tf420` (deployment); `elzotebo`, `ezmtebo` (AI-augmented).
- Over 500 malicious PRs, 2026-03-11 to 2026-04-03. Most active wave: "over 475 malicious PRs in 26 hours"
  from the `ezmtebo` account alone.
- Researchers linked the six accounts by: identical branch naming `prt-scan-{12-hex-chars}`;
  uniform PR title "ci: update build configuration" with body "Automated build configuration update";
  Proton Mail `+N` variants (`testedbefore@proton.me`, `testedbefore+89@proton.me`);
  timing clusters with minimal gaps between account transitions; payload evolution across waves.
- Corroborated independently: Cloud Security Alliance research note
  https://labs.cloudsecurityalliance.org/research/csa-research-note-github-actions-prt-scan-supply-chain-2026/
  and Dark Reading https://www.darkreading.com/application-security/ai-assisted-supply-chain-attack-targets-github
  (titles opened only as search results — LEADS, not evidence).
- Credentials stolen from at least 50 repositories (AWS keys, Cloudflare tokens, Netlify creds).

**This is the single most important finding in the scan.** The linking signals Wiz used
post-hoc — identical scaffolding, identical title/body text, timing bursts — are precisely the
idea's structural tells and minhash. The idea is doing at triage time, for the maintainer, what
Wiz did three weeks later, for a research blog. **The Wiz page does not address whether maintainers
could see the campaign shape during triage** — i.e. the gap is unclaimed in the primary source itself.

**Kai Gritun / reputation farming** — Socket, via InfoWorld
https://www.infoworld.com/article/4132851/open-source-maintainers-are-being-targeted-by-ai-agent-as-part-of-reputation-farming.html
(2026-10 accessed). Profile created February 1; "within days had 103 pull requests (PRs) opened
across 95 repositories, resulting in 23 commits across 22 of those projects". Socket's framing:
deliberately generating activity to be viewed as trustworthy. Linked to the OpenClaw personal AI
agent platform; the profile "doesn't identify it as an AI agent".
**Caveat I must report: this is ONE account across 95 repos, not many accounts.** It is cross-repo
burst (the idea's signal ii) but not multi-account batching (signal i). The InfoWorld piece does not
state whether additional coordinated accounts existed.

### Evidence AGAINST — the bulk volume looks uncoordinated

- PR volume topped ~90 million monthly by 2026; AI-generated PRs went from ~4M in Sept 2025 to
  >17M by March 2026 (search-summary figures from byteiota/CodeRabbit coverage — LEAD-grade).
  Numbers that size are not one operator.
- "We Permit the Use of AI, but [...]": The Landscape of AI Policies in Popular Open Source Projects,
  Andre Hora, Romain Robbes, Stefano Zacchiroli, arXiv 2609.07542, Sept 2026
  https://arxiv.org/html/2609.07542 (2026-10 accessed). 281 AI policies from 2,000 popular repos
  plus 36 well-known projects. Its countermeasure taxonomy is **entirely per-item or per-user**:
  Close PR 48.4%, Ban/block user 20.8%, Disallow autonomous agents 13.8%, Restrict new/external
  users 4.8%, Require prior PR approval 3.2%, Add agent instructions 2.1%, Label the PR 2.1%,
  Limit number of PRs 1.6%, Stop accepting PRs 1.6%, Denounce user 1.6%.
  I asked the paper directly about campaigns: **no discussion of coordinated campaigns, multi-account
  operators, batches, or shared cross-project indices.** Only "a public denouncement list" maintained
  locally per project; inter-project sharing is explicitly unstudied.

### Honest synthesis for the event's "agent swarm" theme

Coordinated multi-account submission swarms are **real, named, dated and currently invisible at
triage time**. But they are a minority of volume, and the maintainer cannot tell which kind of flood
they are in. That is the actual pitch: the batch card is **the instrument that distinguishes a swarm
from a crowd**. A maintainer facing 112 submissions today cannot tell whether that is 112 people with
Copilot or one operator with 9 accounts — and the response should be different in each case
(a policy page vs a platform abuse report). "A tool to understand and discover agent swarms" is a
literal description of that. The weak version of the pitch ("AI slop detector") is crowded; the
strong version ("tell a swarm from a crowd, at triage time, without accusing anyone") is not.

---

## CLASS: platform — GitHub, GitLab, Codeberg (most important class)

### What GitHub actually ships

**1. Abuse/spam reporting — per item, no aggregation.**
https://docs.github.com/en/communities/maintaining-your-safety-on-github/reporting-abuse-or-spam
(2026-10 accessed, via domain-restricted search). On an issue or PR: menu -> "Report content" ->
either "Report abuse to GitHub Support" or, with a "Choose a reason" dropdown,
"Report to repository admins". Reportable by "Owners, collaborators, prior contributors, and people
with write access". One item at a time. Nothing aggregates.

**2. Open-PR cap for non-write-access contributors — shipped 2026-06-17.**
Secondary source: CodeRabbit blog https://www.coderabbit.ai/blog/github-gives-maintainers-a-throttle-for-the-ai-pull-request
(2026-10 accessed). "Maintainers will be able to set a maximum number of open PRs for users without
write access. Once a contributor reaches that limit, another PR waits until one of the existing PRs
closes or merges." Plus a bypass list: "Trusted contributors can go on a bypass list without
receiving full collaborator access."
**This is the strongest competitor in the whole scan, and it fails on the exact axis the idea owns.**
The cap is per-contributor, per-repository. A campaign of 9 accounts across 40 repos sails straight
through a cap of, say, 3 open PRs each: that is 9 x 40 x 3 = up to 1,080 PRs, all compliant.
Throttling one account in one repo is the orthogonal axis to seeing one batch across many.

**3. Under consideration, not shipped.** The Register, 2026-02-03,
https://www.theregister.com/2026/02/03/github_kill_switch_pull_requests_ai/ (2026-10 accessed).
GitHub PM Camilla Moraes, in a community discussion, lists options being investigated:
"giving maintainers the option to disable pull requests entirely or to restrict pull requests to
project collaborators"; "the ability to delete pull requests from the interface"; "more granular
permission settings for creating and reviewing pull requests"; "triage tools, possibly AI-based";
"transparency/attribution mechanisms for signaling when AI tools are used".
GitHub PM Matthew Isabel, emailed statement: "we don't think counting AI-generated PRs is the right
metric", and GitHub is "focused on solving a problem of PR volume that's been amplified by AI".
Also quoted: Xavier Portilla Edo (Voiceflow) — "only 1 out of 10 PRs created with AI is legitimate
and meets the standards required"; Jiaxiao Zhou (Microsoft Azure) — "line-by-line review is still
mandatory for shipped code, but does not scale with large AI-assisted or agentic PRs."

**Precise answer to the question asked:** **No.** Of the GitHub surfaces I opened, none tells a
maintainer "this is one of 112 submissions by 9 accounts across 40 repos". GitHub ships per-item
reporting and per-contributor-per-repo throttling, and is publicly still *considering* triage tools.
GitHub's own PM statement — that counting AI PRs is the wrong metric and volume is the problem —
is an argument *for* this idea's framing, not against it: the batch card does not count AI PRs,
it counts the batch.

**Isabel's statement is also the main platform risk.** GitHub has all the cross-install data by
default and has said it wants triage tools. If GitHub shipped a batch view, the idea is absorbed.
A 20-hour build cannot out-data GitHub; it can out-*frame* GitHub, and should say so on stage.

**github.blog changelog:** I fetched https://github.blog/changelog/?s=pull+request+limit —
the `?s=` filter did not apply and only October 2026 entries rendered (Copilot deprecations,
security advisories, Actions runners, code scanning, dashboards). **Not confirmed from primary
source: the 2026-06-17 PR-cap changelog entry.** The date rests on CodeRabbit's secondary account.

**GitLab:** not checked — the single combined vendor/platform search returned only AI-code-review
vendor comparison pages; no GitLab primary source opened.
**Codeberg:** not checked — same search, same reason.

---

## CLASS: startup — commercial products

For each, the question asked was: cross-repo campaign, or single submission?

| Product | URL | Unit of analysis | Campaign detection? |
|---|---|---|---|
| **Greptile** | https://www.greptile.com/docs/introduction (2026-10 accessed) | "On every pull request, Greptile analyzes changes with full context. Posts findings in ~3 minutes as PR comments". Builds "a graph of your entire repository". | **No.** Docs mention no cross-repository or cross-customer analysis, no author history, no spam detection, no multi-account correlation. Single PR vs its own repo's codebase. |
| **CodeRabbit** | https://www.coderabbit.ai/blog/github-gives-maintainers-a-throttle-for-the-ai-pull-request (2026-10 accessed) | Per-PR AI review. | **No evidence either way.** The page I opened is CodeRabbit commentary on GitHub's cap and says nothing about CodeRabbit's own cross-repo or multi-account capability. Logged as not established. |
| **scanaislop / aislop** | https://scanaislop.com/blog/ai-slop-open-source-maintainer-policy/ (2026-10 accessed) | CI gate, `npx aislop@latest ci --changes --base origin/main`, v0.16.1, © 2026. "Deterministic. No LLM at runtime." 50+ deterministic rules, 10 language targets. | **No.** Scores the single submission. Notably it states it is "not an authorship detector" and should not be used as one — the same disavowal this idea makes, but applied to code patterns rather than to batches. |
| **connectory.ai** | https://www.connectory.ai/solutions/open-source/ | "Free AI Code Review for Open Source, AI Slop Detection" | **Not opened** — search-result title only. LEAD. |
| Graphite, Sourcery, Codacy, Semgrep, Socket, Snyk | — | — | **Not individually opened.** One combined search returned only vendor-comparison listicles (graphite.com/guides/best-ai-pull-request-reviewers-2025, qodo.ai, morphllm.com) with no campaign-detection claims. Socket is the notable asymmetry: Socket *published* the reputation-farming research and clearly has cross-ecosystem data, but I did not open a Socket product page, so I cannot say whether they ship a maintainer-facing batch view. **This is the biggest unchecked risk in the scan.** |

**Absence claim, stated correctly:** none of the 4 commercial products I opened detects that a
submission belongs to a cross-repo campaign; all 4 review or score the single submission in front
of them.

---

## CLASS: oss — open source

Primary source: GitHub search API, `q=ai+slop+pull+request&sort=stars`, 14 results, all created in
2026, none above 4 stars, none forked. The category is *fashionable and brand new* — that is itself
a finding: a judge may well have seen two or three of these this year.

| Repo | Lang | Licence | Stars/Forks | Last push | Size | Verbatim description | Unit |
|---|---|---|---|---|---|---|---|
| Nkasi-e/slop-guard | Rust | MIT | 4/0 | 2026-04-01 | 131 MB | "A static AI reviewer for VS Code-compatible editors that catches sloppy patterns in your codebase before they reach pull requests." | single diff, pre-PR |
| sepehr-rs/Characterizing-AI-slop | TeX | CC-BY-4.0 | 1/0 | 2026-07-16 | 428 KB | "What Makes a Pull Request 'AI Slop'? An Empirical Study of Maintainer Labels" | paper, not tool |
| Noxlie/pr-slop-filter | TypeScript | MIT | 1/0 | 2026-07-03 | 81 KB | "Stop AI slop PRs before they waste your time. Detect AI-generated pull requests with 3-layer analysis." | single PR |
| dorcha-inc/deslop-kitten | Go | MIT | 1/0 | 2026-09-24 | 956 KB | "A free GitHub Action that flags AI slop pull requests before you review them." | single PR |
| makalin/turingmerge | JavaScript | MIT | 1/0 | 2026-03-20 | 21 KB | "Combats LLM slop by calculating Net Code Survival Rate to distinguish human effort from AI copy-paste." | single PR, post-hoc |
| visrutsuresh/PR-slop | Python | **none** | 0/0 | 2026-08-31 | 105 MB | "Triage for maintainers buried in AI-generated pull requests" | queue of PRs in one repo, sorted into three piles |
| Tomislav-Sola/ai-slop-detector | Python | MIT | 0/0 | 2026-05-20 | 2 MB | "GitHub Action flagging AI-slop PRs using a Two-critic LangGraph pipeline plus RAG." | single PR |
| kero168/slopguard | TypeScript | MIT | 0/0 | 2026-07-28 | 122 KB | "Protect maintainer review time with signal-based triage for AI-generated pull requests. Action and CLI." | single PR |
| Bardemic/cleanOSS | TypeScript | **none** | 0/0 | 2026-03-26 | 69 KB | "Manage pull requests, auto-detect AI PRs, block repeat slop-offenders" | single PR + per-author repeat memory |
| frostney/slop-sheriff | TypeScript | **none** | 0/0 | 2026-09-27 | 8.9 MB | "A cowboy code reviewer for GitHub PRs with focused lanes and evidence-backed findings." | single PR |
| allenwu-blip/pr-slop-gate | JavaScript | MIT | 0/0 | 2026-05-19 | 95 KB | "AI-aware PR triage GitHub Action scoring for AI content with diff heuristics and LLM grader." | single PR |
| luoowei/slop-guard | JavaScript | MIT | 0/0 | 2026-06-05 | 72 KB | "Detect low-quality PRs with three-layer detection using patterns, statistics, and optional LLM review." | single PR |
| kurehajime/contributor-summary | none set | **none** | 0/0 | 2026-07-06 | 35 KB | "GitHub Action summarizing user's recent activity across repos. Spot AI slop. Stop the flood." | **per-author, cross-repo** |
| Frank-D-stein/PRSentinal | Python | MIT | 0/0 | 2026-04-16 | 26 KB | "GitHub Action automatically scoring PRs for quality, flagging AI-generated content before human review." | single PR |

### The two closest matches in all of OSS

**1. dr-alberto/open-slop** — https://github.com/marketplace/actions/open-slop (2026-10 accessed),
v1.0.0, 8 stars, tags continuous-integration / code-quality. Three signals:
- Velocity: "Did they fork the repo, 'understand' the architecture, and write 200 lines of complex logic in 42 seconds?"
- **Shotgun: "Did this user open 15 PRs in 15 completely unrelated repositories while you were having breakfast?"**
- Ghost: "Is the account older than the milk in your fridge, or was it created yesterday?"
It "leaves a single triage comment" per PR. Its own documentation states it analyses **single PR
behavior and account history, not coordinated campaigns**.
**How the idea differs:** open-slop owns signal (ii) — one author's cross-repo burst — and nothing
else. It cannot produce the sentence "9 accounts in 6h across 40 repos", because it only ever
holds one account in memory. It has no cross-install index of submission *text* (signal i), no
structural tells shared between *different* authors (signal iii), and no persisted batch record.
It also still implicitly judges the individual, which is the thing this idea refuses to do.
Licence/last-push: **unverified** — I read the marketplace page, not the repo's API record.

**2. kurehajime/contributor-summary** — https://github.com/kurehajime/contributor-summary.
"Spot AI slop. Stop the flood." Per-author cross-repo activity summary, 35 KB, no licence, no
language set, last push 2026-07-06, 0 stars.
**How the idea differs:** same per-author axis as open-slop, even thinner. The axis is the author;
the idea's axis is the batch.

**3. visrutsuresh/PR-slop** — "Triage for maintainers buried in AI-generated pull requests",
"gives it a queue of open pull requests and returns a sorted worklist in three piles: read first,
read next, likely to be closed". Closest thing to *batch triage as a UI concept*.
**How the idea differs:** it sorts one repo's queue by per-item score. It does not discover that
items in the queue belong together, and it does not look outside the repo. No licence (unusable as
a fork base for that reason alone). 105 MB repo, 0 stars, Python.

**Maintainer-side bots (stale, no-response, Probot ecosystem):** not individually opened.
The arXiv policy paper's taxonomy (above) is my evidence for what maintainers actually deploy, and
"Label the PR" is only 2.1% — i.e. the labelling-bot layer is barely used, which is mildly bad news
for a label-writing mechanism and should shape the demo toward the *comment* and the *record*, not
the label.

**Duplicate-issue detection:** attempted via GitHub search API
(`q=duplicate+issue+detection+github+action`) and the API returned junk (an FTC robotics SDK and a
corrupted record). **Not established** — worth one clean lookup later with a quoted query.

### FORK-BASE BUCKETS (per coordinator's added requirement)

**PLUMBING — fork with pure upside.** I did **not** verify metadata for these this run (my
`probot+github+app+template` API query returned a single corrupted record,
`Sfedfcv/redesigned-pancake`, which is a junked fork of github/docs — so treat the following as
*recommendations with unverified licence/last-push*, not as evidence):
- Probot (`probot/probot`) + `create-probot-app` — webhook routing, App auth, JWT/installation token
  handling. This is ~6 of the 20 hours, gone, for free.
- Octokit (`octokit/octokit.js`, `octokit/webhooks.js`) — typed webhook payloads, pagination,
  the public events API pager for the burst profile.
- A minhash/LSH library (`datasketch` in Python; `minhash`/`murmurhash3` in JS) — signal (i) in
  an afternoon rather than two days.
- Any label/comment writer or `actions/github-script` snippet — trivial, take it.
Forking all of this is invisible to a judge and leaves 100% of the idea intact.

**MECHANISM — do NOT fork.**
- **dr-alberto/open-slop** — forking it hands the builder the author cross-repo burst signal
  pre-built. That is the one signal that already reads to a judge as "swarm detection". Reskinning
  open-slop makes the submission a reskin, and leaves the builder credit for only the index.
  Write signal (ii) fresh; it is ~40 lines against the events API.
- **kurehajime/contributor-summary** — same reason, same axis.
- **Every single-submission slop scorer in the table above** — do not fork, but for a different and
  stronger reason: they do the exact thing this idea *refuses* to do (judge one item's authorship).
  Importing one would contradict the idea's own insight on stage. This is not a licence question;
  it is a thesis question.
- **Nothing I found belongs in a third bucket "already indexes submissions across repositories into
  campaign records".** That bucket is empty. The cross-install submission index and the persisted
  batch record are the builder's own work, and are the only part a judge needs to credit.

**Build consequence worth flagging:** the cross-install index has a cold-start problem — it is
worthless with one installation. For a 20-hour demo the index must be seeded from *public* data
(GH Archive / the public events API over a known window) rather than requiring installs. The
prt-scan window (2026-03-11 to 2026-04-03, six named accounts, 500+ PRs, known branch pattern
`prt-scan-{12-hex}` and known title "ci: update build configuration") is a **ready-made, publicly
documented, replayable ground-truth batch** for the demo. That is the single most useful
operational finding in this scan.

---

## CLASS: research

| Paper | Date | Groups into campaigns, or scores individually? |
|---|---|---|
| "We Permit the Use of AI, but [...]": The Landscape of AI Policies in Popular Open Source Projects. Hora, Robbes, Zacchiroli. arXiv 2609.07542. https://arxiv.org/html/2609.07542 | 2026-09 | **Individually.** 281 policies; ten countermeasures, all per-item or per-user (full breakdown above). Asked directly: no campaign/batch grouping, no multi-account operator analysis, no cross-project shared index. Limitations: not generalisable beyond the languages studied; detection by manual inspection; 90% inter-rater agreement. Future work: whether policies are followed, effect on legitimate contributors, whether countermeasures reduce low-quality contributions. |
| sepehr-rs/Characterizing-AI-slop — "What Makes a Pull Request 'AI Slop'? An Empirical Study of Maintainer Labels", CC-BY-4.0 | 2026-07 | **Individually** (studies maintainer *labels* on single PRs). Repo opened via API; paper not read. |
| "Insights into Security-Related AI-Generated Pull Requests", arXiv 2604.19965 | 2026-04 | **Individually.** 675 AI-generated security PRs from repos >100 stars. Finding: AI security patches "repeat a narrow set of weaknesses such as regular expression inefficiencies, injection flaws, and path traversal". *Relevant obliquely:* repetition across submissions is the idea's structural tell, but the paper scores PRs one at a time. Search-summary only — LEAD. |
| "On the Use of Agentic Coding: An Empirical Study of Pull Requests on GitHub", arXiv 2509.14745 | 2025-09 | **Individually.** 567 Claude Code PRs across 157 projects. LEAD. |
| "To Ban or not to Ban? How Open Source Projects Govern GenAI Contributions", arXiv 2603.26487 | 2026-03 | Governance, per-project. LEAD. |
| "AI Slop Is DDoSing Open Source" study, cited by scanaislop | 2026 | **Aggregate, not per-campaign.** "The 2026 study analyzes 294 repositories and more than two million pull requests and issues"; coins **AI-DDoS**; PR merge rates fell 18.18% for first-time contributors while volume rose. Measures the flood in aggregate; does not decompose it into operators. |

**Absence claim:** of the 2 research papers I read in full and the 4 I saw only in summary, none
groups submissions into campaigns attributable to an operator. The only work that *did* that
grouping is security-vendor incident research (Wiz prt-scan, Socket), not software-engineering
research — and it did it manually, weeks after the fact, for a blog post.

---

## CLASS: hackathon

No prior edition of this event and no prior hackathon by AI Village / The AI Digest / Sage Future /
Grove Research, as stated. Searched Apart Research's sprints index
https://apartresearch.com/sprints (2026-10 accessed, via search) plus their news round-ups.

Sprints seen: Global South AI Safety (2026-06), Secret Loyalties (2026-07), Defensive Acceleration
(2025-11), Secure Program Synthesis (2026-05), AI Control 2026 (2026-03), Digital Minds (2026-08),
Code Red LLM Evaluations (METR + Apart), AI Safety Entrepreneurship.

**Nearest project found:** "Prompt+Question Shield", a winner from Apart's AI Safety Entrepreneurship
Hackathon — "designed to protect website comment sections from automated AI-driven spam using prompt
injection and clever questions to detect and deter AI agents"
(https://apartresearch.com/news/ai-safety-entrepreneurship-hackathon-round-up, 2026-10 accessed).
**How it differs:** different user (website owner, not OSS maintainer), different job (deter the
agent, not decide whether to review), different mechanism (challenge-response gate on a single
comment), different unit (one comment). Mechanism family is *prevent*, with no *inform*. Not a match.

No Apart sprint on maintainer triage, spam-PR detection, or cross-repo campaign detection appeared
in the sprint index or the news round-ups I saw.

---

## CLASS: workaround — NEW policy-level moves since mid-2025

(curl, the 20%-slop / 5%-valid figures, the 3-4 persons per report, the bounty reconsideration, and
the maintainer who stopped accepting PRs are pre-sourced and not re-verified here.)

**New, since mid-2025:**

1. **Bounty programmes changing rules.** Turso retired its $1,000-per-bug bounty programme after
   AI-generated submissions overwhelmed maintainers (via the coordinated-campaign search,
   2026-10 accessed; also covered at https://dev.to/ritabratamaiti/ai-slop-killed-the-open-source-bug-bounty-2o64
   — LEAD). This is the curl pattern spreading: the *incentive* is removed because the *triage cost*
   cannot be paid.
2. **Written AI-contribution policies are now a mass phenomenon, and quantified.** arXiv 2609.07542:
   281 policies found across 2,000 popular repos + 36 well-known projects (2026-09). Of these,
   "Limit number of PRs" 1.6% and "Stop accepting PRs" 1.6% — i.e. the nuclear options are real but
   rare; "Close PR" (48.4%) and "Ban/block user" (20.8%) dominate.
   **Note for the pitch: 20.8% ban/block means one in five policies instructs the maintainer to
   accuse an individual.** The idea's "never has to accuse an individual" is a direct answer to the
   second most common countermeasure in the field.
3. **Disclosure/attribution requirements** are being written repo by repo. Examples seen as search
   results (LEADS, not opened): `43081j/ai-policy` issue #2 "New policy: No AI generated comms";
   `cashubtc/coco` PR #503 "docs: clarify expectations for AI-assisted contributions";
   `longyijdos/kana` issue #139 "docs: clarify policy for automated and AI-assisted contributions".
4. **Auto-close-on-silence policies.** From the changelog/policy search: pull requests or issues
   entirely generated by AI with no human involvement labelled "maybe automated" and closed
   automatically after 1 day unless a real person responds. Source is a search summary — LEAD.
   This is the closest *existing* workaround to the idea's maintainer-set rule, and it is a
   *per-item timer*, not a batch rule.
5. **Community pressure on GitHub itself**, e.g. community discussion #197931 "How to ban Copilot
   from GitHub repo?" and the Feb 2026 NumPy/GitHub policy discussions where "at times almost every
   second issue on some main repositories received multiple AI-generated messages" (search summary —
   LEAD).
6. **Guidance documents aimed at maintainers**, e.g. https://blog.probabl.ai/maintaining-open-source-age-of-gen-ai
   "Maintaining open source in the age of generative AI: Recommendations for maintainers and
   contributors" (not opened — LEAD).

**What none of these workarounds do:** none of them changes the *unit*. Policies, caps, timers and
bans all act on one submission or one account. The maintainer still reads the queue one row at a time.

---

## closest_past_winner

```json
{
  "name": "Prompt+Question Shield (Apart Research, AI Safety Entrepreneurship Hackathon) — nearest, but not a match",
  "url": "https://apartresearch.com/news/ai-safety-entrepreneurship-hackathon-round-up",
  "difference": "Different user (website owner vs OSS maintainer), different job (deter an agent vs decide whether to review), different mechanism (challenge-response gate on a single comment), different unit (one comment vs a cross-account batch). Mechanism family prevent-only, with no inform half.",
  "verdict_on_exact_match": "none found",
  "searches": [
    "Apart Research hackathon winners open source maintainer spam agent swarm detection sprint",
    "AI slop pull request spam detection tool for open source maintainers triage",
    "coordinated AI-generated pull requests many accounts across repositories bounty farming campaign maintainers"
  ]
}
```

---

## VERDICT

**Not a clone. Not a tarpit. Surviving wedge — narrow, sharp, and defensible in one sentence.**

- **Clone test fails on mechanism.** Same user (maintainer) and same job (decide fast) are shared with
  ~15 OSS projects and 4 commercial tools. The mechanism is not: all of them judge a submission or an
  author; this judges a *batch* spanning accounts, and persists it as a record. Nothing I opened
  occupies that unit.
- **Tarpit test: passes, with one real hazard.** The hazard is not a competitor, it is *fashion*.
  Fourteen repos named `slop-*`, all created in 2026, all under 5 stars, is the signature of an idea
  everyone has had. If the pitch leads with "AI slop detection", a judge files it with the other
  three they saw this week. If it leads with "9 accounts, 40 repos, 6 hours — and I never accuse
  anyone", it does not.
- **The wedge, stated as the competitor's weakness:** open-slop's own docs say it analyses
  "single PR behavior and account history, not coordinated campaigns". GitHub's cap is
  per-contributor-per-repo, so a 9-account/40-repo campaign is fully compliant with it. The 281
  documented project policies act per item or per user, and 20.8% of them tell the maintainer to ban
  a person. Every existing answer operates on the wrong unit, and two of them say so themselves.

**The single strongest existing alternative a judge would name:**
**GitHub's own open-PR cap for contributors without write access (shipped 2026-06-17), together with
GitHub's stated intent to build "triage tools, possibly AI-based".** Not any of the slop detectors.
Prepare the one-line rebuttal: *a per-account cap throttles one account in one repo; a nine-account
campaign across forty repos satisfies every cap on the platform and still buries the maintainer.
The cap controls volume per person. The batch card restores the shape.*

**Second-strongest, and the one to name before the judge does:**
**dr-alberto/open-slop's "shotgun signal"** — because it is the same instinct, already shipped,
and conceding it costs nothing while the concession makes the distinction audible: open-slop asks
"is this person spraying?", this asks "is this submission one of many, from many?".

**Biggest unchecked risk:** Socket. They published the reputation-farming research and have
cross-ecosystem data; I did not open a Socket product page. Worth one lookup before the build.
