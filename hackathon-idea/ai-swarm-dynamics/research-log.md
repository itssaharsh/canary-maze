# research-log.md
Subagent D · 2026-10-02 · budget: ~30 web searches/fetches (halved, event starts within a day)
**Spent: 30 (29 fetches + 1 search). 24 produced usable content; 3 refused/404; 3 opened but empty or moved.**

Tools used: the web search and web fetch tools only. **No curl, no scripts, no mirrors,
no archives, no caches.** Refused fetches were treated as FINAL and not retried from
another host.

Order of lookups, in batches of four run in parallel.

## Batch 1 — three kinds of source (code-host API, forum, org engineering blog)
| # | Query / URL | Result |
|---|---|---|
| 1 | `api.github.com/search/issues?q=AI+generated+spam+in:title+is:issue+is:open+sort:reactions-desc` | OK — 2 issues, both 0 reactions → E5 (absence signal) |
| 2 | `hn.algolia.com/api/v1/search?query=AI crawlers&tags=comment` | OK → E7(author income), E17(Read the Docs), E22($25 audits) |
| 3 | `diff.wikimedia.org/2025/04/01/how-crawlers-impact-the-operations-of-the-wikimedia-projects/` | OK → E18 (primary, +50% bandwidth, 65%/35% split) |
| 4 | `api.github.com/search/repositories?q=anubis+bot+protection&sort=stars` | OK → E21 (third-party installers, Swiss hosting CLI, Helm chart) |

## Batch 2 — maintainer blog, community project page, forum
| # | Query / URL | Result |
|---|---|---|
| 5 | `api.github.com/repos/TecharoHQ/anubis` | OK → E20 (22,995 stars, created 2025-03-17) |
| 6 | `daniel.haxx.se/blog/2025/07/14/death-by-a-thousand-slops/` | OK → E1 (the strongest primary item in the run) |
| 7 | `en.wikipedia.org/wiki/Wikipedia:WikiProject_AI_Cleanup` | OK → E6 (300+ participants, "indistinguishable from human text") |
| 8 | `hn.algolia.com/api/v1/search?query=multi-agent debugging&tags=comment` | OK → E28, E29, E30 (self-built workarounds) |

