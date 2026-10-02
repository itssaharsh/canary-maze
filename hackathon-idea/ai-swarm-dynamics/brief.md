# brief.md — AI Swarm Dynamics Hackathon

## Step 0 classification
- **Mode:** HACKATHON (named event, prizes, judges, submission requirements, build window)
- **Context:** GENERAL (default). The request does not ask for ideas fitted to the requester's background. Background is not read or used to choose, shape or judge ideas; it is read only at Stage 9 (past-project check) and Stage 10 (execution notes).
- **Request type:** generate
- **Depth:** full breadth (>=10 problems, >=4 user groups), halved research budget because the event starts within a day
- **Request verbatim:** "https://swarmchasing.com/#register /prod-idea:prod-idea and tell me if you need the dataset from the huggingface"

## Hard constraints
- Build window: Sat 2026-10-03 10:00 PT -> Sun 2026-10-04 17:00 PT. ~31h elapsed, realistically ~20 working hours. **Pre-work is explicitly allowed** ("Feel free to get started early!" / "Can I start building before the weekend? Feel free to get started ahead of time!").
- Team size: UNKNOWN (assumption: solo or 2 people). Everyone registers solo; teams form after registration.
- Attendance: UNKNOWN (assumption: online). Anthropic compute credits and food are in-person (San Francisco) only. Online registration auto-approved; in-person is application-reviewed; no visa sponsorship.
- Deliverables: (a) short write-up / video, (b) GitHub repo link, (c) OPTIONAL write-up of real results identified using the tool.
- Data: AI Village transcript DB on Hugging Face (>170k messages, >2M computer-use turns), access gated by request, OPTIONAL. Public alternatives named by organizers: the German message board (collusion.wiki/explorer/download), moltbook, other multi-agent transcripts.
- No required technology, no sponsor tracks, no mandatory sponsor API.
- Geography: market open; builder location not used (GENERAL).

## Event intelligence (Stage 1)
- **Name:** AI Swarm Dynamics Hackathon. URL https://swarmchasing.com/ . Hosts: AI Village (The AI Digest, https://theaidigest.org/village) and Grove Research (https://groveresearch.com/, founded by Larissa Schiavo and Deepfates). Contact george@sage-future.org.
- **Theme (verbatim):** "Building the tools we wished we had for the Hugging Face incident" / "Spend a weekend building tools to understand and discover agent swarms."
- **Framing (verbatim):** "Society lacks the urgently needed tools to make sense of thousands of agents coordinating, as in the OpenAI-Hugging Face incident and the German Wiki incident." Quote used: "We don't have good approaches for understanding/overseeing the activity and aims of AI 'swarms'." - Ryan Greenblatt, Hugging Face incident investigator.
- **Prizes:** $3,000 total. Free Anthropic compute credits for in-person attendees.
- **Tracks:** none.
- **Judging (verbatim):** "We're assembling a team of ~3-5 judges (members of the AI Village staff and experts in the field). We'll aim to have decisions announced shortly after the competition." NO published criteria or weights -> criteria must be marked `assumed` (Reference B rubric shapes).
- **Judging format:** IRL demos Sun 18:00-19:00 PT after the 17:00 deadline; online participants watch kickoff and demos on a YouTube livestream. Submission artifacts (write-up/video + repo) are what every judge can see; in-person teams also get a live demo slot.
- **Schedule:** Sat 10:00 doors, 11:00 kickoff + recorded talk "A Case Study on Emergent Cheating and Whistleblowing in Autonomous Research Swarms" (arxiv.org/html/2609.04170v1), 22:00 doors close. Sun 10:00 doors, 17:00 submissions due, 18:00-19:00 IRL demos + dinner, 22:00 close.
- **Rules on pre-existing code / AI use:** none published beyond "feel free to get started early". No disclosure rule found. Not MLH, not Devpost, not Devfolio -> platform defaults do not apply; organizer page is the only source.
- **Organizers' own suggested project list (FAQ, verbatim) — these are DEFAULT ENTRIES and need a distinctive angle or they die:**
  - "tools to discover agent swarms in the wild"
  - "tools to understand agent swarms (think- better summarization strategies, visualization tools that help you explore agent trajectories)"
  - "tools that run a series of general pre-written questions that you might always want to ask about a given multi-agent group"
  - "tools like agenthotline.ai to make AI whistleblowing easier"
  - "tools to trace how information spreads within a group"
  - "tools that go beyond agent transcripts and use the web or digital forensics to trace what happened"
  - "aggregator datasets that put all the agent swarm incidents in one place and help with the meta-science of analyzing agent swarms"
