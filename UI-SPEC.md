---
name: Canary Maze
scope: sprint
one_line: "Canary Maze proves two automated clients shared a secret"
ambition: L1   # the data is 2-6 nodes and a handful of text records; the whole value is legibility of evidence read as a still. L2+ actively hurts: a glowing node graph is exactly the decoy-maze/screensaver reading the critic warned about.
registers: { claim: serious, figure: productive, records: productive, verification: system, honesty: system }
direction: "derived from the tamper-evident chain-of-custody form: canvas warm document stock #FDFCFA · ink printed near-black #16140F · accent serial vermilion #C8361B (the colour a unique serial is printed in on evidence-bag tape) · body Public Sans (the lettering of official records; US Web Design System) · mono IBM Plex Mono (unambiguous 0/O and 1/l/I, because hex secrets and IPs are compared character by character). Body candidates considered: Public Sans (chosen), Libre Franklin, Host Grotesk."
personality: precise
dials: { variance: 3, motion: 3, density: 7 }
stack: { page: "single HTML file", fonts: "Google Fonts (Public Sans, IBM Plex Mono)" }
superseded_prototype: "ui-prototype/ was the design source and was DELETED at cleanup: it hardcoded its copy, which is exactly the construction U-0001 blames for three on-screen contradictions. The shipped implementation is viewer/, which derives every line from canarymaze/export.py."   # no framework: one screen, no routes, no server state. The real app serves canary surface separately; this page reads a JSON export of the two ledgers.
archetype: "none of B13 — closest is (l) spatial scene + HUD with the scene replaced by a 160px sequence figure, because 2-6 lanes do not earn a canvas"
viewports: [320x640, 390x844, 1024x768, 1440x900]
signature:
  interaction: "the marker draws across the shared secret in the mint record, then in the sighting record 80ms later — the eye is led from issue to fetch"
  visual: "the shared secret is the only marked run of characters anywhere on the page, marked identically in both records"
wow: "click Verify bundle → the server is never contacted → the strip states the Merkle root, the row count and 'server not contacted' → the claim survives without trusting the operator"
demo: { seed: ./seed/sighting.json, flag: "?demo=1", state_param: "?state=", reset: "alt+shift+r", replay: "alt+shift+p", guest: true }
live_vs_simulated: [ "canary minting and sighting detection: live", "the seeded two-client replay: labelled seeded on the records themselves", "laundered-token semantic matching: shipped disabled" ]
deviations:
  - "Light only, no dark mode. I asked for dark-capable, then derived against it: the canonical artifact is a screenshot pasted into a written submission, and a dark still fights a light document. Logged rather than silently dropped."
  - "No card anywhere on the page. Nothing passes B5's card test: the records are a homogeneous pair, not a browsable set, and not movable. They get a sunken well instead."
  - "No texture, no grain, no grid. The records are the texture."
  - "accent is fill-only. --accent-text #BE3118 exists for the rare accent-coloured text case because #C8361B measured 4.485 on the sunken well, which fails 4.5 with no rounding."
---

## 0. Brief + context profile

- **One line:** Canary Maze proves two automated clients shared a secret.
- **User and moment:** the operator of a site or public API, at a desk, at the moment they have to show a third party what happened rather than just block it.
- **Primary action:** verify.
- **Hero object:** the pair of access-log records and the one string they share.
- **Product moment:** the marker lands on the same secret in both records.
- **Demo moment:** Verify bundle runs with the server stopped and still confirms.
- **Differentiator:** every other answer blocks, counts or guesses. This one records, and the record checks out without trusting the recorder.
- **Artifact:** the evidence bundle file, plus its verification output.
- **World inventory:** the raw access-log line · the HMAC secret string · the append-only ledger · the evidence bundle and its Merkle root · the chain-of-custody form with its serialised fields.
- **Moving truth:** the organic sighting counter, which changes only when a real sighting is recorded.
- **Judging:** no published criteria. Submission is a write-up or video + a public repo + optionally a results write-up. Judges are research staff at two research orgs, reading over about a week. No live demo slot for this entrant. Full detail in `hackathon-idea/ai-swarm-dynamics/idea-package.md`.
- **Budget:** ~4-5 UI hours inside a solo ~20-hour build. Nothing exists yet.

