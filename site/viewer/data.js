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
  "humans_turned_away": 0,
  "requests": 2
 },
 "sightings": [
  {
   "secret": "2ed7dda1a2069f63",
   "origin": "seeded",
   "elapsed": "within the same second",
   "elapsed_s": 0.0,
   "issued": {
    "label": "A",
    "ctx_id": "c0e7aead548d",
    "at": "09:55:17",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "net": "20.171.207.0/24",
    "raw": "20.171.207.0/24 - - [2026-10-03T09:55:17Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\""
   },
   "requested": {
    "label": "B",
    "ctx_id": "58a7736b46e0",
    "at": "09:55:17",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "net": "104.28.52.0/24",
    "raw": "104.28.52.0/24 - - [2026-10-03T09:55:17Z] \"GET /c/2ed7dda1a2069f63/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\""
   }
  }
 ],
 "mint_sample": null
};
window.CANARY_BUNDLE = {
 "format": "canary-maze-bundle/3",
 "note": "make demo",
 "counts": {
  "mints": 1,
  "sightings_organic": 0,
  "sightings_seeded": 1,
  "sightings_paste": 0,
  "sightings_selftest": 0,
  "human_requests": 0,
  "humans_turned_away": 0,
  "requests": 2
 },
 "rows": {
  "request": [
   {
    "id": 1,
    "ts": "2026-10-03T09:55:17Z",
    "method": "GET",
    "path": "/m/q3-supplier-review",
    "status": 200,
    "ip_net": "20.171.207.0/24",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "ctx_id": "c0e7aead548d",
    "raw_line": "20.171.207.0/24 - - [2026-10-03T09:55:17Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\"",
    "origin": "seeded",
    "is_automated": 1
   },
   {
    "id": 2,
    "ts": "2026-10-03T09:55:17Z",
    "method": "GET",
    "path": "/c/2ed7dda1a2069f63/q3-supplier-review",
    "status": 200,
    "ip_net": "104.28.52.0/24",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "ctx_id": "58a7736b46e0",
    "raw_line": "104.28.52.0/24 - - [2026-10-03T09:55:17Z] \"GET /c/2ed7dda1a2069f63/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\"",
    "origin": "seeded",
    "is_automated": 1
   }
  ],
  "mint": [
   {
    "id": 1,
    "secret": "2ed7dda1a2069f63",
    "ctx_id": "c0e7aead548d",
    "path": "/m/q3-supplier-review",
    "salt_epoch": "2026-10-03",
    "ts": "2026-10-03T09:55:17Z",
    "request_id": 1
   }
  ],
  "sighting": [
   {
    "id": 1,
    "secret": "2ed7dda1a2069f63",
    "mint_ctx_id": "c0e7aead548d",
    "seen_ctx_id": "58a7736b46e0",
    "mint_request_id": 1,
    "seen_request_id": 2,
    "delta_s": 0.0,
    "origin": "seeded",
    "ts": "2026-10-03T09:55:17Z"
   }
  ]
 },
 "leaves": [
  "d9bf20fe0586b04fe2ff66f7305af67315600ddda99c19b21a3bdf7ee2fd3783",
  "c203ebc12f9f88c8afc2408f211410844aafb83afc27b7fb6e8de6d3f405aff5",
  "55f475bb45c122e37a52b015742f3d769df2009511a2a9a10c3c5f1ec9658c0f",
  "70967d3652b1c2161e7058d02092bd44ee805fa53d566f5dc961712612aa0c0d",
  "152385e5569db6e3eb7a07a6e3228ca49587ff5ded246b0f55deb2bd10d13b0d"
 ],
 "root": "6c5501e6a66a707e93076a1ac572d948854b3dfaca89071becbb8506743d8093"
};
