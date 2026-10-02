# Fresh review — Canary Maze

Reviewer: fresh context, no stake in the build. Date 2026-10-02. Ships 2026-10-04 17:00 PT.
Read-only: no code changed, no git state changed. `git status --porcelain` is clean apart from
this file.

Ran: `python3 -m pytest -q` (89 passed), `make verify` (PASS, 5/5), `make demo` (PASS, 4 rows,
state `sighting`), the Flask surface on :8123 against a scratch DB, ~30 scripted attacks against
`gate`, `context`, `detect`, `bundle`, `app` and `export`, and a read-only read of the live
production ledger `canary.sqlite3`. Build artefacts (`viewer/data.js`, `viewer/data.json`,
`bundles/bundle.json`, `demo.sqlite3`) were backed up and restored around the `make demo` run.

The repository was being modified by another process during this review (`ui-prototype/` was
deleted and the `make clean` ledger bug was fixed while I read). Findings are against HEAD
`8027232` plus the Makefile fix.

---

## BLOCKING

### B1 — The viewer's verification button computes nothing. It prints an operator-supplied boolean.

`viewer/render.js:162-187` · `scripts/export_all.py:43-48` · `viewer/index.html:51-54`
(and the byte-identical `site/viewer/render.js`, live now)

`wireVerify()` reads `window.CANARY_VERIFY` out of `data.js` and prints `v.ok`. There is no
hashing anywhere in the viewer — `grep -riE "crypto|sha-?256|digest|subtle" viewer/ site/viewer/`
returns **zero hits**. The page is never given the leaves or the rows: `export_all.py` writes only
`{"ok": true, "rows": 4, "root_short": "fd33…47", "problems": []}`. The page is structurally
incapable of recomputing anything.

What it claims:

- `viewer/index.html:51-54` — "This button **recomputes every hash here, in your browser, from
  the bundle file alone.** It makes no request to our server…"
- `viewer/render.js:176-177` — prints "… **recomputed in this page from the bundle file alone**"
- `site/index.html` figcaption — "Recomputed in the browser, from the bundle file alone."
- `viewer/render.js:160-161` (code comment) — "Verification runs here, in the page, against the
  bundle the page was built from."

Failure scenario: open `site/viewer/index.html`, edit `data.js` so
`CANARY_DATA.sightings[0].requested.raw` reads any access-log line you invent, leave
`CANARY_VERIFY` untouched. The page renders the forged record and the button says "Verified. The
server was not contacted. 4 rows checked · root fd33…47". Equivalently: delete
`bundles/bundle.json` entirely — the page still says Verified, because no bundle is ever read.

Confirmed live: I fetched `https://site-nine-hazel-35.vercel.app/viewer/` and the copy is there
verbatim.

The Python verifier (`canarymaze/bundle.py`, `make verify`) is real. Only the viewer's claim is
false. Cheapest honest fix is to change the copy; the right fix is ~15 lines of
`crypto.subtle.digest` over a shipped `bundle.json`. As it stands this is worse than not shipping
the button, because the whole wedge is "check this without trusting us" and a judge with devtools
open finds the check is a constant.

### B2 — Anyone can inject an `origin='organic'` sighting with two unauthenticated GETs.

`canarymaze/app.py:93-96` · `canarymaze/export.py:97, 121-134`

`/export.json` is public and unauthenticated, and `_mint_sample` emits the **plaintext secret** of
the most recent mint. It is emitted in every state, not only `awaiting` — `export.py:97` calls it
unconditionally, contradicting its own docstring at `export.py:121-123`.

Reproduced end to end:

```
STEP 1: GET /export.json          -> mint_sample.secret = fda51fe0d27fed4c
                                     mint_sample.ua     = Mozilla/5.0 (compatible; GPTBot/1.2; …)
                                     mint_sample.net    = 20.171.207.0/24
STEP 2: GET /c/fda51fe0d27fed4c/q3-supplier-review   (User-Agent: curl/8.5.0)  -> 200
RESULT: sightings_organic 0 -> 1
        sighting id=1 origin=organic mint_ctx=c67c77ba93db seen_ctx=c278061bcc1d
```

The viewer then publishes, as its headline claim: *"A URL that only context A was ever shown was
requested within the same second by context B, on a different network."*

No salt knowledge, no header forgery, no privileged network position. One `curl` of a public JSON
endpoint, then one `curl` of the URL it hands you.

Second, independent channel for the same attack: `docs/paste_log.json` is **committed to the
public repository** and contains live canary URLs
(`https://respondent-logging-probably-simpsons.trycloudflare.com/c/f9e60863dea8cd0e/q3-supplier-review`).
That secret is in the live `canary.sqlite3` mint table right now.

Blast radius: `sightings_organic` is the single number `docs/RESULTS.md:25` bolds as "the honest
number, not a rounding", and it is remotely writable by any reader of the site or the repo.

### B3 — The live surface returns HTTP 500 and loses the mint under any concurrency.

`canarymaze/ledger.py:70` · `canarymaze/app.py:37-40, 63, 149`

`sqlite3.connect(self.path)` is called with no `check_same_thread=False`. The `Ledger` is created
lazily on the first automated request's worker thread and cached in `app.extensions`, and
`Flask.run()` sets `threaded=True`. Every subsequent request on a different thread raises.

