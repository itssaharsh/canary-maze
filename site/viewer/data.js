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
  "requests": 2
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
    "at": "14:13:20",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "net": "20.171.207.0/24",
    "raw": "20.171.207.0/24 - - [2026-10-03T14:13:20Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\""
   },
   "requested": {
    "label": "B",
    "ctx_id": "58a7736b46e0",
    "at": "14:13:20",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "net": "104.28.52.0/24",
    "raw": "104.28.52.0/24 - - [2026-10-03T14:13:20Z] \"GET /c/6edafebf1e484d7e/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\""
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
  "requests": 2
 },
 "rows": {
  "request": [
   {
    "id": 1,
    "ts": "2026-10-03T14:13:20Z",
    "method": "GET",
    "path": "/m/q3-supplier-review",
    "status": 200,
    "ip_net": "20.171.207.0/24",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "ctx_id": "c0e7aead548d",
    "raw_line": "20.171.207.0/24 - - [2026-10-03T14:13:20Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\"",
    "origin": "seeded",
    "is_automated": 1
   },
   {
    "id": 2,
    "ts": "2026-10-03T14:13:20Z",
    "method": "GET",
    "path": "/c/6edafebf1e484d7e/q3-supplier-review",
    "status": 200,
    "ip_net": "104.28.52.0/24",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "ctx_id": "58a7736b46e0",
    "raw_line": "104.28.52.0/24 - - [2026-10-03T14:13:20Z] \"GET /c/6edafebf1e484d7e/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\"",
    "origin": "seeded",
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
    "ts": "2026-10-03T14:13:20Z",
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
    "ts": "2026-10-03T14:13:20Z"
   }
  ]
 },
 "leaves": [
  "0080a9d38b974ae7c77cb547c2f50508c04f512e712e8f5445fea2c4fb0a72f5",
  "a6c86026006dae9a1efb02d91fbfcb4a1c16ef796c8c1a2717cc64f32bbab694",
  "0319f1b7347fbae41369cf3908f211ea716bd39bd726551f2f2d4f60d66d055e",
  "73503f1e94c11f6fccb4333716ae7a0916f83d9318cebf7cd05e5da12b07a267",
  "4299b1fc737a5792ab6e342db29197fdee1005020bae540c47270d7a925e06c3"
 ],
 "root": "fc445b71f7cbc428c36eec82c64d71111ffb1fc9ec6ea815ccddc24769cb551b"
};
