---
id: ADR-0003
type: decision
title: Write the maze; do not fork Pyison
status: active
scope: project
components: canarymaze/maze.py
triggers: forking a serving layer, adding a dependency for the maze
evidence: ARCHITECTURE.md#Decisions
verified_at: 2026-10-02@81795d7
relates: 
supersedes: 
helpful: 0
harmful: 0
cite_hash: 41874f6bbd79ea0f
created: 2026-10-02
source: unknown
---

The build brief said to fork Pyison (MIT, 125 stars) for the serving layer. Reversed deliberately: the maze is the one component never demoed, the critic pass named 'forking an unfamiliar 125-star repo' as the most likely way to lose Saturday, and the maze needed is about 60 lines fully understood. Pyison is credited in the README as the alternative considered. This is a documented deviation from the brief, not an oversight.