#!/usr/bin/env bash
# Keep the local half of the collection path alive, and keep Vercel pointed at it.
#
#   nohup bash scripts/keep_alive.sh > .keepalive.log 2>&1 &
#
# The public surface lives on Vercel and survives this machine. The LEDGER does
# not: it is a local file (ADR-0005), reached over a signed hand-off through a
# Cloudflare quick tunnel (ADR-0006). That path broke three times in one day -
# the OOM killer, then two restarts of the machine - and each time it broke
# silently: Vercel kept serving crawlers and simply had nowhere to report them.
# A quick tunnel also gets a NEW hostname every time it restarts, so bringing
# the processes back is not enough; Vercel has to be told where they went.
#
# This loop does the three things a person kept doing by hand:
#   1. start the Flask surface if it is not answering;
#   2. start the tunnel if it is not registered;
#   3. if the tunnel hostname differs from the one Vercel was last given, update
#      CANARY_INGEST_URL and redeploy, then prove the path end to end.
#
# It cannot survive the machine itself going down - nothing here can - so after a
# reboot, run the line above again. Everything it needs is in .env.
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-python3}"
PORT="${PORT:-8000}"
CF="${CF:-$HOME/.local/bin/cloudflared}"
INTERVAL="${INTERVAL:-60}"
PUBLIC="${CANARY_PUBLIC_URL:-https://site-nine-hazel-35.vercel.app}"
STATE=".ingest_url"            # the hostname Vercel was last told about

set -a; [ -f .env ] && . ./.env; set +a
export CANARY_TRUST_PROXY=cloudflare
# Resolved through canarymaze.paths, never typed here: a ledger path written into
# a script is how a retired ledger got reopened three separate times (F-0004).
export CANARY_DB="${CANARY_DB:-$PWD/$("$PY" -c 'from canarymaze.paths import ledger_path; print(ledger_path())')}"
export PORT

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }

flask_ok()  { curl -fsS -o /dev/null --max-time 5 "http://127.0.0.1:$PORT/robots.txt" 2>/dev/null; }
tunnel_url() { grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' .tunnel.log 2>/dev/null | tail -1; }
tunnel_ok() {
  local u; u="$(tunnel_url)"
  [ -n "$u" ] && [ -f .tunnel.pid ] && kill -0 "$(cat .tunnel.pid)" 2>/dev/null \
    && curl -fsS -o /dev/null --max-time 15 "$u/robots.txt" 2>/dev/null
}

ensure_flask() {
  flask_ok && return 0
  log "flask not answering on :$PORT - starting it"
  setsid nohup "$PY" -m canarymaze.app >> .serve.log 2>&1 < /dev/null &
  echo $! > .flask.pid
  for _ in $(seq 1 15); do flask_ok && { log "flask up (pid $(cat .flask.pid))"; return 0; }; sleep 1; done
  log "flask FAILED to start; see .serve.log"; return 1
}

ensure_tunnel() {
  tunnel_ok && return 0
  log "tunnel not healthy - starting a new one (the hostname will change)"
  [ -f .tunnel.pid ] && kill "$(cat .tunnel.pid)" 2>/dev/null
  setsid nohup "$CF" tunnel --url "http://127.0.0.1:$PORT" --no-autoupdate > .tunnel.log 2>&1 < /dev/null &
  echo $! > .tunnel.pid
  for _ in $(seq 1 90); do
    if grep -q "Registered tunnel connection" .tunnel.log 2>/dev/null && tunnel_ok; then
      log "tunnel up: $(tunnel_url)"; return 0
    fi
    sleep 2
  done
  log "tunnel FAILED to become reachable; see .tunnel.log"; return 1
}

ledger_rows() {
  "$PY" - <<'PYEOF'
import os, sqlite3
try:
    print(sqlite3.connect(f"file:{os.environ['CANARY_DB']}?mode=ro", uri=True)
          .execute("SELECT COUNT(*) FROM request").fetchone()[0])
except Exception:
    print(-1)
PYEOF
}

# Prove the whole path: a request to the PUBLIC surface must become a row HERE.
# The probe carries the self-test token, so it can never be counted as evidence.
path_ok() {
  local before after
  before="$(ledger_rows)"
  curl -fsS -o /dev/null --max-time 30 \
       -A "canary-maze-keepalive/1.0" \
       -H "X-Canary-Selftest: ${CANARY_SELFTEST_TOKEN:-}" \
       "$PUBLIC/m/q3-supplier-review" 2>/dev/null || return 1
  for _ in 1 2 3 4 5; do
    sleep 1; after="$(ledger_rows)"
    [ "$after" -gt "$before" ] && return 0
  done
  return 1
}

sync_vercel() {
  local u; u="$(tunnel_url)"
  [ -z "$u" ] && return 1
  if [ "$(cat "$STATE" 2>/dev/null)" = "$u" ]; then return 0; fi
  log "tunnel hostname changed -> telling Vercel ($u)"
  ( cd site \
    && printf '%s' "$u" | vercel env add CANARY_INGEST_URL production --force >/dev/null 2>&1 \
    && vercel deploy --prod --yes >/dev/null 2>&1 ) || { log "vercel update FAILED"; return 1; }
  if path_ok; then
    echo "$u" > "$STATE"; log "collection path verified end to end"
  else
    log "vercel updated but the end-to-end probe did not land in the ledger"
    return 1
  fi
}

echo $$ > .keepalive.pid
log "keep_alive started (ledger: $CANARY_DB, public: $PUBLIC)"
while true; do
  ensure_flask && ensure_tunnel && sync_vercel
  sleep "$INTERVAL"
done