| Factor | This product |
|---|---|
| Task frequency | Once per investigation → explain, don't optimise for speed |
| Data density | A few records, each of which must be readable character by character → density 7, no truncation on the primary |
| Stakes | High. This makes a claim about a third party's behaviour → calm, high contrast, uncertainty stated on the face of the artifact, L0-L1 |
| Audience | Domain experts (researchers) → domain terms, no hand-holding, no tour |
| Use scene | Desk, and overwhelmingly **as a still image inside a written document** → light canvas, high contrast, screenshot-first |
| Emotional target | **Admissible** |
| Personality | Precise — ease-out-quint, 120-220ms, no bounce |
| Sponsor / host | None. No sponsor API exists at this event. |

## 1. Judge tests

**5-second answers.** A stranger sees two monospace access-log records, one above the other, with exactly one identical run of characters marked in both. Above them, one sentence naming what happened. They can say: it's about web traffic, and those two requests share something.

**30-second answers.** The loop completes without narration: the marker lands in both records → the sequence figure draws the arc from issue to fetch with the elapsed time on it → Verify bundle returns a Merkle root and the words "server not contacted" → the footer states how many sightings were organic and how many were seeded, and that zero human requests are in the ledger.

**Demo-critical screen:** one. The sighting record (`/`). Everything else is finished states, no flourish.

**The 3 stills:** (1) the marked record pair; (2) the verification strip with "server not contacted"; (3) the first-run state showing the seeded replay with the organic counter at 0 — because that is the state a judge is most likely to actually see, and it must not be embarrassing.

## 3. Screen inventory

| id | route | why it exists | entered from | primary action | states |
|---|---|---|---|---|---|
| S1 | `/` | the whole product: one sighting, its records, its verification | — | Verify bundle | ideal · first-run · partial · error · verified · verify-failed |
| S2 | `/ledger` | every mint and sighting row, for the reader who wants the rest | S1 "Open full ledger" | — | ideal · empty |

S2 is a plain table, built last, no flourish. No other screens: no auth, no onboarding, no settings, no history. The demo path has no login.

## 5. S1 — treatment table

| Element | Tier | Register | Levers (grayscale first) | States | Transition |
|---|---|---|---|---|---|
| **Record pair** — two access-log records, the shared secret marked in both | **primary** | productive | the largest region, full width, **sunken** so it reads as raw material rather than as our UI; IBM Plex Mono 14/22; every character present, no truncation, horizontal scroll inside the well rather than an ellipsis; the shared secret is the only marked run of characters on the page, marked identically in both records | first-run: the seeded pair, labelled seeded on the records themselves · partial: the mint record present, the sighting row reading "awaiting a sighting" · error: the record that loaded stays, the other states why | the marker draws left to right across the secret in the mint record (220ms), then in the sighting record 80ms later |
| **Sequence figure** — contexts as lanes, time left to right | secondary | productive | compact SVG, 160px tall, directly above the records; 2-6 lanes; lanes are 1px `line` rules with a 13px Public Sans label; one arc from mint to sighting carries the elapsed time | empty: lanes render with "nothing observed" on the axis · >6 contexts: "+N more", keeping the two named in the claim | the arc draws `pathLength` 0→1 over 320ms, after both markers have landed |
| **Claim sentence** | tertiary | serious | Public Sans 20/28 500, full width above the figure, set as content — not a hero headline; states only what the records support | — | — |
| **Scope limit line** | tertiary | serious | one 13px `ink-muted` line directly under the claim. Names what a sighting does **not** establish, and cites the measurement: one actor label in the AI Village dump spans 741 addresses | — | — |
| **Context blocks** — what A and B were (user-agent, ASN, first seen) | tertiary | system | two 13px blocks flanking the figure; labels Public Sans `ink-muted`, values IBM Plex Mono `ink`; a field that was not recorded reads "not recorded", never blank | — | — |
| **Verify bundle** | interactive | serious | the one filled vermilion button on the page, at the end of the record pair | idle · running "Verifying… 3/12" counted from real rows · pass → becomes the verification strip · fail → the strip names the row that failed and the records stay | on pass the button's container expands into the strip |
| **Verification strip** | secondary | system | full-width band under the records; IBM Plex Mono 13; Merkle root, rows checked, and the words "server not contacted" | — | expands from the button, 280ms |
| **Honesty footer** | tertiary | system | one line, page footer: organic sightings · seeded sightings · human requests in ledger 0. Content with numbers, **not** a badge in the top bar | — | counters roll only when a run adds to them |
| **Top bar** | tertiary | system | product name in Public Sans 600 15px, and one ghost "Open full ledger" at the right. No descriptor sentence, no status pill, no sample-data badge | — | — |