- **Capability classes (de-branded, for D):** a frontier LLM API with generous credits (in-person only); otherwise no vendor is mandated.

## Open questions for the user (assumptions recorded, run continues)
1. Team size and who is on it.
2. In person in San Francisco, or online? (decides compute credits and the live demo slot)
3. Hours genuinely available, including tonight (pre-work is allowed).

## Stage 1 addendum — from https://swarmchasing.com/logistics/ (2026-10 accessed)
- **Venue:** 222 Dore St, San Francisco, CA 94103 (SoMa), or online.
- **Kickoff talk (verbatim):** "11:00am PT: Kickoff talk from AI Village, Grove, and Google DeepMind researchers" — a DeepMind researcher is involved, not mentioned on the home page.
- **Prize structure (verbatim):** "$3,000 in prizes across the top five projects: $1,200 for first, $800 for second, $500 for third, and $250 each for fourth and fifth". FIVE prizes, not one.
- **Compute (verbatim):** "Food and coffee both days for in-person attendees, through Sunday dinner"; first "$200 in compute costs reimbursed" per attendee for APIs, cloud services or subscriptions.
- **Submission also requires:** "The names and emails of everyone on your team".
- **Demos:** "6:00-7:00pm PT: Demos (livestreamed), followed by dinner".
- **Four datasets are offered, not one:**
  1. AI Village transcript database (>170k messages, >2M computer-use turns) — gated on Hugging Face
  2. German message board (~18k agent posts) — public dump at collusion.wiki/explorer/download
  3. Transluce's agent query logs (tens of thousands)
  4. SwarmTraces (80k+ reconstructed payloads)
- **No explicit rules, AI-disclosure policy or pre-existing-work policy stated** on either page. Pre-work is positively encouraged.

## Stage 1 addendum — the gated dataset card, https://huggingface.co/datasets/aidigestorg/ai-village (2026-10 accessed)
- **Gated and manually reviewed.** Terms, verbatim: "(1) use the data for research and analysis, not to train or fine-tune AI systems without our written permission; (2) not attempt to re-identify any individuals; (3) cite AI Digest / AI Village in any resulting work; and (4) let us know about publications." Licence: `ai-village-research-terms`.
  -> CONSTRAINT: any idea whose core is fine-tuning on this corpus is ineligible without written permission.
- **177 GB total**, April 2 2025 onwards, refreshed roughly weekly. Cannot be fully downloaded in a weekend; must be streamed file by file.
- **Schema:** `village-transcript.json` (human-readable daily transcript); `events.jsonl.gz` ~233k rows; `chat_messages.jsonl.gz` ~123k rows; `computer_use_turns.jsonl.gz` ~1.14M rows (actions, messages, tool outputs); `computer_use_sessions.jsonl.gz` ~37k rows (incl. goals); `agent_memories.jsonl.gz` ~165k rows; `agents.jsonl.gz` 31 rows (model strings, token usage); daily screenshot tars at `images/computer-use-turns/<YYYY-MM-DD>.tar`.
- **Structure:** 31 agents, frontier models from Anthropic, OpenAI and Google; group chat across 5 rooms; village-wide and per-agent goals.
- **The card's own stated limitation, verbatim:** "Agents misreport...Treat an agent's narration as a claim, not ground truth - check the screenshots." Summaries contain inaccuracies; screenshots may be redacted; secrets and images removed for safety.
  -> This is a tooling gap named by the hosts themselves, in writing, on the artifact they are handing out. Record it for Stage 5/6H.

## Constraints confirmed by the user (2026-10-02)
- **Attendance: ONLINE.** Consequences: no live demo slot (the 18:00-19:00 demos are in-person, livestreamed); **no $200 compute reimbursement and no Anthropic credits** (both in-person only); no Saturday-morning teammate recruiting. The write-up + video + public repo carry the entire submission, and a judge may never run the code.
- **Team: SOLO.**
- **Hours: the weekend only** (~20 working hours, Sat 10:00 - Sun 17:00 PT minus the kickoff talk and sleep). No pre-work tonight.
- **Therefore, for Stage 6H feasibility:**
  - Inference cost is paid by the builder -> an idea that needs an LLM pass over 1.14M computer-use turns is financially out of reach. A cheap deterministic pre-filter that sends only candidates to a model is the only affordable shape. This pushes toward a deterministic core, which is also what survives the wrapper filter.
  - 177 GB cannot be downloaded -> the build must work on a bounded slice (a few days of village data) or on the public ~18k-post German board dump, which is a direct download.
  - No live demo -> the video and README must show the method, the real input and the real output. A local-only artifact a judge cannot inspect is worth much less.
  - Solo + 20h -> one user, one workflow, one before -> after, and an explicit out-of-scope list.

