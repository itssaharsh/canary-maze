window.CANARY_DATA = {
 "state": "sighting",
 "scope_line": "A sighting establishes that the secret moved between two request contexts. It does not establish that they are two different operators - one operator can rotate addresses. In the organizers' collusion.wiki dump, one actor label spans 741 of them.",
 "claim": "A URL that only context A was ever shown was requested within the same second by context B, on a different network. This is a seeded replay, not observed traffic.",
 "counts": {
  "mints": 1,
  "sightings_organic": 0,
  "sightings_seeded": 1,
  "sightings_paste": 0,
  "sightings_selftest": 0,
  "human_requests": 0,
  "humans_turned_away": 1,
  "published": 0,
  "requests": 2,
  "requests_direct": 2,
  "requests_reported": 0
 },
 "sightings": [
  {
   "id": 1,
   "secret": "554e2618e7b1494c",
   "origin": "seeded",
   "recorded_origin": "seeded",
   "elapsed": "within the same second",
   "elapsed_s": 0.0,
   "issued": {
    "label": "A",
    "ctx_id": "937a02779f5d",
    "at": "18:13:54",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "net": "20.171.207.0/24",
    "raw": "20.171.207.0/24 - - [2026-10-03T18:13:54Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\"",
    "via": "direct"
   },
   "requested": {
    "label": "B",
    "ctx_id": "acf2d741def9",
    "at": "18:13:54",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "net": "104.28.52.0/24",
    "raw": "104.28.52.0/24 - - [2026-10-03T18:13:54Z] \"GET /c/554e2618e7b1494c/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\"",
    "via": "direct"
   }
  }
 ],
 "mint_sample": null
};
window.CANARY_BUNDLE = {
 "format": "canary-maze-bundle/4",
 "note": "",
 "counts": {
  "mints": 1,
  "sightings_organic": 0,
  "sightings_seeded": 1,
  "sightings_paste": 0,
  "sightings_selftest": 0,
  "human_requests": 0,
  "humans_turned_away": 1,
  "published": 0,
  "requests": 2,
  "requests_direct": 2,
  "requests_reported": 0
 },
 "rows": {
  "request": [
   {
    "id": 1,
    "ts": "2026-10-03T18:13:54Z",
    "method": "GET",
    "path": "/m/q3-supplier-review",
    "status": 200,
    "ip_net": "20.171.207.0/24",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "ctx_id": "937a02779f5d",
    "raw_line": "20.171.207.0/24 - - [2026-10-03T18:13:54Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\"",
    "origin": "seeded",
    "via": "direct",
    "is_automated": 1
   },
   {
    "id": 2,
    "ts": "2026-10-03T18:13:54Z",
    "method": "GET",
    "path": "/c/554e2618e7b1494c/q3-supplier-review",
    "status": 200,
    "ip_net": "104.28.52.0/24",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "ctx_id": "acf2d741def9",
    "raw_line": "104.28.52.0/24 - - [2026-10-03T18:13:54Z] \"GET /c/554e2618e7b1494c/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\"",
    "origin": "seeded",
    "via": "direct",
    "is_automated": 1
   }
  ],
  "mint": [
   {
    "id": 1,
    "secret": "554e2618e7b1494c",
    "ctx_id": "937a02779f5d",
    "path": "/m/q3-supplier-review",
    "salt_epoch": "2026-10-03",
    "ts": "2026-10-03T18:13:54Z",
    "request_id": 1
   }
  ],
  "sighting": [
   {
    "id": 1,
    "secret": "554e2618e7b1494c",
    "mint_ctx_id": "937a02779f5d",
    "seen_ctx_id": "acf2d741def9",
    "mint_request_id": 1,
    "seen_request_id": 2,
    "delta_s": 0.0,
    "origin": "seeded",
    "ts": "2026-10-03T18:13:54Z"
   }
  ],
  "published": []
 },
 "leaves": [
  "ea0887038aa4385eb54aec0c017d128a3a0cf3e25e6b4ad070320cca627fbaed",
  "4ce5be523c4ad61e40fecd18dd24f79639f27caa4a38d4207fdd2cf6d23aa1b2",
  "bc639736b8ea3f1d1885e268f9ed18dcb588d98a73a2b05a1e2533a0794cebc5",
  "7cd05ac21ae76bbf16d6d921c1c5dfa5db099287519daf1dece4df92fcdb2992",
  "04b26d45d6e08328800d7fd094e22cd5882d4bb32f2cc94319b07f9d086408c6"
 ],
 "root": "da3f02bf9bb102614126ef0b936b211939cb81e36f2fd712268c6309ef584dbd"
};
