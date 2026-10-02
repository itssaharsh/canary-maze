"""Every line the viewer shows is computed here, so no state can contradict itself.

This is the regression test for the three on-screen contradictions a fresh
evaluator found in the hardcoded prototype (docs/memory/feedback/U-0001).
"""
import subprocess
import sys
from pathlib import Path

from canarymaze.export import export, human_delta
from canarymaze.ledger import Ledger

ROOT = Path(__file__).resolve().parents[1]


def test_empty_ledger_claims_nothing(ledger):
    p = export(ledger)
    assert p["state"] == "empty"
    assert p["sightings"] == [] and p["mint_sample"] is None
    assert "No secrets issued yet" in p["claim"]


def test_awaiting_state_never_names_a_second_context(ledger):
    rid = ledger.record_request(method="GET", path="/m/x", status=200,
                                ip="20.171.207.14", ua="GPTBot/1.2", ctx_id="ctxA")
    ledger.record_mint(secret="s" * 16, ctx_id="ctxA", path="/m/x",
                       salt_epoch="E", request_id=rid)
    p = export(ledger)
    assert p["state"] == "awaiting"
    # the contradiction the evaluator found: a populated second context on a screen
    # that says no second context has been seen
    assert p["sightings"] == []
    assert "No other context has requested" in p["claim"]
    # the live secret must NOT be published: /export.json is public, and leaking it
    # let any reader fetch the canary and manufacture an organic sighting
    ms = p["mint_sample"]
    assert ms is not None
    assert "secret" not in ms, "the public export must never carry the live secret"
    assert ms["secret_prefix"] == "ssss\u2026"
    assert "s" * 16 not in ms["raw"], "the raw line must have the secret redacted too"


def test_sighting_state_claims_exactly_what_happened(ledger):
    a = ledger.record_request(method="GET", path="/m/x", status=200, ip="20.171.207.14",
                              ua="GPTBot/1.2", ctx_id="ctxA", ts="2026-10-03T11:04:12Z")
    ledger.record_mint(secret="s" * 16, ctx_id="ctxA", path="/m/x", salt_epoch="E",
                       request_id=a, ts="2026-10-03T11:04:12Z")
    b = ledger.record_request(method="GET", path="/c/s/x", status=200, ip="104.28.52.9",
                              ua="Chrome/124", ctx_id="ctxB", ts="2026-10-03T11:08:47Z")
    from canarymaze.detect import on_canary_request
    on_canary_request(ledger, secret="s" * 16, seen_ctx_id="ctxB", seen_request_id=b,
                      origin="seeded")

    p = export(ledger)
    assert p["state"] == "sighting"
    s = p["sightings"][0]
    assert s["issued"]["label"] == "A" and s["requested"]["label"] == "B"
    assert s["elapsed"] == "4m 35s"
    assert "4m 35s" in p["claim"]
    # the raw records carry the truncated network, never a full address
    assert "20.171.207.0/24" in s["issued"]["raw"]
    assert "20.171.207.14" not in s["issued"]["raw"]


def test_the_scope_line_is_always_present_and_bounds_the_claim(ledger):
    for _ in range(1):
        p = export(ledger)
        assert "does not establish that they are two different operators" in p["scope_line"]
        assert "741" in p["scope_line"]


def test_the_claim_never_says_actor_or_operator_as_a_conclusion(ledger):
    a = ledger.record_request(method="GET", path="/m/x", status=200, ip="1.2.3.4",
                              ua="GPTBot/1.2", ctx_id="ctxA")
    ledger.record_mint(secret="s" * 16, ctx_id="ctxA", path="/m/x", salt_epoch="E",
                       request_id=a)
    b = ledger.record_request(method="GET", path="/c/s/x", status=200, ip="9.9.9.9",
                              ua="Chrome/124", ctx_id="ctxB")
    from canarymaze.detect import on_canary_request
    on_canary_request(ledger, secret="s" * 16, seen_ctx_id="ctxB", seen_request_id=b)
    claim = export(ledger)["claim"].lower()
    for forbidden in ("actor", "attacker", "operator", "bot farm"):
        assert forbidden not in claim, f"the claim must not assert {forbidden!r}"


def test_counts_separate_organic_from_seeded(ledger):
    p = export(ledger)
    c = p["counts"]
    assert {"sightings_organic", "sightings_seeded", "sightings_paste",
            "human_requests"} <= set(c)


def test_human_delta_reads_naturally():
    assert human_delta(275) == "4m 35s"
    assert human_delta(42) == "42s"
    assert human_delta(3600) == "1h 00m"


def test_the_seeded_replay_runs_end_to_end_and_marks_everything_seeded(tmp_path):
    db = tmp_path / "replay.sqlite3"
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "seed_replay.py"),
                        "--db", str(db)], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr

    led = Ledger(str(db))
    c = led.counts()
    assert c["sightings_seeded"] == 1, "the replay must produce a real sighting"
    assert c["sightings_organic"] == 0, "the replay must never touch the organic count"
    assert c["human_requests"] == 0
    p = export(led)
    assert p["state"] == "sighting"
    assert p["sightings"][0]["origin"] == "seeded"
    led.close()


def _sighting(ledger, ip_a, ip_b):
    a = ledger.record_request(method="GET", path="/m/x", status=200, ip=ip_a,
                              ua="GPTBot/1.2", ctx_id="ctxA", ts="2026-10-03T11:04:12Z")
    ledger.record_mint(secret="s" * 16, ctx_id="ctxA", path="/m/x", salt_epoch="E",
                       request_id=a, ts="2026-10-03T11:04:12Z")
    b = ledger.record_request(method="GET", path="/c/s/x", status=200, ip=ip_b,
                              ua="Chrome/124", ctx_id="ctxB", ts="2026-10-03T11:04:12Z")
    from canarymaze.detect import on_canary_request
    on_canary_request(ledger, secret="s" * 16, seen_ctx_id="ctxB", seen_request_id=b)
    return export(ledger)["claim"]


def test_the_network_clause_is_derived_not_asserted(ledger):
    claim = _sighting(ledger, "20.171.207.14", "104.28.52.9")
    assert "on a different network" in claim


def test_no_network_clause_when_the_networks_match(ledger):
    # same /24: saying "on a different network" here would be false
    claim = _sighting(ledger, "20.171.207.14", "20.171.207.99")
    assert "on a different network" not in claim


def test_a_sub_second_gap_is_described_honestly_not_padded(ledger):
    claim = _sighting(ledger, "1.2.3.4", "9.9.9.9")
    assert "within the same second" in claim
    assert "0s later" not in claim
