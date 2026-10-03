# Demo video — shooting script

**Target: 2:00.** One take, terminal + browser, no edit required. The submission
is read by research staff over about a week, so the write-up carries the entry;
this exists to make the offline verification *visible*, which is the one thing
prose cannot do.

Record at 1920×1080, terminal font ≥16pt. Do not speed anything up. If you narrate,
say the words in the right column — they are shorter than they look out loud.

---

### 0:00 — 0:15 · The claim, before any code

**Screen:** `https://site-nine-hazel-35.vercel.app/viewer/`, already loaded.

> "If an automated client reads your site and hands what it found to another one,
> you can usually only say they *look* similar. This is a record that one specific
> secret moved between two of them."

Point at the claim sentence and the two marked records. Do not scroll yet.

---

### 0:15 — 0:40 · The two records

**Screen:** same page. Scroll to the context diff table, then the record pair.

> "A secret was issued to context A. Four minutes later, context B asked for it —
> different user-agent, different network. The same run of characters is marked in
> both raw log lines."

Let the marked secret sit on screen for three full seconds. It is the product moment.

---

### 0:40 — 1:10 · Stop the server. This is the wow moment.

**Screen:** terminal, split or full.

```
# kill the surface outright
pkill -f canarymaze.app ; echo "server down"
make verify
```

> "Now the server is off. Nothing is running."

Let `make verify` print all five lines and **PASS**. Read one aloud:

> "An edited row is caught and named. Five properties, each able to fail, with
> nothing to contact."

---

### 1:10 — 1:35 · Break it on camera

**Screen:** editor, then browser.

```
# change one character in a record
sed -i 's/Supplier/Supplyer/' viewer/data.js
```

Reload `viewer/index.html` **from disk** (`file://`), press **Recompute the hashes
locally**, with the browser network panel open.

> "Every hash is recomputed in the page with crypto.subtle. The network panel is
> empty — nothing was contacted. And it names the row that no longer matches."

The empty network panel is the shot. Hold it.

---

### 1:35 — 1:50 · The unhappy truth

**Screen:** `docs/RESULTS.md`, the two measurement tables.

> "A sighting is not two actors. We measured that on the organizers' own corpus:
> across seventy-eight thousand sessions, forty-six of forty-six agents present
> more than one context, and the busiest presents seven and a half thousand.
> So the tool says 'context', never 'actor'."

---

### 1:50 — 2:00 · The counters

**Screen:** back to the viewer footer.

> "Organic sightings: zero, reported as-is. Humans in the ledger: zero, by
> construction. And five of ten crawlers never reached us at all — the CDN refused
> them. That's in the write-up too."

End on the footer. No outro card.

---

## If a shot fails

- The viewer needs no server: open `viewer/index.html` directly, always.
- To restore the edited record: `python3 scripts/export_all.py --db demo.sqlite3`
- To rebuild everything from nothing: `make clean && make demo`

## What not to show

- **Never demo the maze pages.** They are plumbing, the neighbourhood is crowded
  with crawler tarpits, and showing them invites exactly the wrong comparison.
- Never speed up footage while implying real time.
- Do not claim an organic sighting. There are none, and the counter says so.
