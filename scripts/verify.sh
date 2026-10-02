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

# ---- 1. before/after on a real number -------------------------------------
BEFORE=$("$PY" - "$DB" <<'PY'
import sys; sys.path.insert(0, ".")
from canarymaze.ledger import Ledger
led = Ledger(sys.argv[1]); print(led.counts()["sightings_seeded"]); led.close()
PY
)
"$PY" scripts/seed_replay.py --db "$DB" >/dev/null 2>&1
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

# ---- 2. no human ever entered the ledger ----------------------------------
HUMANS=$("$PY" - "$DB" <<'PY'
import sys; sys.path.insert(0, ".")
from canarymaze.ledger import Ledger
led = Ledger(sys.argv[1]); print(led.counts()["human_requests"]); led.close()
PY
)
if [ "$HUMANS" = "0" ]; then note "human requests in ledger" "0  OK"
else note "human requests in ledger" "$HUMANS  FAILED (the gate is broken)"; FAIL=1; fi

# ---- 3. the bundle verifies with no server and no network -----------------
"$PY" scripts/export_all.py --db "$DB" --bundle bundles/verify.json >/dev/null 2>&1
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

# ---- 5. the model cannot reach the proof graph ----------------------------
# Populate the laundered table (what a model would produce) and rebuild. The
# bundle must be byte-identical, which is what "no model on the proof path" means.
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
if [ "$SAME" = "IDENTICAL" ]; then note "proof graph with the model enabled vs off" "byte-identical  OK"
else note "proof graph with the model enabled vs off" "DIFFERENT  FAILED"; FAIL=1; fi

rm -f "$DB" "$DB-wal" "$DB-shm" bundles/verify.json
echo
if [ "$FAIL" = "0" ]; then echo "PASS"; exit 0; else echo "FAIL"; exit 1; fi