Reproduced against the real server (`CANARY_SALT=… PORT=8123 python3 -m canarymaze.app`), six
concurrent `curl` with `User-Agent: GPTBot/1.2`:

```
500 500 200 500 500 500

sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same
thread. The object was created in thread id 133506184980160 and this is thread id 133506080425664.
  canarymaze/app.py:63  in maze_page
  canarymaze/ledger.py:85 in record_request
```

Sequential requests pass (werkzeug reuses the thread), which is exactly why 89 tests, `make demo`
and `make verify` are all green — every one of them drives `app.test_client()` on a single thread.

Blast radius: on `/c/<secret>/<slug>` the same 500 loses the **sighting itself**, the one event
the project exists to capture, and writes no request row either. Crawler fleets fetch in parallel
by default, so this is the normal case. It is a live candidate root cause for
`sightings_organic = 0`.

Worse, the documented fallback does not exist. `ARCHITECTURE.md:65` and `.prod-build/contract.md`
§7 both promise: *"SQLite locked: retry once, then serve the page **without** minting — never
block a crawler, because a blocked crawler is a lost sighting."*
`grep -rnE "retry|except (sqlite3|Operational|Exception)|check_same_thread|threaded|Lock\("
canarymaze/ scripts/` returns exactly two hits — `detect.py:49` (`IntegrityError`) and
`village_spread.py:77` — neither of them this path. The actual behaviour is the precise failure
the docs call unacceptable.

### B4 — A tampered bundle verifies. Three independent ways.

`canarymaze/bundle.py:47-58, 61-71, 85-124`

**(a) `counts` and `note` are never hashed and never cross-checked against `rows`.**
Run against the shipped `bundles/bundle.json`:

```
A1 counts.sightings_organic 0 -> 4127 : VERIFIES (BAD)
A2 note rewritten                     : VERIFIES (BAD)
```

`python3 -m canarymaze.bundle bundles/bundle.json` prints `PASS  4 rows checked`. Those two fields
are what a reader actually reads: the counter block and the free-text provenance note. An operator
can publish `sightings_organic: 4127` over an empty `sighting` table and the offline verifier
blesses it.

**(b) CVE-2012-2459 second-preimage.** `merkle_root` duplicates the last node on an odd level
(`bundle.py:54-55`), and `verify` recomputes the root over the *presented* leaf list
(`bundle.py:109`), so a leaf list and its trailing-duplicate extension have the same root.
Measured collisions: `n=3→4` (dup last 1), `n=5→6` (dup last 1), `n=6→8` (dup last 2), `n=7→8`
(dup last 1).

Exploited on a 3-row bundle — 1 request, 1 mint, 1 sighting, which is the natural shape of a
single organic sighting:

```
honest   bundle: 3 rows, root 645ff2bebeb9973c, verify=True, sightings=1
tampered bundle: 4 rows, root field STILL 645ff2bebeb9973c, verify=True, problems=[]
                 sightings now presented: 2   (root byte-identical: True)
```

So a published root does not pin the sighting count. Append a copy of the trailing row and a copy
of its leaf, leave `root` untouched, and the bundle verifies with one more sighting than the root
ever attested.

**(c) No referential integrity.** Delete every `mint` row, keep the sighting, re-root honestly:
`verify` returns `(True, [])`. A bundle can assert "secret S moved from context A to context B"
with nothing showing S was ever issued to A — and the sighting's entire meaning rests on that mint
row. `verify` also never checks that `sighting.mint_ctx_id` agrees with the mint row for that
secret, or that `mint_request_id` / `seen_request_id` point at rows that are present.

`tests/test_bundle.py:63-68` adds a row *without* a leaf (caught by the length check) and
`:108-111` changes a leaf (caught by the root). Both do the adjacent easy case; neither does the
duplication. AC-5 says "any byte of any bundled **row**", so (a) is arguably outside its letter —
but it is squarely inside what the README, the viewer and the landing page claim.

### B5 — A fully browser-shaped request is minted for and written to the ledger.

`canarymaze/gate.py:63-68`

Rule 1 (`declares_crawler`) short-circuits before Rule 2 (`has_browser_shape`), so the
user-agent string alone decides. Reproduced with the complete real Chrome 129 header set —
`Accept-Language`, `Sec-Fetch-Mode/Site/Dest/User`, `Sec-Ch-Ua`, `Upgrade-Insecure-Requests`,
the full Chrome `Accept` — with only the UA swapped:

```
is_automated(real chrome)                                       = False
is_automated(chrome + "…compatible; Googlebot/2.1; +http://…")   = True
ledger rows written = 1   mints = 1   human_requests counter = 0
ROW: 81.2.69.0/24 - - [2026-10-02T21:43:39Z] "GET /m/q3-supplier-review HTTP/1.1" 200 872 "-" …
```

This is not hypothetical. Chrome DevTools ships a built-in "Googlebot" network-conditions preset;
every popular User-Agent Switcher extension ships a Googlebot preset; spoofing Googlebot is a
widely circulated paywall bypass. `DECLARED_CRAWLERS` (`gate.py:30-40`) also contains the bare
substrings `"crawler"`, `"spider"`, `"scraper"` and `"bot/"`, so any UA containing them is minted
for regardless of browser shape.

