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
   "elapsed_s": "0.000000",
   "issued": {
    "label": "A",
    "ctx_id": "937a02779f5d",
    "at": "18:40:47",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "net": "20.171.207.0/24",
    "raw": "20.171.207.0/24 - - [2026-10-03T18:40:47Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\"",
    "via": "direct"
   },
   "requested": {
    "label": "B",
    "ctx_id": "acf2d741def9",
    "at": "18:40:47",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "net": "104.28.52.0/24",
    "raw": "104.28.52.0/24 - - [2026-10-03T18:40:47Z] \"GET /c/554e2618e7b1494c/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\"",
    "via": "direct"
   }
  }
 ],
 "mint_sample": null
};
window.CANARY_BUNDLE = {
 "format": "canary-maze-bundle/5",
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
 "viewer": "baf2909a7f8c040fe241ec441478010f5b1d54bacbb1dfd64448ac4812bc7186",
 "rows": {
  "request": [
   {
    "id": 1,
    "ts": "2026-10-03T18:40:47Z",
    "method": "GET",
    "path": "/m/q3-supplier-review",
    "status": 200,
    "ip_net": "20.171.207.0/24",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "ctx_id": "937a02779f5d",
    "raw_line": "20.171.207.0/24 - - [2026-10-03T18:40:47Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\"",
    "origin": "seeded",
    "via": "direct",
    "is_automated": 1
   },
   {
    "id": 2,
    "ts": "2026-10-03T18:40:47Z",
    "method": "GET",
    "path": "/c/554e2618e7b1494c/q3-supplier-review",
    "status": 200,
    "ip_net": "104.28.52.0/24",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "ctx_id": "acf2d741def9",
    "raw_line": "104.28.52.0/24 - - [2026-10-03T18:40:47Z] \"GET /c/554e2618e7b1494c/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\"",
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
    "ts": "2026-10-03T18:40:47Z",
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
    "ts": "2026-10-03T18:40:47Z"
   }
  ],
  "published": []
 },
 "leaves": [
  "b4c811b35d72287ae2cb5833a777f29bf19f9019a5b658d4ffdf86e8a60bd79e",
  "1b7975ce2c28d435c04a08e7e4dfc091cf015a566e6accb552d7e1def715894a",
  "75e4ba08942286c013226f6300374009079f9c488e47b669f8baf33187db0766",
  "b21555cc4c594a50d7f1b5e095142236eca6a07e78791542893f6d06f3c382d6",
  "d3b7b0a24b2e0d4b2eb3640e0a3519a63eb304204d94e4c5b47e9d013e0f65c0"
 ],
 "root": "ec6e18b7c2358a9abf6cab76aee730606cea3fa274952540bfaba47ab6abd243"
};
