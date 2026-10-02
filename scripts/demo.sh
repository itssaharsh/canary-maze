#!/usr/bin/env bash
# One command, no network, no server: build the whole artefact from scratch.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-python3}"
DB="${CANARY_DB:-demo.sqlite3}"

echo "==> clean"
rm -f "$DB" "$DB-wal" "$DB-shm"

echo "==> seeded two-client replay (through the real gate, mint and detector)"
"$PY" scripts/seed_replay.py --db "$DB"

echo
echo "==> export bundle and viewer"
"$PY" scripts/export_all.py --db "$DB" --note "make demo"

echo
echo "==> verify the bundle offline"
"$PY" -m canarymaze.bundle bundles/bundle.json

echo
echo "Open viewer/index.html in a browser. It needs no server and no network."
