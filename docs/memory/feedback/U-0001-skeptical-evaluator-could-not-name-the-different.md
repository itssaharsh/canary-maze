---
id: U-0001
type: feedback
title: Skeptical evaluator could not name the differentiator from the UI stills
status: active
scope: project
components: viewer/index.html, ui-prototype/index.html
triggers: designing the viewer, writing viewer copy, adding a state to the viewer
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

A fresh evaluator given only screenshots said: 'The differentiator? I cannot tell.' The one claim that makes this evidence rather than a dashboard, 'server not contacted', rendered as 11px monospace in a grey box in a state the user must trigger. It also found three on-screen contradictions caused by HARDCODED copy: the partial state showed a fully populated Context B card while its headline said no other context had requested the secret; the error state asserted a sighting it said it could not read; and the scope paragraph was byte-identical across all states. Lesson: in this product every line of copy must be DERIVED FROM export.json, never hardcoded, because a tool whose thesis is honesty cannot contradict itself on screen. It also recommended replacing the sequence figure with a context DIFF (emphasise fields that differ, mute fields that match), which is both simpler and fixes the 320/390 illegibility. One finding was NOT reproduced: 'marker renders light pink in some states' - computed styles are identical across all four states.