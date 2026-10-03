window.CANARY_DATA = {
 "state": "sighting",
 "scope_line": "A sighting establishes that the secret moved between two request contexts. It does not establish that they are two different operators - one operator can rotate addresses. In the organizers' collusion.wiki dump, the busiest named agent label wrote 317 revisions from 308 distinct addresses.",
 "claim": "A URL that only context A was ever shown was requested within the same second by context B, on a different network. This is a seeded replay, not observed traffic.",
 "counts": {
  "mints": 1,
  "sightings_organic": 0,
  "sightings_seeded": 1,
  "sightings_paste": 0,
  "sightings_selftest": 0,
  "human_requests": 0,
  "humans_turned_away": 0,
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
   "elapsed_s": "0.000000",
   "issued": {
    "label": "A",
    "ctx_id": "937a02779f5d",
    "at": "19:13:05",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "net": "20.171.207.0/24",
    "raw": "20.171.207.0/24 - - [2026-10-03T19:13:05Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\"",
    "via": "direct"
   },
   "requested": {
    "label": "B",
    "ctx_id": "acf2d741def9",
    "at": "19:13:05",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "net": "104.28.52.0/24",
    "raw": "104.28.52.0/24 - - [2026-10-03T19:13:05Z] \"GET /c/554e2618e7b1494c/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\"",
    "via": "direct"
   }
  }
 ],
 "mint_sample": null
};
window.CANARY_BUNDLE = {
 "format": "canary-maze-bundle/5",
 "note": "make demo",
 "counts": {
  "mints": 1,
  "sightings_organic": 0,
  "sightings_seeded": 1,
  "sightings_paste": 0,
  "sightings_selftest": 0,
  "human_requests": 0,
  "humans_turned_away": 0,
  "published": 0,
  "requests": 2,
  "requests_direct": 2,
  "requests_reported": 0
 },
 "viewer": "e510fcde5dc070755e11ad9378ab1fefbb75e4e14452fe8af05cfb31fa0d3ae2",
 "rows": {
  "request": [
   {
    "id": 1,
    "ts": "2026-10-03T19:13:05Z",
    "method": "GET",
    "path": "/m/q3-supplier-review",
    "status": 200,
    "ip_net": "20.171.207.0/24",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "ctx_id": "937a02779f5d",
    "raw_line": "20.171.207.0/24 - - [2026-10-03T19:13:05Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\"",
    "origin": "seeded",
    "via": "direct",
    "is_automated": 1
   },
   {
    "id": 2,
    "ts": "2026-10-03T19:13:05Z",
    "method": "GET",
    "path": "/c/554e2618e7b1494c/q3-supplier-review",
    "status": 200,
    "ip_net": "104.28.52.0/24",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "ctx_id": "acf2d741def9",
    "raw_line": "104.28.52.0/24 - - [2026-10-03T19:13:05Z] \"GET /c/554e2618e7b1494c/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\"",
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
    "ts": "2026-10-03T19:13:05Z",
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
    "ts": "2026-10-03T19:13:05Z"
   }
  ],
  "published": []
 },
 "leaves": [
  "d236d038310bcfb29d22733c567cb513d7749d36814304ca037556b0abfd8e47",
  "e52034ae301c79881f146245296d87395cfad1be80e5ba71ea2222fdf2dd5545",
  "4cf3d868255e1652256848e29dfa8ba9d17483e81f2bceb7b2b611133b6d5370",
  "598b8a5c8dc2789ac0a583f77b63d3eb695b0b63f5b72f044a7a91db0a57e75a",
  "a4ea5883fa7f084a82a70ce38d775282bbbaed3ca930b54313f8a23060c89bc7"
 ],
 "root": "10666c65bbf5d97b5e85e7941136ab24fbf675a5b2e65dbf11a0819ec240a5d8"
};