The gate's own docstring states the opposite policy (`gate.py:4-7`): *"a request is treated as
HUMAN unless we have positive reason to think otherwise… Being wrong in the human direction costs
the right to ship this at all. We choose to lose sightings."* Rule 1 inverts that trade: it
chooses to gain a false mint over losing a sighting. The docstring describes only Rule 2.

The claim this falsifies is made unconditionally in three places: `README.md` ("A human is never
minted for and never enters the ledger"), `site/index.html` step 01, and
`.prod-build/contract.md` §2.

Be clear about the scope: **Rule 2 held.** See "What held up" — I could not find a mainstream
browser that Rule 2 misclassifies. The dangerous direction is Rule 1.

### B6 — The claim that the gate holds is checked by a counter that cannot be non-zero.

`canarymaze/ledger.py:76-78, 139` · `canarymaze/app.py:56-59, 80-81`

`record_request(..., is_automated: bool = True, ...)` and **nothing in the repository ever passes
`is_automated=False`**. `grep -rn "is_automated=" canarymaze/ scripts/` returns one hit: the
`COUNT` query itself. On the human branch `app.py` returns before reaching `record_request`.

So `human_requests = COUNT(*) FROM request WHERE is_automated=0` is pinned to 0 by construction,
not by the gate. Deleting the gate entirely would not move it. B5 demonstrates it: a
browser-shaped request lands in the ledger and the counter still reads 0.

It is presented as a falsifiable check in six places:

| Where | Text |
|---|---|
| `scripts/verify.sh:36-44` | one of the five `make verify` properties — "human requests in ledger  0  OK" |
| `scripts/seed_replay.py:95-96` | `raise SystemExit("a human request reached the ledger - the gate is broken")` |
| `README.md` verify table | "human requests in ledger = 0 \| the gate holds; this is not a visitor-tracking tool" |
| `viewer/render.js:101-103` | footer counter |
| `site/index.html` | "the gate holds — without this it would be a visitor-tracking tool" |
| `docs/RESULTS.md:27` | "Human requests in ledger \| 0 \| the gate held" |

`ledger.py:131-132`'s own docstring says the counter "exists so the claim that humans are
excluded is checkable rather than asserted". It makes the claim *unfalsifiable*, which is the
opposite.

**Same defect, same shape: `sightings_paste`** (`ledger.py:138`). `ORIGINS` allows `"paste"` and
`schema.sql:51` permits it, but nothing ever constructs the app with `origin="paste"` — only
`"organic"` (the default) and `"seeded"` (`seed_replay.py:65`). So the paste column on the viewer,
the landing page and RESULTS.md can never be non-zero.

And the consequence is live: `scripts/trigger_paste.py` deliberately lets paste-triggered fetches
land as `origin='organic'` (its docstring, lines 14-19 — defensible reasoning). But that means a
paste-triggered sighting is **counted as organic and labelled "organic traffic"** by
`render.js:117`, which is exactly the presentation `trigger_paste.py:90-92` forbids: *"claiming
otherwise would be the exact overclaim this project exists to avoid."* `trigger_paste.py` was run
three times in the last 30 minutes, so the next fetch of that URL trips this.

---

## MAJOR

### M1 — The top-line claim of the README and the landing page is the overclaim the project exists to avoid.

`README.md:3` · `site/index.html` h1 and `<meta name="description">` · `.prod-build/contract.md` §11

> "**Prove two automated clients shared information**, instead of guessing from how alike they look."
> "Prove two AI clients shared information."

`README.md` Limitation 2, and `site/index.html` in its own limits section, both say:

> "Two clients can touch the same secret without having talked — one may simply have followed the
> other through the same link graph. The bundle records a shared artifact, not intent."

The h1 asserts "shared information"; the same page denies it ~200 lines later. A judge reads the
headline and the limits and finds the contradiction without leaving the page. On a project whose
differentiator is honesty, this is the finding that costs the most and the cheapest one to fix.

Everything *below* the headline is scrupulous — `export.py:25-29` `SCOPE_LINE`, the derived claim
at `export.py:101-118`, ADR-0002. Only the headline overreaches.

### M2 — "No trust in us" is false: nothing anchors the root.

`site/index.html` step 03 ("No server, no network, no trust in us") · `ARCHITECTURE.md:56`
("no trust in the operator") · `bundle.py:4-6` · `tests/test_bundle.py:1-2`

The operator computes the rows, the leaves and the root, and the root is only ever read back out
of the same file. I fabricated an `origin='organic'` sighting, recomputed leaves and root
honestly, and `verify` returned `(True, [])`.

The bundle detects edits made *after* a reader independently recorded the root. Nothing in the
repository publishes, signs, timestamps or notarizes one — no root string appears in `README.md`,
`docs/RESULTS.md` or any committed doc. The three roots I found all differ: `a795…b3` (live
`site/viewer/data.js`), `fd33…47` (`viewer/data.js`), `6c96bc…` (`bundles/bundle.json`), and
`make demo` produced a fourth.

The honest wording is available and strong on its own: *"the bundle is internally consistent and
has not been edited since it was built."* Pinning one root in the README or RESULTS.md would make
the stronger claim true for about two minutes of work.

### M3 — The live "Live evidence" page displays a root for a bundle that exists nowhere.

`site/viewer/data.js` (committed; root `a795…b3`) vs `viewer/data.js` (`fd33…47`) vs
`bundles/bundle.json` (`6c96bc…`)

The live page invites a reader to check a root whose bundle they cannot obtain: `bundles/` is
gitignored and the live site serves no `bundle.json`.

`.gitignore:11-12` states the policy — *"build outputs: regenerated by `make demo`, so never
committed. A committed copy would be a stale snapshot of a ledger that has since moved on."*
`site/viewer/data.js` is committed anyway and is exactly that stale snapshot.

### M4 — The honesty counters disagree across every surface, and none matches the live ledger.

| Surface | Mints |
|---|---|
| `site/index.html` "What is real here" table | **1** |
| `docs/RESULTS.md:23` | **2** |
| `viewer/data.js`, `bundles/bundle.json` | **1** |
| live `canary.sqlite3` (read read-only, now) | **3** |

Test count: `README.md:168` "85 tests" · `.prod-build/state.md:16` "88 tests green" ·
`site/index.html` "89". `python3 -m pytest -q` → **89 passed**. A judge falsifies the README in
one command.

Both documents are dated today and both claim ledger provenance — `site/index.html`: "Every number
below comes from the ledger, not from a slide."

### M5 — The production ledger contains no third-party traffic, and no surface says so.

Read `canary.sqlite3` read-only: **5 requests, 3 mints, 0 sightings**. Every user-agent is the
builder's own:

```
1 × 127.0.0.0/24      Mozilla/5.0 … compatible; GPTBot/1.2 …     (a local curl)
2 × 103.81.39.0/24    canary-maze-paste-trigger/1.0
2 × 103.81.39.0/24    curl/8.5.0
```

`docs/RESULTS.md:23` presents this as "Mints | 2 | secrets issued to automated contexts" and
`site/index.html` as "Mints | 1 | secrets issued to an automated context". Both read as "automated
clients we observed"; all of them are self-generated. RESULTS.md is otherwise commendably blunt
about `organic sightings = 0` — this one row undercuts the rest of it.

A judge also cannot reproduce any of these numbers: `canary.sqlite3` is gitignored and the tunnel
hostname is ephemeral (`RESULTS.md:11-17`).

### M6 — `_mint_sample` publishes a live canary secret into every export, including the Vercel viewer.

`canarymaze/export.py:97, 121-134` · `scripts/export_all.py:55-57`

`mint_sample.secret` ships in `/export.json`, `viewer/data.json`, `viewer/data.js`, and the
committed-and-deployed `site/viewer/data.js` (`"secret": "369bf1645c560f02"`). The docstring says
it is "Shown only in the awaiting state" — that describes the viewer, not the payload.

For the seeded demo the secret is inert. Run `export_all.py --db canary.sqlite3` once — which
RESULTS.md effectively invites — and the live production canary is published to the open web and
committed to git. This is the delivery mechanism for B2.

### M7 — `make verify`'s two strongest-sounding checks are near-tautologies.

`scripts/verify.sh:36-44` and `:65-83`

Check 2 ("human requests in ledger") cannot fail — see B6.

Check 5 ("proof graph with the model enabled vs off byte-identical") inserts a row into
`laundered` and rebuilds. `bundle.build` reads only `PROOF_TABLES`, and `Ledger.rows()`
(`ledger.py:126-127`) raises `ValueError` on anything else. It can only fail if someone edits that
allowlist. That is a legitimate regression guard — but the copy claims much more, because **there
is no model integration at all**. `grep -rni "laundered|paraphras|semantic" canarymaze/ scripts/`
finds the table DDL, the bundle comment and the verify.sh `INSERT`, and nothing else. There is
nothing to enable or disable.

`README.md:106` ("shipped disabled"), `ARCHITECTURE.md:54` ("ships **disabled** in a separate
table"), and the demo script's t=1:10 beat ("Disable the model, re-run, diff the proof graph:
byte-identical") all describe a feature that was never written. If a judge asks "show me the model
path you disabled", there is nothing to show.

The true claim is good and provable: *the bundle writer cannot read any table but three, enforced
in two places, with two tests.* Say that instead. (The property itself holds — see "What held up".)

### M8 — Causally impossible sightings are recorded, and a test locks the behaviour in.

`canarymaze/detect.py:42` · `tests/test_detect.py:174-178` · `canarymaze/bundle.py:118-122`

`delta = max(0.0, (seen_ts - mint_ts).total_seconds())` silently clamps. Reproduced: mint at
`11:30:00Z`, canary fetch at `11:00:00Z` — thirty minutes *earlier* — writes
`sighting id=1 delta_s=0.0 ts=2026-10-02T11:00:00Z`. `export.human_delta(0.0)` then yields
"within the same second", so the published claim reads *"requested **within the same second** by
context B"* for a fetch that preceded the issue by half an hour.

The detector never requires the sighting to post-date the mint, and `bundle.verify`'s only
semantic check is `mint_ctx_id != seen_ctx_id`; it never checks `sighting.ts >= mint.ts`.

`test_a_clock_skewed_backwards_does_not_produce_negative_elapsed_time` asserts `delta_s == 0.0`
for exactly this input. It pins the clamp and never asks whether the pair should be a sighting at
all.

In-product likelihood is low (one process, one clock; an NTP step-back would do it). It matters
because the bundle can carry an internally impossible row that the offline verifier passes.

Related, unhandled: `detect._parse` (`detect.py:19-20`) uses `strptime("%Y-%m-%dT%H:%M:%SZ")` with
no guard. A mint `ts` of `2026-10-02T11:04:12.500Z` raises `ValueError` out of the canary route →
HTTP 500 → the sighting is lost. `now_iso()` can't produce that today, so this is latent
fragility, not a live bug.

### M9 — One client manufactures two contexts by changing one header.

`canarymaze/context.py:36-39, 42-52` · `canarymaze/app.py:17-24`

**(a) `X-Forwarded-For`.** `client_ip` takes the left-most hop. Reproduced with the real peer
fixed at `198.51.100.77` both times:

```
GET /m/q3-supplier-review   X-Forwarded-For: 20.171.207.14
GET /c/<secret>/q3-…        X-Forwarded-For: 104.28.52.9
-> sightings_organic = 1   mint_ctx=c342b46aa05c  seen_ctx=fc24fb5e9c9d
-> request id=1 ip_net=20.171.207.0/24   (real peer was 198.51.100.77)
-> request id=2 ip_net=104.28.52.0/24    (real peer was 198.51.100.77)
```

The real peer appears nowhere in the record. The viewer's diff table then reports
"network — differs" and the claim appends ", on a different network", entirely from
attacker-supplied strings.

Deployment relevance: the shipped launcher (`scripts/serve_public.sh:53`) puts the surface behind
a Cloudflare quick tunnel. Cloudflare **appends** the real client address to `X-Forwarded-For`
rather than replacing it, so the left-most hop stays attacker-controlled. The comment at
`app.py:18-20` acknowledges the trust assumption and concludes the deploy is safe; it is not, for
that reason.

**(b) No XFF needed.** Same peer, same /24, identical headers plus `X-Trace: 1` → a different
`header_order_fingerprint` → a different ctx_id → a sighting. Any client that varies its header
set between two fetches (connection reuse vs. a new connection, a retry that adds a trace header,
an SDK that adds `Accept-Charset` on retry) manufactures one.

Zero tests touch this: `grep -rn "X-Forwarded\|client_ip" tests/` → nothing.
`tests/test_context.py:142-146` asserts header-order sensitivity as a *feature*. No test asserts
the property that matters — that one client cannot cheaply become two.

### M10 — Unhandled `IntegrityError` on the mint path: a crawler's parallel fetch gets a 500.

`canarymaze/app.py:66-68`

```python
if ledger().mint_for_secret(secret) is None:
    ledger().record_mint(secret=secret, ...)
```

Read-then-write, no transaction, no `except`. Two handlers for the same context and path both read
`None`, both insert, and the second raises `sqlite3.IntegrityError: UNIQUE constraint failed:
mint.secret` → HTTP 500. I reproduced the interleaving directly.

AC-2 holds sequentially and fails concurrently. AC-2's named verifier is
`pytest tests/test_mint.py -q`, and `tests/test_mint.py` never opens a ledger — it is nine
pure-function tests. **No test anywhere requests `/m/<slug>` twice from one context**
(`grep -n 'get("/m/' tests/*.py` shows four single requests in four different tests). AC-2's
"exactly one mint row" clause is unverified.

---

## MINOR

- **Opening `viewer/index.html` makes two third-party network requests.** `viewer/index.html:8-10`
  preconnects and loads Google Fonts. `scripts/demo.sh:2` says "One command, no network, no
  server"; the README Quickstart is headed "3 commands, no network"; `render.js:11-13` says "works
  from file:// with no server and no network"; `contract.md` §5 says "offline is the normal case".
  The *verifier* is genuinely offline (`tests/test_bundle.py:33-44` monkeypatches `socket`), but
  the page `make demo` tells you to open is not. Falsifiable with devtools open.
- **`scripts/verify.sh` accepts no arguments.** AC-7's named verification is
  `scripts/verify.sh --compare-model-off`; the script parses nothing, so the documented command
  silently runs the default path.
- **`.prod-build/contract.md` §5 contradicts the shipped behaviour and the README.** The J2 error
  state reads "unknown secret → **404**, logged, no row", while the code, the README and
  `tests/test_app.py:57-63` all require 200 ("a 404 would tell the client the URL was a trap").
  The contract is tracked in git, so a judge can read the contradiction.
- **`require_production_salt` is only called from `__main__`** (`canarymaze/app.py:146-148`). Any
  WSGI entry (`gunicorn 'canarymaze.app:create_app()'`, `flask --app canarymaze.app run`) imports
  `create_app` and never runs the guard; `CANARY_ALLOW_DEV_SALT=1` also bypasses it and the error
  text advertises that. The documented launcher (`serve_public.sh:29-36`) does the right thing and
  `tests/test_app.py:98-111` tests the function — but not that any entry point calls it. Low
  likelihood, catastrophic if hit (`docs/memory/failures/F-0001` is the record of exactly this
  class), so it deserves a line in the deploy notes.
- **The catch-all serves everything in `viewer/`** (`canarymaze/app.py:116-120`).
  `GET /.vercel/project.json` on the canary surface returns 200 with
  `{"projectId":"prj_IqNlPdMKyKXmL4pEqRH0YwFriP1H","orgId":"team_hMixP48HIAtFDhe0NFr4gmeT"}`. Not
  secret, but it should not be on the public surface, and anything dropped into `viewer/` later is
  published automatically. **No traversal:** I tried `../README.md`, `..%2f`, `%2e%2e%2f`,
  `....//`, `..%252f`, `..%5c`, `/etc/passwd` — all 404. `send_from_directory`'s `safe_join` holds.
- **Werkzeug's access log writes full peer addresses to `.serve.log`.** `serve_public.sh:44`
  redirects the dev server's stderr there. Behind the tunnel the peer is `127.0.0.1`, but
  `app.py:149` binds `0.0.0.0`, so a direct run logs real addresses. "A full address is never
  stored" is true of the *ledger* and well tested; it is not true of the process's own log.
  `.serve.log` is gitignored.
- **Flask's development server is the production server** (`canarymaze/app.py:149`). Werkzeug
  prints its own "do not use in a production deployment" warning into `.serve.log` on every start.
- **`trigger_paste.py --report` under-counts pastes.** `scripts/trigger_paste.py:103`
  `published = {e["secret"]: e for e in entries}` keys by secret, so the three entries now in
  `docs/paste_log.json` (one secret, two hostnames) collapse to one and `published by paste : 1`
  is printed for three pastes.
- **ctx_id collides for distinct hosts in one /24.** `derive(h, "203.0.113.10")` ==
  `derive(h, "203.0.113.200")` == `8b18a8cd2f17`. Two separate machines behind one cloud NAT
  running the same client library are one context, so a genuine cross-client share inside a /24 is
  invisible. This is the **safe** direction (a missed sighting, not a false one), and
  `tests/test_context.py:127-130` deliberately wants the /24 collapse — but README assumption A-2
  documents only *stability*, not collision. One sentence would cover it.
- **`has_browser_shape` keys on truthiness** (`gate.py:60`, `h.get(name)`), so a header present
  with an empty value reads as absent. I could not produce a real browser that sends an empty
  `Accept-Language`, so this is a latent sharp edge rather than a finding.
- **`scripts/seed_replay.py:63`** — `def run(db_path: str) -> int` returns `counts`, a dict.

---

## NITS / delete before submission

- **`idea_gate.py`** — 1002 lines, 68K, tracked, at the repository root, referenced by nothing but
  its own usage string. Delete.
- **`graphify-out/`** — 3.3M of a 5.4M repository, 57 tracked files, most of them opaque
  `cache/ast/` and `cache/semantic/` hash-named JSON blobs. `.gitignore:21` ignores
  `graphify-out/.graphify_*` and `cost.json` but not `cache/`. The README never mentions the
  directory. Add `graphify-out/cache/` to `.gitignore`, or drop the directory.
- **`UI-SPEC.md`** — tracked, 14K, still names the deleted `ui-prototype/` (line 11) and specifies
  verification behaviour the product does not have: line 93 `Verify idle: "Verify bundle" ·
  running: "Verifying… 3/12"`, and line 17 "the claim survives without trusting the operator". A
  judge reading it sees a spec the build did not meet.
- **`.prod-build/`** — 6 tracked files including `pb.py` (90K) and the contract that contradicts
  the shipped 200/404 behaviour. Shipping the build harness is defensible; shipping a contract that
  disagrees with the code is not.
- **`prod-idea/ledger.jsonl`** — tracked, referenced by nothing in the README.
- **Two Vercel projects** (`site/.vercel`, `viewer/.vercel`). The `viewer` project deploys a
  directory whose `data.js` is gitignored, so that deployment renders "No data loaded. Run `make
  demo` to build the viewer." Only `site` is linked from the README. Delete the stale project.
- **`ui-prototype/`** — already deleted at HEAD (`8027232`); the question in the brief is settled.
  Three stale references remain: `.prod-build/contract.md:3` ("Upstream read: … ,
  `ui-prototype/index.html`" — now a file that does not exist), `docs/memory/INDEX.md:14`, and
  `docs/memory/feedback/U-0001…md:7`. The U-0001 ones are historical records and are fine to leave;
  the contract's line is not. `UI-SPEC.md:11` already explains the deletion. Nothing executable
  references it.
- **`tests/test_viewer_data.py:22-24` is a no-op assertion.**
  `assert f'{el} hidden' in HTML or f'{el}' in HTML and "hidden" in HTML` parses as
  `A or (B and C)`; `B` and `C` are both true for any page containing the id and the word "hidden"
  anywhere, so it passes regardless of whether the region starts hidden.
- **`tests/test_viewer_data.py:49-50`** asserts `HTML.count('tabindex="0" role="region"') == 2` —
  a brittle string count that breaks on attribute reordering.

---

## Test quality

89 tests, 1.81s, all passing. Most are real behavioural tests; three are not, and the gaps cluster
exactly where the blocking findings are.

**Strongest file: `tests/test_export.py`.** Genuine behavioural tests of derived copy — the network
clause appears only when the two /24s actually differ (`:122-131`), a sub-second gap reads "within
the same second" rather than "0s later" (`:133-136`), the awaiting state never names a second
context (`:23-35`), and `:93-120` drives `seed_replay.py` as a subprocess end to end. These would
catch the U-0001 regressions they were written for.

**Also solid:** `tests/test_ledger.py:65-83` (checks the dropped octet is absent from `ip_net`
*and* from `raw_line` — the right assertion), `:94-100` (exercises both append-only triggers),
`tests/test_bundle.py:71-80` (recomputes leaves *and* root before asserting, so only the semantic
check can catch it — a real test), `tests/test_bundle.py:33-44` (monkeypatches `socket` so network
use fails loudly).

**Tautological / asserting on their own fixtures:**

| Test | Problem |
|---|---|
| `test_viewer_data.py:44-47` `test_verification_copy_names_what_it_does` | Asserts the strings "makes no request to our server" and "Recompute the hashes locally" are present **in the HTML**. It checks that the page contains the copy; it never checks the code does what the copy says. The copy is false (B1). This is the test that let B1 ship. No test anywhere asserts that `render.js` hashes anything. |
| `test_viewer_data.py:22-24` | Operator-precedence no-op; see NITS. Cannot fail. |
| every `assert c["human_requests"] == 0` (`test_app.py:72`, `test_export.py:…`, `test_ledger.py:111`) | Asserts a value that is structurally pinned to 0 (B6). Reads as gate coverage; is not. |

**Tests that lock in wrong behaviour:**

- `test_detect.py:174-178` asserts `delta_s == 0.0` for a canary fetch 4m12s *before* the mint —
  pins the clamp, never questions whether the pair is a sighting (M8).
- `test_context.py:142-146` asserts header-order sensitivity as a feature; that is the mechanism of
  M9(b), and nothing tests the converse.

**Missing coverage, each mapping to a finding above:** no test for `X-Forwarded-For` or `client_ip`
(M9a); no test requesting `/m/<slug>` twice from one context (M10, AC-2); no concurrency test at
all (B3, M10); no test that a browser-shaped request with a crawler UA is rejected (B5); no bundle
test for `counts`/`note` tampering, leaf duplication, or missing-mint referential integrity (B4);
no test that any viewer code computes a hash (B1).

---

## Requirements completeness — AC-1..AC-9

| AC | Verdict | Evidence |
|---|---|---|
| **AC-1** browser headers → no mint, no row | **Partially satisfied** | `tests/test_gate.py` covers Accept-Language-only and Sec-Fetch-only browsers; `test_app.py:66-73` checks no row. But AC-1's literal condition is **violated** when the UA matches `DECLARED_CRAWLERS` (B5), and no test covers that input. The "no row" half is additionally guarded by a counter that cannot fail (B6). |
| **AC-2** same ctx + path twice → same secret, exactly one mint row | **Not satisfied as named** | Named verifier `tests/test_mint.py` never opens a ledger — nine pure-function tests. No test requests `/m/<slug>` twice from one context anywhere. Concurrently it fails with a 500 (M10). |
| **AC-3** own mint context → 200, no sighting | **Satisfied** | `test_detect.py:137-142`, `test_app.py:47-54`. Verified by hand too. |
| **AC-4** different context → 200, exactly one sighting, both raw rows | **Satisfied for the happy path** | `test_detect.py:129-134, 151-156`, `test_app.py:30-44`. "Exactly one" is real — `UNIQUE(secret, seen_ctx_id)` plus the `IntegrityError` catch at `detect.py:49-51`. But nothing tests that the sighting is *earned*: B2 shows the "different context" can be anyone who read `/export.json`. |
| **AC-5** any altered byte → fail, naming the row | **Broken** | Row-field tampering is caught and named (`test_bundle.py:47-52`, `verify.sh:52-63`). Three other tamperings verify clean: `counts`/`note`, trailing-leaf duplication, missing mint rows (B4). |
| **AC-6** verifier makes no network call, needs no server | **Satisfied for the Python verifier** | `test_bundle.py:33-44` monkeypatches `socket`; `make verify` passes with no server; I ran it. The viewer — which is what the product shows a judge — verifies nothing (B1) and loads remote fonts (MINOR). |
| **AC-7** model disabled → byte-identical proof graph | **Flag does not exist** | `scripts/verify.sh --compare-model-off` is unparsed. The underlying property holds but is near-tautological, and there is no model to disable (M7). |
| **AC-8** viewer shows organic/seeded separately plus the human count | **Satisfied in form** | `render.js:97-103` renders all four; `test_export.py:80-85` asserts the separation in the payload. Two of the four counters cannot be non-zero (B6), and a paste-triggered sighting will be labelled "organic traffic" by `render.js:117`. AC-8's named verification ("assert on `viewer/data.json`") is not what any test does. |
| **AC-9** `make demo` on a clean checkout, no network → viewer + PASS | **Satisfied for the CLI** | Ran it: PASS, 4 rows, state `sighting`. "No network" is false for the page `make demo` tells you to open (MINOR). |

---

## What held up under attack

Stated plainly, because it is useful signal.

1. **Claim 5 — the canary route 200s for every context. HOLDS.** Verified for a known secret, an
   unknown secret (`deadbeefdeadbeef`), a garbage secret with a garbage slug, and a human-shaped
   request: all 200. `app.py:78` falls back to `maze.slugs()[0]` for an unknown slug rather than
   404ing. The only 404s are URL shapes a minted link cannot produce (`/c//<slug>`, or a secret
   containing an encoded `/`, which werkzeug rejects before routing).
2. **Claim 3 — the `laundered` table cannot reach the bundle. HOLDS.** Two independent guards:
   `bundle.PROOF_TABLES` (`bundle.py:31`) and `Ledger.rows()` raising `ValueError` on any other
   table (`ledger.py:126-127`), plus `test_bundle.py:83-90` and `test_ledger.py:115-117`. I
   inserted into `laundered` and rebuilt: the row does not appear and the string "paraphrase" is
   not in the serialized bundle. Only the *framing* overclaims (M7).
3. **The false "bounded by HMAC collision" claim is gone and cannot return silently.** It survives
   only as an explicit negation in three places — `README.md:56`, `canarymaze/mint.py:13-15`, and
   `docs/memory/decisions/ADR-0002` ("Never reintroduce it"). Grepping `collision` across code,
   docs, HTML and SQL finds nothing else. This was done properly.
4. **Gate Rule 2 held.** I could not construct a mainstream browser request that `is_automated`
   calls automated. Tried: the full Chrome 129 set; Firefox with `intl.accept_languages` cleared
   (still sends `Sec-Fetch-*`); Safari before 16.4 (no `Sec-Fetch-*`, but sends `Accept-Language`);
   `privacy.resistFingerprinting` (normalizes rather than drops `Accept-Language`); Tor Browser
   defaults; header-name case variations (`test_gate.py:77-79` covers this); subresource and
   no-cors shapes. Every one keeps at least one of `Accept-Language` / `Sec-Fetch-*` / `Sec-CH-UA`.
   The converse also held: `python-requests`, `curl` and an empty header set all classify
   automated. The dangerous direction is Rule 1 (B5), not Rule 2.
5. **Claim 6 — addresses are truncated to /24 before storage. HOLDS for the ledger.**
   `ledger.py:25-38, 83` — `truncate_ip` runs inside `record_request`, the full address is never
   passed deeper, and `combined_log_line` is built from the already-truncated value. v4→/24,
   v6→/48, unparseable→`unknown`. I found no ledger path that stores a full address. (The process
   access log is a separate matter, MINOR.)
6. **Append-only is enforced, not conventional.** `schema.sql:68-79` has `BEFORE UPDATE` /
   `BEFORE DELETE` `RAISE(ABORT)` triggers on all three proof tables; `test_ledger.py:94-100`
   exercises both.
7. **There is genuinely no actor entity.** No `actor` table, no join producing one, and the "A"/"B"
   labels come from a display-only, never-persisted function (`context.py:55-71`).
   `test_export.py:66-79` asserts the claim text never concludes "actor" or "operator".
8. **No path traversal** in the catch-all route — seven encodings tried, all 404.
9. **The arXiv citation checks out.** `arXiv:2605.13706` is real: "Identifying AI Web Scrapers
   Using Canary Tokens", Seiden / Ren / Zhang / Kim / Liu / Wenger, v1 2026-05-13, v2 2026-09-03,
   and the README's central verbatim quote ("We host dynamic websites that serve unique canary
   tokens to each visiting scraper") appears in the abstract. The footer's METR link also resolves
   to a real document. I could not independently confirm the three body quotes (the "mapping
   between scrapers", "arbitrarily complex fingerprinting", "22 production model systems"), since
   only the abstract page was reachable — worth a 30-second self-check before submission.
10. **The detector's negative cases are right.** Unissued secret → `None`; same context → `None`;
    missing request row → `None` (`detect.py:33-40`, tested at `test_detect.py:145-148, 137-142,
    181-184`). The UNIQUE-constraint double-submit guard is correctly caught, not swallowed
    blindly.

---

## Suggested order of work, given ~43 hours

If only three things get fixed, these three:

1. **B1** — change the viewer and landing-page copy, or ship `bundle.json` and 15 lines of
   `crypto.subtle.digest`. Right now the product's central moment is false on its own face. The
   copy fix is ten minutes.
2. **B3** — `sqlite3.connect(self.path, check_same_thread=False)` plus a `threading.Lock` around
   the writes, or `threaded=False`, plus the `try/except` the architecture doc already promises.
   Without this the live surface loses most of its traffic, and organic sightings cannot happen.
3. **B2** — drop `secret` from `_mint_sample`, or gate `/export.json`. One field. Otherwise
   `sightings_organic` is writable by anyone who reads the site.

Then **B6** (make `human_requests` actually record human requests — pass `is_automated=False` and
write the row, or delete the counter and the five claims that cite it), **B4(a)** (hash `counts`
and `note`, or remove them), **M1** (the headline), **M4** (make the three counter surfaces agree),
and the cleanup list.

B5 and B4(b)/(c) are genuine but need design decisions rather than one-liners; if they cannot be
fixed, say so in the Limitations section — this project has earned the right to be believed when
it names its own limits, and spending that credit on a headline it contradicts two screens later
is the worst trade available.