## Batch 3 — vendor community forum, standards body, forum, code-host API
| # | Query / URL | Result |
|---|---|---|
| 9 | `meta.discourse.org/search.json?q=AI generated spam signups` | OK → E16, E36 (admin's own words on the signup API endpoint) |
| 10 | `datatracker.ietf.org/doc/draft-meunier-web-bot-auth-architecture/` | OK → E35 (v05 2026-03-02, expired, replaced) |
| 11 | `hn.algolia.com/api/v1/search?query=agent swarm&tags=comment` | OK → E32, E38 (and surfaced the UNCTAD thread) |
| 12 | `api.github.com/search/issues?q=bot+accounts+coordinated+in:title+is:issue+sort:reactions-desc` | OK → E25 (the agent-populated venue allegation) |

## Batch 4
| # | Query / URL | Result |
|---|---|---|
| 13 | `api.github.com/repos/aibtcdev/agent-news` | OK → E26 |
| 14 | `de.wikipedia.org/wiki/Wikipedia:WikiProjekt_KI-Inhalte` | **HTTP 404 — not accessible.** A guessed URL; no such page under that name. This is the reason I have **no non-English wiki-patroller evidence**, reported as a gap rather than papered over. Not retried (no budget to hunt the correct title). |
| 15 | `api.github.com/search/repositories?q=multi-agent+observability+created:>2026-01-01&sort=stars` | OK → E31. **This single lookup killed problem P6.** |
| 16 | `upwork.com/nx/search/jobs/?q=bot detection moderation` | **HTTP 403 Forbidden — FINAL.** Logged as not accessible; no retry, no alternate host, no scraping tool substituted. Cost: one freelance-spend signal for P5. |

## Batch 5
| # | Query / URL | Result |
|---|---|---|
| 17 | `api.github.com/search/repositories?q=coordinated+inauthentic+behavior+detection&sort=stars` | OK → E9 (11 tools, all human-social-media signals, ≤1 star) — the prior-art probe behind P2's wedge |
| 18 | `blog.cloudflare.com/signed-agents/` | OK → E24 (GA 2025-08-28, five named agents) |
| 19 | `boards-api.greenhouse.io/v1/boards/discord/jobs` | OK → E27 (11 safety/security engineering roles) |
| 20 | `langfuse.com/changelog` | **HTTP 404 — not accessible.** Intended as an absorption check on an LLM-observability incumbent. Not retried; E31's repo scan covered the absorption question for P6 instead. |

## Batch 6
| # | Query / URL | Result |
|---|---|---|
| 21 | `opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/` | **Opened but empty** — the page states the GenAI conventions "have moved to the OpenTelemetry GenAI semantic conventions repository" and is "no longer maintained in this repository". No attributes, no dates. Recorded as a lead, not evidence. |
| 22 | WebSearch: `arxiv 2026 attributing text to which LLM generated it model attribution accuracy benchmark` | OK — returned leads only; used to pick lookup #28 |
| 23 | `indeed.com/jobs?q="coordinated inauthentic behavior"` | **HTTP 403 Forbidden — FINAL.** Logged as not accessible. Cost: the second independent employer needed to make P5's spend signal STRONG; P5 was killed partly for that reason. |
| 24 | `en.wikipedia.org/wiki/Category:Articles_containing_suspected_AI-generated_texts` | OK → E7 (7,619 articles; 1,155 in Sep 2026) |

## Batch 7
| # | Query / URL | Result |
|---|---|---|
| 25 | `anubis.techaro.lol/docs/user/known-instances` | **Opened but no list rendered** — only the site's own "Protected by Anubis / From Techaro" footer came back. Named-adopter claims therefore **unverified**; E21 (third-party tooling) carries the adoption argument instead. |
| 26 | `developers.cloudflare.com/ai-crawl-control/` | OK → E23. The decisive prior-art probe for P4: named-crawler visibility and allow/block, nothing on operator attribution or correlating agents acting together. |
| 27 | `hn.algolia.com/api/v1/search?query=AI generated pull requests&tags=comment` | OK → E2, E3, E4 (three further independent maintainers) |
| 28 | `arxiv.org/abs/2501.02406` | OK → E37. Notable **negative** result: the abstract gives no accuracy figure, no model count and no text-length threshold, so no solution in this run assumes an attribution accuracy number. |

## Batch 8 — final two, both spent on prior-art probes
| # | Query / URL | Result |
|---|---|---|
| 29 | `api.github.com/search/repositories?q=LLM+provenance+fingerprint+detect+which+model` | OK → E10. `total_count: 0`, `incomplete_results: false`. Recorded as a **weak** absence signal scoped to those terms, not as proof of absence. |
| 30 | `incidentdatabase.ai/apps/incidents/` | **Opened but JavaScript-rendered** — no incident count, no field list, no taxonomy returned. Consequence: default **D8 ("an incident aggregator already exists") is unverified**, so I did not cite it as a reason to kill D8; D8 is set aside as a converged default, not as a proven duplicate. |

## Things I deliberately did NOT search
- The event, its project gallery, its hosts, its sponsors, or any person connected to
  them. No lookup in this log touches them.
- The requester, their team or their past work. No memory or profile tool was called.
- I did not request access to the gated multi-agent transcript corpus named in the brief,
  and none of the surviving solutions depends on it — all five run on public data an
  operator, maintainer, patroller or admin already holds.

## Budget notes
- 3 hard refusals/404s (#14, #16, #20, #23 — four counting #20) cost me: a non-English
  wiki group, two freelance/job spend signals, and one incumbent changelog. Each is
  named in `discovery.md` as a gap in the relevant problem's "missing voices" or in §8.
- The single highest-return lookup was #15 (multi-agent observability repos), which killed
  a problem I would otherwise have carried into Stage 4.
- The single best evidence item was #6 (curl), the only source in the run that publishes
  its own measured cost per incident.
