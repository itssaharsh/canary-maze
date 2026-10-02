"""The one branching function. Attack it first."""
from canarymaze.detect import on_canary_request


def mint_one(led, ctx="ctxA", secret="s" * 16, ts="2026-10-03T11:04:12Z"):
    rid = led.record_request(method="GET", path="/m/x", status=200, ip="20.171.207.14",
                             ua="GPTBot/1.2", ctx_id=ctx, ts=ts)
    led.record_mint(secret=secret, ctx_id=ctx, path="/m/x", salt_epoch="2026-10-03",
                    request_id=rid, ts=ts)
    return secret


def fetch(led, ctx, ts="2026-10-03T11:08:47Z", ip="104.28.52.9"):
    return led.record_request(method="GET", path="/c/x/y", status=200, ip=ip,
                              ua="Chrome/124", ctx_id=ctx, ts=ts)


def test_a_different_context_is_a_sighting(ledger):
    s = mint_one(ledger)
    rid = fetch(ledger, "ctxB")
    assert on_canary_request(ledger, secret=s, seen_ctx_id="ctxB",
                             seen_request_id=rid, origin="organic") is not None
    assert ledger.counts()["sightings_organic"] == 1


def test_the_minting_context_is_never_a_sighting(ledger):
    s = mint_one(ledger)
    rid = fetch(ledger, "ctxA")
    assert on_canary_request(ledger, secret=s, seen_ctx_id="ctxA",
                             seen_request_id=rid) is None
    assert ledger.counts()["sightings_organic"] == 0


def test_an_unissued_secret_is_never_a_sighting(ledger):
    rid = fetch(ledger, "ctxB")
    assert on_canary_request(ledger, secret="f" * 16, seen_ctx_id="ctxB",
                             seen_request_id=rid) is None


def test_one_sighting_per_pair_however_often_it_is_refetched(ledger):
    s = mint_one(ledger)
    for _ in range(5):
        rid = fetch(ledger, "ctxB")
        on_canary_request(ledger, secret=s, seen_ctx_id="ctxB", seen_request_id=rid)
    assert ledger.counts()["sightings_organic"] == 1


def test_a_third_context_is_its_own_sighting(ledger):
    s = mint_one(ledger)
    for ctx in ("ctxB", "ctxC"):
        rid = fetch(ledger, ctx)
        on_canary_request(ledger, secret=s, seen_ctx_id=ctx, seen_request_id=rid)
    assert ledger.counts()["sightings_organic"] == 2


def test_elapsed_time_is_measured_from_the_mint(ledger):
    s = mint_one(ledger, ts="2026-10-03T11:04:12Z")
    rid = fetch(ledger, "ctxB", ts="2026-10-03T11:08:47Z")
    on_canary_request(ledger, secret=s, seen_ctx_id="ctxB", seen_request_id=rid)
    assert ledger.rows("sighting")[0]["delta_s"] == 275.0   # 4m 35s


def test_a_clock_skewed_backwards_does_not_produce_negative_elapsed_time(ledger):
    s = mint_one(ledger, ts="2026-10-03T11:04:12Z")
    rid = fetch(ledger, "ctxB", ts="2026-10-03T11:00:00Z")
    on_canary_request(ledger, secret=s, seen_ctx_id="ctxB", seen_request_id=rid)
    assert ledger.rows("sighting")[0]["delta_s"] == 0.0


def test_a_missing_request_row_is_not_a_sighting(ledger):
    s = mint_one(ledger)
    assert on_canary_request(ledger, secret=s, seen_ctx_id="ctxB",
                             seen_request_id=9999) is None


def test_seeded_and_organic_are_counted_separately(ledger):
    s = mint_one(ledger)
    rid = fetch(ledger, "ctxB")
    on_canary_request(ledger, secret=s, seen_ctx_id="ctxB", seen_request_id=rid,
                      origin="seeded")
    c = ledger.counts()
    assert c["sightings_seeded"] == 1 and c["sightings_organic"] == 0
