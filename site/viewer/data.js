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
    "at": "18:52:08",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "net": "20.171.207.0/24",
    "raw": "20.171.207.0/24 - - [2026-10-03T18:52:08Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\"",
    "via": "direct"
   },
   "requested": {
    "label": "B",
    "ctx_id": "acf2d741def9",
    "at": "18:52:08",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "net": "104.28.52.0/24",
    "raw": "104.28.52.0/24 - - [2026-10-03T18:52:08Z] \"GET /c/554e2618e7b1494c/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\"",
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
 "viewer": "73f56bf68c6d3f99dac03f351bed52224a5dbb9fd49838533b1e937365d12334",
 "rows": {
  "request": [
   {
    "id": 1,
    "ts": "2026-10-03T18:52:08Z",
    "method": "GET",
    "path": "/m/q3-supplier-review",
    "status": 200,
    "ip_net": "20.171.207.0/24",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "ctx_id": "937a02779f5d",
    "raw_line": "20.171.207.0/24 - - [2026-10-03T18:52:08Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\"",
    "origin": "seeded",
    "via": "direct",
    "is_automated": 1
   },
   {
    "id": 2,
    "ts": "2026-10-03T18:52:08Z",
    "method": "GET",
    "path": "/c/554e2618e7b1494c/q3-supplier-review",
    "status": 200,
    "ip_net": "104.28.52.0/24",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "ctx_id": "acf2d741def9",
    "raw_line": "104.28.52.0/24 - - [2026-10-03T18:52:08Z] \"GET /c/554e2618e7b1494c/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\"",
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
    "ts": "2026-10-03T18:52:08Z",
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
    "ts": "2026-10-03T18:52:08Z"
   }
  ],
  "published": []
 },
 "leaves": [
  "0f92ef22f7349ef8131e66c0d96dd209bdb514062e71ad04f3530675779d4de4",
  "15f727069cc04b4dc6e590324937bc44dbcf6786e413a7cf8a632f048b7c0077",
  "ce718abccb84395a633f838ba50370bc8db854c9161d577ba68a98c665649fa7",
  "54bb73553043dceb4987ce4b3c65d5b578c957adc932e776a1136887fef1d5bc",
  "ee0894f067de9ae33bf9919a2ca42fc5625aba5d29d6b4874e1c5be57ae99104"
 ],
 "root": "8ca61488d74632efc0edad8bd71184f6c47502647496a74c81158ce2854e9eaf"
};