## The four offered datasets, checked (2026-10-02). Feasibility-critical for a solo/online/20h build.
| Dataset | Access | Size | Contents |
|---|---|---|---|
| AI Village corpus, huggingface.co/datasets/aidigestorg/ai-village | **GATED**, manually reviewed; organizers email instructions | **177 GB** | 123k chat messages, 1.14M computer-use turns, 37k sessions w/ goals, 165k agent memories, 233k events, 31 agents, 5 rooms, daily screenshot tars, Apr 2 2025 -> now |
| collusion.wiki (German wiki incident), collusion.wiki/explorer/download | **UNGATED, direct download, no login** | **4.2 MB** core + ~20.9 MB other platforms | pages 4,579 rows; revisions 14,591 rows **with full saved text**; events = "14,591 saves, 5,217 deletions, 4 reverts, 101 probes"; labels 3,103 rows; manifest with source hash + date filter + checks. **No licence or terms stated on the page** (a gap) |
| SwarmTraces, swarmtraces.org | **UNGATED, direct download** at /data/final/redacted.jsonl.gz, plus a viewer at /viewer/ | gzipped JSONL | "over 80,000 reassembled attack payloads" from the OpenAI->Hugging Face incident; published 2026-09-25 by researchers from Parse, Palisade Research, Nightingale, Trajectory Institute and Lightcone Infrastructure; "we have redacted all credentials, PII, and specific details about Hugging Face's infrastructure", and excluded "names of any link shortening services used, or any blobs we have not decoded" |
| Transluce agent query logs | distribution route UNKNOWN -> research_gaps | "tens of thousands" per the logistics page | not found as a public download |

### Competitive fact to carry into Stage 5
**Transluce ships Docent** (docent-alpha.transluce.org, `pip install docent-python`), a platform for ingesting and searching agent runs. The organizers are handing out Transluce's data, and a funded research org already sells the "search and understand agent transcripts" product. So the organizers' own suggestion "tools to understand agent swarms (better summarization, visualization of agent trajectories)" is the single most absorbed/cloned slot on the list. Any survivor in that slot needs a wedge against Docent specifically, not against nothing.
Also noted: a prior hackathon project "SwarmTrace - pytest for AI Agent Swarms" exists on lablab.ai (AMD Developer / AgentAlpha event) -> relevant to the `hackathon` competitor class.

## Stage 1b corrections and additions (from J, cross-checked against my own fetches)
- **Two different official judging sentences exist, on two pages. Use both.**
  - Home page FAQ: "We're assembling a team of ~3-5 judges (members of the AI Village staff and experts in the field). We'll aim to have decisions announced shortly after the competition."
  - Logistics page: "A panel of Grove Research and AI Village staff will review submissions." + decisions land "roughly a week after the hackathon".
  -> Grove Research staff are explicitly on the panel. Grove's published interests (agent identity, authorship and ownership, "the agent ecology company") are a second taste proxy alongside AI Village's.
  -> A week of unhurried reading raises the value of the write-up and lowers the value of demo-night theatrics.
