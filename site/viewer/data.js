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
    "at": "14:56:53",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "net": "20.171.207.0/24",
    "raw": "20.171.207.0/24 - - [2026-10-03T14:56:53Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\""
   },
   "requested": {
    "label": "B",
    "ctx_id": "58a7736b46e0",
    "at": "14:56:53",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "net": "104.28.52.0/24",
    "raw": "104.28.52.0/24 - - [2026-10-03T14:56:53Z] \"GET /c/6edafebf1e484d7e/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\""
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
  "requests": 2,
  "requests_direct": 2,
  "requests_reported": 0
 },
 "rows": {
  "request": [
   {
    "id": 1,
    "ts": "2026-10-03T14:56:53Z",
    "method": "GET",
    "path": "/m/q3-supplier-review",
    "status": 200,
    "ip_net": "20.171.207.0/24",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "ctx_id": "c0e7aead548d",
    "raw_line": "20.171.207.0/24 - - [2026-10-03T14:56:53Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\"",
    "origin": "seeded",
    "via": "direct",
    "is_automated": 1
   },
   {
    "id": 2,
    "ts": "2026-10-03T14:56:53Z",
    "method": "GET",
    "path": "/c/6edafebf1e484d7e/q3-supplier-review",
    "status": 200,
    "ip_net": "104.28.52.0/24",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "ctx_id": "58a7736b46e0",
    "raw_line": "104.28.52.0/24 - - [2026-10-03T14:56:53Z] \"GET /c/6edafebf1e484d7e/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\"",
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
    "ts": "2026-10-03T14:56:53Z",
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
    "ts": "2026-10-03T14:56:53Z"
   }
  ]
 },
 "leaves": [
  "32143a886df116e38c1c254273809f0e40a067ff211391f9ff7bef3d2fc6afeb",
  "c3397c33c612b5bbc9f579f5c48c3c07074a95352866e9ca4fbda521c7f0db91",
  "d0cbe28c5ccd7b0f3163f0284179da1700afa94314d773e1385b561732a8452c",
  "384d2ade2c0c36ba036d1fb6fec8cbdad151fe385935258048a961eff311a93c",
  "077a2fa04f46925ab9703ce0970335a9af25a7e265620020e7032be8f198bbdb"
 ],
 "root": "385d506264485019dbaf4a81233851614b991e2e85c3b9b7fbd7732ae093217f"
};
