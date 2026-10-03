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
    "at": "18:15:54",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "net": "20.171.207.0/24",
    "raw": "20.171.207.0/24 - - [2026-10-03T18:15:54Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\"",
    "via": "direct"
   },
   "requested": {
    "label": "B",
    "ctx_id": "acf2d741def9",
    "at": "18:15:54",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "net": "104.28.52.0/24",
    "raw": "104.28.52.0/24 - - [2026-10-03T18:15:54Z] \"GET /c/554e2618e7b1494c/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\"",
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
    "ts": "2026-10-03T18:15:54Z",
    "method": "GET",
    "path": "/m/q3-supplier-review",
    "status": 200,
    "ip_net": "20.171.207.0/24",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "ctx_id": "937a02779f5d",
    "raw_line": "20.171.207.0/24 - - [2026-10-03T18:15:54Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\"",
    "origin": "seeded",
    "via": "direct",
    "is_automated": 1
   },
   {
    "id": 2,
    "ts": "2026-10-03T18:15:54Z",
    "method": "GET",
    "path": "/c/554e2618e7b1494c/q3-supplier-review",
    "status": 200,
    "ip_net": "104.28.52.0/24",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "ctx_id": "acf2d741def9",
    "raw_line": "104.28.52.0/24 - - [2026-10-03T18:15:54Z] \"GET /c/554e2618e7b1494c/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\"",
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
    "ts": "2026-10-03T18:15:54Z",
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
    "ts": "2026-10-03T18:15:54Z"
   }
  ],
  "published": []
 },
 "leaves": [
  "ea0887038aa4385eb54aec0c017d128a3a0cf3e25e6b4ad070320cca627fbaed",
  "0db8822eb94d02679486aaebf43343d155ef15c9711fd546c693268cbaecf472",
  "ccfdbef49e9741854be13b842b0a16085bc947d58b9d4233e8325f3c56e4fb74",
  "8181c98434804f720163eca07d3efb68ec35af368ed0c5d4f4139023bc30e7d3",
  "78c87f2401b502f21fc9cb53be4df18fd8d0f00e3bd05ee74764b57cccbb8e3c"
 ],
 "root": "5579893b7b33c6dc10f63e49470c9188852f7d73a180777a46f901762bb9d8b0"
};
