window.CANARY_DATA = {
 "state": "sighting",
 "scope_line": "A sighting establishes that the secret moved between two request contexts. It does not establish that they are two different operators - one operator can rotate addresses. In the AI Village dump, one actor label spans 741 of them.",
 "claim": "A URL that only context A was ever shown was requested within the same second by context B, on a different network.",
 "counts": {
  "mints": 1,
  "sightings_organic": 0,
  "sightings_seeded": 1,
  "sightings_paste": 0,
  "sightings_selftest": 0,
  "human_requests": 0,
  "humans_turned_away": 1,
  "requests": 2,
  "requests_direct": 2,
  "requests_reported": 0
 },
 "sightings": [
  {
   "secret": "6edafebf1e484d7e",
   "origin": "seeded",
   "elapsed": "within the same second",
   "elapsed_s": 0.0,
   "issued": {
    "label": "A",
    "ctx_id": "c0e7aead548d",
    "at": "15:21:26",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "net": "20.171.207.0/24",
    "raw": "20.171.207.0/24 - - [2026-10-03T15:21:26Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\""
   },
   "requested": {
    "label": "B",
    "ctx_id": "58a7736b46e0",
    "at": "15:21:26",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "net": "104.28.52.0/24",
    "raw": "104.28.52.0/24 - - [2026-10-03T15:21:26Z] \"GET /c/6edafebf1e484d7e/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\""
   }
  }
 ],
 "mint_sample": null
};
window.CANARY_BUNDLE = {
 "format": "canary-maze-bundle/3",
 "note": "",
 "counts": {
  "mints": 1,
  "sightings_organic": 0,
  "sightings_seeded": 1,
  "sightings_paste": 0,
  "sightings_selftest": 0,
  "human_requests": 0,
  "humans_turned_away": 1,
  "requests": 2,
  "requests_direct": 2,
  "requests_reported": 0
 },
 "rows": {
  "request": [
   {
    "id": 1,
    "ts": "2026-10-03T15:21:26Z",
    "method": "GET",
    "path": "/m/q3-supplier-review",
    "status": 200,
    "ip_net": "20.171.207.0/24",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "ctx_id": "c0e7aead548d",
    "raw_line": "20.171.207.0/24 - - [2026-10-03T15:21:26Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\"",
    "origin": "seeded",
    "via": "direct",
    "is_automated": 1
   },
   {
    "id": 2,
    "ts": "2026-10-03T15:21:26Z",
    "method": "GET",
    "path": "/c/6edafebf1e484d7e/q3-supplier-review",
    "status": 200,
    "ip_net": "104.28.52.0/24",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "ctx_id": "58a7736b46e0",
    "raw_line": "104.28.52.0/24 - - [2026-10-03T15:21:26Z] \"GET /c/6edafebf1e484d7e/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\"",
    "origin": "seeded",
    "via": "direct",
    "is_automated": 1
   }
  ],
  "mint": [
   {
    "id": 1,
    "secret": "6edafebf1e484d7e",
    "ctx_id": "c0e7aead548d",
    "path": "/m/q3-supplier-review",
    "salt_epoch": "2026-10-03",
    "ts": "2026-10-03T15:21:26Z",
    "request_id": 1
   }
  ],
  "sighting": [
   {
    "id": 1,
    "secret": "6edafebf1e484d7e",
    "mint_ctx_id": "c0e7aead548d",
    "seen_ctx_id": "58a7736b46e0",
    "mint_request_id": 1,
    "seen_request_id": 2,
    "delta_s": 0.0,
    "origin": "seeded",
    "ts": "2026-10-03T15:21:26Z"
   }
  ]
 },
 "leaves": [
  "106f1d12a40b90a40698c8743c753851833dbe6b0c93e9504b32e2bb15583f56",
  "9d9f46eadcaaf789c7e67deb8bebc593de9ef7a28a31bb6fff4e8f08925bb0f0",
  "e9202f84922411f88f88a6418a2f3c51e0c4e04bc8c669876002d840fa1bde9c",
  "8efa385e6be77da3f9a7e4164fa7df0a1afa3b9833c2a7c8889bab6062f6fcf5",
  "c446e368c13fb9febdd521abeba5169f35d1d752fc1c4916fd7ff47489832a16"
 ],
 "root": "6572e1b6194afa7729a58773c7e6a84d3c4e27a08f25a328a100520a0ffe2848"
};
