#!/usr/bin/env bash
# Deterministic proof, runnable with no network and no cloud credentials.
# Asserts a real before/after number and prints PASS or FAIL.
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-python3}"
DB="verify.sqlite3"
FAIL=0
note() { printf '  %-52s %s\n' "$1" "$2"; }

rm -f "$DB" "$DB-wal" "$DB-shm"

echo "Canary Maze :: verify"
echo

# One dependency, and without it every check below fails with a traceback that
# says nothing useful. Say the useful thing instead.
if ! "$PY" -c "import flask" 2>/dev/null; then
  echo "  Flask is not installed, so the surface cannot be exercised."
  echo "    $PY -m pip install -r requirements.txt"
  echo
  echo "FAIL (missing dependency, not a failed check)"
  exit 1
fi

# ---- 1. before/after on a real number -------------------------------------
BEFORE=$("$PY" - "$DB" <<'PY'
import sys; sys.path.insert(0, ".")
from canarymaze.ledger import Ledger
led = Ledger(sys.argv[1]); print(led.counts()["sightings_seeded"]); led.close()
PY
)
# stderr is kept: discarding it turned every setup problem into "0 -> 0 FAILED"
SEED_ERR=$("$PY" scripts/seed_replay.py --db "$DB" 2>&1 >/dev/null) || {
  echo "  the seeded replay could not run:"; echo "$SEED_ERR" | sed 's/^/    /'; }
AFTER=$("$PY" - "$DB" <<'PY'
import sys; sys.path.insert(0, ".")
from canarymaze.ledger import Ledger
led = Ledger(sys.argv[1]); print(led.counts()["sightings_seeded"]); led.close()
PY
)
if [ "$BEFORE" = "0" ] && [ "$AFTER" = "1" ]; then
  note "sightings before -> after" "$BEFORE -> $AFTER  OK"
else
  note "sightings before -> after" "$BEFORE -> $AFTER  FAILED (expected 0 -> 1)"; FAIL=1
fi

# ---- 2. the gate actually fires, and no human reaches storage -------------
# Two numbers, because one alone proves nothing. `human_requests` counts ledger
# rows marked non-automated and must be 0 - but nothing ever writes such a row, so
# on its own it is pinned to 0 whether the gate works or not. `humans_turned_away`
# is the falsifiable half: it only moves when the gate refuses a request. A review
# caught the original check asserting the vacuous one.
GATE=$("$PY" scripts/_gate_check.py "$DB")
set -- $GATE
if [ "$1" = "0" ] && [ "$2" -ge 1 ]; then
  note "gate turned a browser away, stored nothing" "turned away $2, in ledger $1  OK"
else
  note "gate turned a browser away, stored nothing" "turned away $2, in ledger $1  FAILED"; FAIL=1; fi

# ---- 3. the bundle verifies with no server and no network -----------------
# --out keeps this away from viewer/: without it every `make verify` overwrote the
# viewer's data with this throwaway ledger, and the landing page then published
# the counters of a test fixture as if they were the product's.
"$PY" scripts/export_all.py --db "$DB" --bundle bundles/verify.json --out bundles/verify-out >/dev/null 2>&1
if "$PY" -m canarymaze.bundle bundles/verify.json >/dev/null 2>&1; then
  note "bundle verifies offline" "OK"
else note "bundle verifies offline" "FAILED"; FAIL=1; fi

# ---- 4. tampering is caught and the row is named --------------------------
TAMPER=$("$PY" - <<'PY'
import json, sys; sys.path.insert(0, ".")
from canarymaze import bundle
b = bundle.load("bundles/verify.json")
b["rows"]["request"][0]["ua"] = "edited after the fact"
ok, problems = bundle.verify(b)
print("CAUGHT" if (not ok and any("request id=" in p for p in problems)) else "MISSED")
PY
)
if [ "$TAMPER" = "CAUGHT" ]; then note "an edited row is caught and named" "OK"
else note "an edited row is caught and named" "FAILED"; FAIL=1; fi

# ---- 5. nothing a model produced can reach the proof graph ----------------
# NOTE ON WHAT THIS DOES AND DOES NOT PROVE. There is no model integration in this
# build - laundered-token matching was scoped out and never written. So this is not
# "the model was disabled and the output did not change"; that phrasing was in an
# earlier version of this file and it described a feature that does not exist.
# What is tested is the STRUCTURAL guarantee: rows in the `laundered` table - the
# only place a model's output would ever land - cannot reach the bundle, because
# the bundle writer reads a fixed three-table allowlist and Ledger.rows() raises on
# anything else. That property holds whether or not the feature is ever built.
SAME=$("$PY" - "$DB" <<'PY'
import json, sys; sys.path.insert(0, ".")
from canarymaze import bundle
from canarymaze.ledger import Ledger
led = Ledger(sys.argv[1])
before = json.dumps(bundle.build(led), sort_keys=True)
led.db.execute("INSERT INTO laundered (secret, candidate_text, score, ts) VALUES (?,?,?,?)",
               ("x"*16, "a paraphrase a model scored highly", 0.93, "2026-10-03T12:00:00Z"))
led.db.commit()
after = json.dumps(bundle.build(led), sort_keys=True)
led.close()
print("IDENTICAL" if before == after else "DIFFERENT")
PY
)
if [ "$SAME" = "IDENTICAL" ]; then note "laundered rows cannot reach the bundle" "byte-identical  OK"
else note "laundered rows cannot reach the bundle" "DIFFERENT  FAILED"; FAIL=1; fi

rm -f "$DB" "$DB-wal" "$DB-shm" bundles/verify.json
echo
if [ "$FAIL" = "0" ]; then echo "PASS"; exit 0; else echo "FAIL"; exit 1; fi