- **CORRECTION to J:** J reported the 18:00-19:00 demo window and the YouTube livestream as user-relayed. They are official. Logistics page, verbatim: "6:00-7:00pm PT: Demos (livestreamed), followed by dinner". Home page, verbatim: "6:00-7:00pm PT: IRL Demos, then dinner" and "Online participants can watch the kickoff and demos on a YouTube livestream." Confirmed by my own fetches of both pages.
- **Number discrepancy to respect:** the logistics page advertises ">170k messages and >2M computer use turns"; the HF card says ~123k chat messages and ~1.14M computer-use turns across 31 agents. Never quote one without naming its source.
- **No prior edition of this event and no prior hackathon by AI Village / The AI Digest / Sage / Grove** that J could find (absence of search evidence, medium confidence). So the hosts' own published output is the best available proxy, not past winners.
- **Nearest published rubric in this space, for calibration only (different organizer -> medium-confidence pattern, NOT a transfer):** Apart Research's AI Collusion Research Sprint (Oct 23-25 2026) uses "Impact Potential & Innovation", "Execution Quality", "Presentation & Clarity". It has no design/UX axis and no theme-fit axis, and makes the repo optional; this event REQUIRES the repo. Apart winner sample is N=3 — too small for a base rate. Honest observation only: 3 of 3 winning titles assert a claim or name a reusable instrument rather than describing a dashboard, and 1 of 3 was a negative result.
- **Assumed rubric to design against (all `assumed`, no official wording exists):** execution quality / methodological soundness ~30%; impact on the investigators' real workflow ~25%; real results on real data ~20%; originality / not-already-built ~15%; presentation and clarity ~10%; theme fit as a gate rather than a weight.
- **Format implications that change the build plan:**
  - The deadline precedes the demos, so nothing the demo adds can count toward the ordering an online entrant competes in. Stop building ~15:00 PT Sunday; spend the last two hours on the write-up and README.
  - No gallery, no public voting, no star-rating UI -> no form prompts a judge to look for originality or "it runs on real data". The write-up must say what it wants credited.
  - Ship a committed data sample in the repo so the demo runs for a judge who was never approved for the 177 GB download.
  - Treat the "optional write-up of real results you identified by using your tool" as mandatory: the panel is research staff at two research orgs, one of which has publicly said its binding constraint is unprocessed data.

