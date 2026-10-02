---
id: F-0003
type: failure
title: The viewer's verification button computed nothing while claiming it did
status: active
scope: global-candidate
components: viewer/render.js, viewer/verify.js, scripts/export_all.py
triggers: writing viewer copy, shipping a verification UI, claiming a client-side check
evidence: viewer/verify.js
verified_at: 2026-10-02@f1a049b
relates: 
supersedes: 
helpful: 0
harmful: 0
cite_hash: c2f81f5fbbaa48e5
created: 2026-10-02
source: unknown
---

ATTEMPTED: ship the product's single differentiating moment - 'recomputes every hash here, in your browser, from the bundle file alone' - by having export_all.py precompute {ok, rows, root} in Python and having render.js print that boolean. ERROR SIGNATURE: none; it printed 'Verified. The server was not contacted.' in every case. A fresh reviewer found it with one grep: no occurrence of crypto, sha256, digest or subtle anywhere in viewer/. ROOT CAUSE: the page was never given the rows or the leaves, so it could not verify even in principle; editing a record in data.js left the page still saying Verified, and deleting the bundle entirely did too. The Python verifier was real throughout - only the on-screen moment was theatre, which is the worst place for it in a product whose whole wedge is 'check this without trusting us'. FIX: ship the bundle itself to the browser and recompute every hash with crypto.subtle in viewer/verify.js. Required making the canonical form portable: json.dumps(275.0) is '275.0' in Python and JSON.stringify(275.0) is '275' in JS, so every value is normalised to a tagged string with floats at six decimals. Verified in a real browser: byte-identical canonical forms, identical leaf hashes, and five tamperings (forged record, forged log line, inflated counts, CVE-2012-2459 duplication, deleted mint rows) all caught on the deployed page. LESSON: a test that asserts a CLAIM STRING is present in the HTML does not test that the code does the thing. tests/test_viewer_data.py asserted 'makes no request to our server' appeared in the markup and passed for a page that verified nothing. When the UI makes a technical claim, test the behaviour, not the sentence. CHEAPEST EARLY CHECK: grep the client bundle for the primitive the copy claims to use.