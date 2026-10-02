# Results

Status as of 2026-10-02T21:28Z. **Numbers are reported exactly as they stand.**

## Live surfaces

| What | Where |
|---|---|
| Landing page | https://site-nine-hazel-35.vercel.app |
| Live evidence viewer | https://site-nine-hazel-35.vercel.app/viewer/ |
| Canary surface | ephemeral per run: `bash scripts/serve_public.sh` prints the hostname |

The canary surface runs through a Cloudflare quick tunnel from the builder's own
machine, so its hostname changes each run and it is only reachable while that
process is up. See `docs/memory/decisions/ADR-0005` for why that trade was taken:
it keeps the ledger on one machine, so the bundle a judge verifies offline is
byte-identical to the one that collected the evidence.

## Counts

| Category | Count | What it means |
|---|---|---|
| Mints | 2 | secrets issued to automated contexts |
| Seeded sightings | 1 | two clients we control, driven through the real gate, mint and detector |
| **Organic sightings** | **0** | **no uncontrolled client has yet fetched a secret issued to another context** |
| Paste-triggered | 0 | none confirmed yet |
| Human requests in ledger | 0 | the gate held |

## The honest reading

**No organic sighting has been observed.** The seeded replay proves the mechanism
end to end through the real code path; it does not prove that automated clients in
the wild share URLs with each other. Those are different claims and this project
will not merge them.

For scale: the closest published experiment (arXiv:2605.13706) waited **two months**
for its tokens to surface. A 31-hour window is not evidence of absence.

## Pending

A canary URL has been minted and is awaiting a paste into a public model product:

```
python3 scripts/trigger_paste.py <public-url>     # mint and print
python3 scripts/trigger_paste.py --report         # what came back
```

A paste-triggered fetch shows **a fetcher following a human's paste**. It is not
two agents sharing information with each other, and it is counted in its own
column for exactly that reason.
