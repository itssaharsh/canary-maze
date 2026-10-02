window.CANARY_DATA = {
 "state": "sighting",
 "scope_line": "A sighting establishes that the secret moved between two request contexts. It does not establish that they are two different operators - one operator can rotate addresses. In the AI Village dump, one actor label spans 741 of them.",
 "claim": "A URL that only context A was ever shown was requested within the same second by context B, on a different network.",
 "counts": {
  "mints": 1,
  "sightings_organic": 0,
  "sightings_seeded": 1,
  "sightings_paste": 0,
  "human_requests": 0,
  "humans_turned_away": 1,
  "requests": 2
 },
 "sightings": [
  {
   "secret": "369bf1645c560f02",
   "origin": "seeded",
   "elapsed": "within the same second",
   "elapsed_s": 0.0,
   "issued": {
    "label": "A",
    "ctx_id": "c0e7aead548d",
    "at": "22:16:02",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "net": "20.171.207.0/24",
    "raw": "20.171.207.0/24 - - [2026-10-02T22:16:02Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\""
   },
   "requested": {
    "label": "B",
    "ctx_id": "58a7736b46e0",
    "at": "22:16:02",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "net": "104.28.52.0/24",
    "raw": "104.28.52.0/24 - - [2026-10-02T22:16:02Z] \"GET /c/369bf1645c560f02/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\""
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
  "human_requests": 0,
  "humans_turned_away": 1,
  "requests": 2
 },
 "rows": {
  "request": [
   {
    "id": 1,
    "ts": "2026-10-02T22:16:02Z",
    "method": "GET",
    "path": "/m/q3-supplier-review",
    "status": 200,
    "ip_net": "20.171.207.0/24",
    "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "ctx_id": "c0e7aead548d",
    "raw_line": "20.171.207.0/24 - - [2026-10-02T22:16:02Z] \"GET /m/q3-supplier-review HTTP/1.1\" 200 872 \"-\" \"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)\"",
    "origin": "seeded",
    "is_automated": 1
   },
   {
    "id": 2,
    "ts": "2026-10-02T22:16:02Z",
    "method": "GET",
    "path": "/c/369bf1645c560f02/q3-supplier-review",
    "status": 200,
    "ip_net": "104.28.52.0/24",
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "ctx_id": "58a7736b46e0",
    "raw_line": "104.28.52.0/24 - - [2026-10-02T22:16:02Z] \"GET /c/369bf1645c560f02/q3-supplier-review HTTP/1.1\" 200 606 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\"",
    "origin": "seeded",
    "is_automated": 1
   }
  ],
  "mint": [
   {
    "id": 1,
    "secret": "369bf1645c560f02",
    "ctx_id": "c0e7aead548d",
    "path": "/m/q3-supplier-review",
    "salt_epoch": "2026-10-02",
    "ts": "2026-10-02T22:16:02Z",
    "request_id": 1
   }
  ],
  "sighting": [
   {
    "id": 1,
    "secret": "369bf1645c560f02",
    "mint_ctx_id": "c0e7aead548d",
    "seen_ctx_id": "58a7736b46e0",
    "mint_request_id": 1,
    "seen_request_id": 2,
    "delta_s": 0.0,
    "origin": "seeded",
    "ts": "2026-10-02T22:16:02Z"
   }
  ]
 },
 "leaves": [
  "0f00463c45513ba8fd72d821b3779b53dcb8c2164b5ec5bc5a336b656703c580",
  "8c5696ce60760a95f0f1f75139cff8ad86b490dd3f7ffd61215c643e47753fcb",
  "d2f2b87474b4ebb6e71f4f25c03fbc18eb2d75e07cdb5aff13a717980a798f60",
  "ed5ee60ec053f23f495d54c4433f8de97a90b37d5950f55103a0f4f0a22fe098",
  "fd8b2fd1dc2e47060c84b22319fd139844c4688d59357f31e00b860c2ddc08a7"
 ],
 "root": "f3d10c653502f6ef76e068f010e95e3e00321d2bb78aa465769f6dc6637a23b2"
};