**Grouping:** spacing first — 32px between the figure and the records, 8px between the two records inside the well (they are a pair). The well is the boundary; no border, no shadow, no card.

## 9. Key copy

- Claim: `Secret 7f3a9c… was issued to context A at 11:04:12 and requested by context B at 11:08:47, 4m 35s later.`
- Scope limit: `A sighting establishes that the secret moved between two request contexts. It does not establish that they are two different operators — one operator can rotate addresses. In the AI Village dump, one actor label spans 741 of them.`
- Record labels: `issued to` / `requested by` (never "attacker", never "bot")
- Verify idle: `Verify bundle` · running: `Verifying… 3/12` · pass strip: `12 rows checked · root 9c4e…b1 · server not contacted`
- Verify fail: `Row 7 does not match the root. The records above are unchanged.`
- First-run: `No organic sighting recorded yet. Showing the seeded replay below.`
- Partial: `awaiting a sighting`
- Error: `Couldn't read the sighting row (ledger locked). The mint record is unaffected.`
- Honesty footer: `Organic sightings 0 · Seeded 1 · Human requests in ledger 0`
- Empty ledger: `No mints recorded. Start the middleware and point a crawler at the site.`

Sentence case everywhere. No "oops". No "AI-powered". The tool never calls a client an attacker.

## 11. Real-product checks

| Check | Answer |
|---|---|
| Value | Yes — the bundle is the deliverable an operator hands to a third party; the screen is how they read it first. |
| Clarity | One sentence, one figure, two records, one button. No tour. |
| Trust | Every number traces to a ledger row; the scope limit sits next to the claim, not in a footnote; no confidence percentage anywhere. |
| Feedback | Verify acknowledges in <100ms and counts real rows. |
| Failure | A failed verify keeps the records and names the row. A failed record load degrades to the other record. |
| 10× data | 2-6 lanes is the design limit; above 6 the figure collapses to "+N more" and the ledger table paginates at 20 rows. |
| Maintainability | One HTML file, two fonts, no dependencies. Every line explainable in Q&A. |

## 14. Tokens

```css
:root{
  color-scheme: light;
  --ff-display:"Public Sans",system-ui; --ff-body:"Public Sans",system-ui; --ff-mono:"IBM Plex Mono",ui-monospace;
  --canvas:#FDFCFA; --surface-1:#F4F2ED; --surface-sunken:#EFEDE7; --surface-2:#E6E3DC;
  --line:#D4D0C7;          /* dividers only, decorative */
  --line-input:#8A857A;    /* 3.583 on canvas · 3.283 on surface-1 · 3.138 on sunken */
  --ink:#16140F;           /* 17.949 on canvas */
  --ink-muted:#5C574C;     /* 7.008 canvas · 6.422 surface-1 · 6.137 sunken · 5.606 surface-2 */
  --accent:#C8361B;        /* FILL ONLY. white label = 5.251. 5.121 on canvas, so it may carry the focus ring */
  --accent-ink:#FFFFFF;
  --accent-text:#BE3118;   /* 4.925 sunken · 5.624 canvas · 5.154 surface-1 — use when accent must be text */
  --accent-hover:#B22F17;  /* white = 6.341 */
  --accent-press:#9C2914;  /* white = 7.662 */
  --focus:var(--accent);
  --success:#1F6A3D; --warning:#7A5200; --danger:#8E1F14;
  --r-sm:2px; --r-md:3px; --r-lg:5px;
  --ease-out-quint:cubic-bezier(.22,1,.36,1); --ease-in-out:cubic-bezier(.77,0,.175,1);
  --dur-press:120ms; --dur-hover:150ms; --dur-mark:220ms; --dur-arc:320ms; --dur-strip:280ms;
}
```

**Accent budget.** The accent appears exactly three places: the marker on the shared secret, the Verify button, the focus ring. Under 5% of pixels. `--danger` is text + word + icon only, never a fill, so it is never confused with the accent despite both being red-family — form distinguishes them, not hue.

## 13. Acceptance

A8 gates 1-4 (Sprint). Gate 2's skeptical evaluator runs on the built screenshots.
