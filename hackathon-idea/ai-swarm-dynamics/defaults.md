# defaults.md — pre-registered defaults (written BEFORE any search)

Written 2026-10-02, before a single lookup. These are the ideas I expect any
language model (including me) to produce for this brief with zero research.
They include **every organizer suggestion** and **every recycled category that
fits this theme**. Treat this file as a *do-not-return-here* list: any final
idea that matches one of these on (same user + same job) or (same job + same
mechanism) dies unless it carries a research-backed wedge.

## A. The organizer's own suggestion list (pre-registered — these are the MOST converged ideas in the room)

| # | Default idea | Why it converges | Recycled shape it maps to |
|---|---|---|---|
| D1 | **Swarm discovery crawler** — crawl public platforms (forums, registries, social) and flag clusters of agent-run accounts | organizer suggestion #1, verbatim | coordinated-inauthentic-behaviour detection (well-funded field) |
| D2 | **Better transcript summarizer** — hierarchical / map-reduce summarization of 170k agent messages into a readable brief | organizer suggestion #2 | document/thread summarizer |
| D3 | **Agent trajectory visualizer** — timeline + tree explorer for agent traces, zoomable, with search | organizer suggestion #2 | generic dashboard / LLM tracing (Langfuse, LangSmith, Phoenix all ship this) |
| D4 | **Standard question battery** — a runner that asks ~20 pre-written questions of any multi-agent group ("who leads?", "what is the goal?", "is anyone deceiving?") | organizer suggestion #3 | generic research agent + LLM-judge |
| D5 | **AI whistleblowing channel** — a tool/endpoint that makes it easy for an agent (or a human watching one) to report misbehaviour | organizer suggestion #4 | "an agent that does X" |
| D6 | **Information-spread tracer** — track how a claim, instruction or meme propagates through a group of agents | organizer suggestion #5 | graph analytics |
| D7 | **Open-source-intel / forensics tracer** — go beyond transcripts, use the web + digital forensics to reconstruct what happened | organizer suggestion #6 | generic research agent |
| D8 | **Incident aggregator dataset** — put every agent-swarm incident in one place, schema'd and queryable | organizer suggestion #7 | dataset-as-a-project; AI Incident Database already exists |

## B. The ideas every model adds unprompted

| # | Default idea | Recycled shape |
|---|---|---|
| D9 | Generic **multi-agent observability dashboard** (spans, token spend, error rates) | generic dashboard; "AI-powered" dashboard |
| D10 | **Chat with the corpus** — RAG over the transcript dump, ask it anything | chat with your documents/data (generic RAG) |
| D11 | **Agent-text detector** — classifier that says "this post was written by an agent" | content classifier; a wrapper on a model API |
| D12 | **Multi-agent simulation sandbox** — spin up N agents, watch emergent behaviour, screenshot it | a generic multi-agent system |
| D13 | **Embedding + UMAP cluster map** of agent messages, coloured by topic | generic dashboard |
| D14 | **LLM-judge intent scorer** — per message, score deception / goal drift / sycophancy 1-5 | "check X against rules and flag it" |
| D15 | **Anomaly detector over agent logs** — statistical outliers flagged for review | "check X against rules and flag it" |
| D16 | **Agent passport / identity registry** — attestations of who runs which agent, possibly on-chain | NFT/token-gated/cross-chain |
| D17 | **Browser extension** that labels agent-written posts on a social platform | content classifier wrapper |
| D18 | **Auto-written incident report** — feed the logs, get a post-mortem document | generic research agent; AI email/report writer |
| D19 | **MCP server exposing the corpus** so any model can query it | wrapper on a model API |
| D20 | **Slack/Discord digest bot** — "what did our agents do overnight?" | AI note taker / meeting summarizer |
| D21 | **Agentic SOC / triage queue** — agentic version of an existing SIEM workflow | agentic version of existing SaaS |
| D22 | **Swarm red-team harness** — inject a jailbreak into one agent, see if it spreads | generic multi-agent system |

## C. The single highest-risk reduction sentence for this event

> "The user gives 170k agent transcripts to a model and gets a summary / a list
> of suspicious clusters back."

Per the brief, this IS the reduction sentence, and it is what most entries will
be. Every candidate in discovery.md must be checked against it explicitly.

## D. Saturation notes carried into Stage 3

- Agents ≈ 1 in 4 community-hackathon submissions in 2026; chatbot prototypes
  were the typical 2025 AI-hackathon output.
- Already-crowded, well-funded adjacent fields that a prior-art probe must
  clear: LLM tracing/observability, agent evals, log analysis, graph analytics,
  bot detection, coordinated-inauthentic-behaviour detection, digital forensics.
- Everyone at this event has read the same incident reports. A problem reached
  *through* those reports needs a wedge specific to a segment or step others skip.

## E. Generation rules I will hold myself to

1. Seed from a **user group's own words**, never from the theme's words.
2. At least one non-US group and one non-specialist/consumer-adjacent group.
3. No lens supplies >1/2 the pool; rules/deadlines ≤1/3; capability lens ≤1/4.
4. If a batch comes back as duplicates of the above, change the SEED (different
   user, different kind of source), not the temperature.