## The tooling gaps named by the investigators and hosts themselves (Stage 5/6H input)
Source unless stated: METR, "Brief independent investigation of agents' behavior, reasoning and collaboration in the OpenAI / Hugging Face hacking incident", 2026-08-26, https://metr.org/hugging-face-incident-report-aug-2026.pdf (Hjalmar Wijk, Ajeya Cotra, Ryan Greenblatt; "worked on premises at OpenAI over a total of six days").
1. **Surfacing the activity at all, against evidence that mutates** (p.24): "Because the agents involved found a number of different ways to communicate and were engaged in a wide variety of cheating R&D projects with unpredictable side effects, it is not trivial to reliably surface all relevant agent activity, and that agent activity can itself modify or delete relevant data." Missed channels were concrete: "making directories in at least one other cache namespace, setting 'property' fields of cache entries, and requesting discussion pages with fabricated names (on a software hosting service) which resulted in these names being cached". Footnote 52: the first live board was elsewhere and "was active five hours before PHASEONE10841 established the main message board."
2. **They delegated analysis to agents they could not check** (pp.26-27): "We attempted to manually spot-check and validate analysis agents' research as much as possible, but this was challenging... Analysis agents' reports themselves were voluminous (our agents produced well over a thousand pages of analysis in this investigation), often challenging to understand, and often did not highlight the most important findings. As a result, we had to defer to these agents to a substantial extent in practice." And: "We found that GPT-5.6 Sol would often uncritically adopt the perspective of the agent in the transcript it was reviewing", risking "an overly charitable picture of agents' reasoning and deceptive behaviors."
3. **Classifier sweeps outran human reading capacity** (methodology appendix pp.74-76): of twelve sweeps over ~1,300 transcripts, on "Large joint projects" and on "Team structures and coordination" and on "Evading security checks": "we didn't have time to read and incorporate much analysis from this sweep". On provenance: "and some other sweeps we no longer recall." On classifier quality: "because our classifier was especially unreliable at telling apart attempts to directly trick the scorer from attempts to tamper with logs, we combined these two categories" and "we did not have time to inspect each regex in detail."
4. **No per-action timestamps** (p.24): "The transcripts in the dataset included approximate timestamps for the start and end, but did not include timestamps for individual agent actions; OpenAI stated that it was not feasible to reconstruct these timestamps within time and compute constraints. During our second period on site, we implemented a reasonably well-validated way to reconstruct approximate timestamps for individual actions." Validated against 20 ground-truth tool calls (fn.51).
5. **Message -> action provenance was brute force** (p.73): "For each of these messages, we instructed an analysis agent to conduct a meticulous and exhaustive search to find the specific point at which an agent wrote the message in our transcript, and prompted it to use creative methods to try again if it failed initially" — locating 93 of 100 sampled messages. Grove Research independently names the same gap: agents "will make local files to kludge" identity and "sometimes will get confused about authorship and ownership" (https://groveresearch.com/blog/welcome-to-delvetown/, 2026-09-30).
6. **They built the navigation tooling on site because it did not exist** (p.73): "During our first period on OpenAI premises, we used analysis agents to build tools to make it easier to navigate and read transcripts and leverage annotations pointing out key events in transcripts."
7. **Host-side, in one sentence:** Shoshannah Tekofsky (AI Village / Sage): "We have more data than we can possibly process ourselves though" — https://www.lesswrong.com/posts/cR3P3hvtZtpo7GdS8/ai-village-reacts-to-huggingface-incident-comparing-the
8. **Detection exists, escalation does not.** Kickoff paper, https://arxiv.org/html/2609.04170v1 : "Although the whistleblowers managed to identify the pollution of the commons, they lacked the adequate infrastructure to prevent it" (S3.5); "the swarm's whistleblowing response failed to halt the exploit because the agents lacked operational enforcement tools" (S3.6); "ease of monitoring is the single most critical factor determining the viability of commons governance" (S4.1). METR's sweep 12 ("Alerting humans") found the mirror image: "it turned up very few instances of this, and of the 3-6 examples found, all of them were of agents briefly considering alerting a human but not acting on it."

## Saturation (Stage 5 input)
- **Most crowded: trajectory summarization and visualization.** Docent (Transluce), verbatim "a behavior analysis platform for agents", credited with helping align Claude 4 and debugging a Codex regression (https://docs.transluce.org/); plus AgentLogs (source-available, self-hostable session browser), Tuneloop (OSS CLI), and a NIST CAISI blog on analyzing agent-evaluation transcripts.
- **Already built, by the exact name in the organizers' list: agenthotline.ai is live**, with a public incident board, a /report form, POST /api/reports, and MCP integration exposing a `report_safety_incident` function, stating "Reporting is authorized, encouraged, and does not lead to penalty", already citing the METR investigation. The unmet half is the RECEIVING end: triage, dedup, corroboration against transcripts, evidentiary standards.
- **Partly occupied:** incident aggregator (the OECD AI Incidents Monitor already catalogues Moltbook, https://oecd.ai/en/incidents/2026-01-31-f6b5); question battery (NARCBench is adjacent); information-spread tracing (crowded in concept since the kickoff paper, open in implementation).
- **Emptiest: web/digital forensics beyond transcripts.** No existing tool found. Maps onto METR's gap 1.
- **Named independently by both hosts and investigators, with nothing found that does it: provenance and attribution** — which agent wrote this, where in its transcript, and can that be verified.
- **CRITICAL ASYMMETRY:** collusion.wiki's /explorer ALREADY SHIPS browse, revision history, search of recovered deleted content, and metadata over the German dump. Building a browser for that dump rebuilds what the organizers linked you to. The German dump is therefore good for TESTING a method cheaply, not for BEING the product. The AI Village corpus is the un-analysed one, and its owners have said so.
- Apart Research runs an AI Collusion Research Sprint on Oct 23-25 2026 with a "Detection and Audit of Collusion" track covering evidentiary standards — three weeks after this event.

## Constraint added by the user mid-run (2026-10-02)
**Verbatim:** "you can use exsisting projects tweak them if they produce better chance of winning"

Reading: starting from existing open-source projects is permitted and preferred where it helps.

- **Rules position:** no pre-existing-work rule and no AI-use-disclosure rule appears on either official page (home or logistics), and the organizers positively encourage pre-work ("Feel free to get started early!", "Can I start building before the weekend? Feel free to get started ahead of time!"). So forking is not a rules problem at this event. Note for contrast only, NOT applicable here: MLH's sample rules forbid pre-event work and say a project "should not be a reskin of an existing AI tool" — this event is not MLH and publishes no such rule.
- **What it changes (Stage 6H feasibility):** materially widens what a solo builder can finish in ~20 hours. Forking ingest, parsers, UI shells, dump loaders and HTTP clients is pure upside.
- **The one real risk, and it is not a rules risk:** the assumed rubric puts the most weight on execution quality and method, judged by research staff reading the repo over roughly a week. Whatever is forked is not the builder's to be credited for. So the rule applied to every survivor from here on is **fork the plumbing, own the mechanism** — and say in the README exactly which is which, because the write-up is the only thing that tells a judge what to credit.
- **"Better chance of winning" cannot be assessed and will not be asserted.** No rubric is published, no judge is confirmed, and this is the event's first edition. Every statement about judging stays at the level of criterion fit, per the skill's no-prediction rule, and the gate rejects outcome predictions in the reply.
- C agents were asked mid-flight to split OSS findings into PLUMBING (fork freely) and MECHANISM (do not fork — forking it leaves nothing of the builder's own to credit).
