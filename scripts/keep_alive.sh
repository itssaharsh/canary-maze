#!/usr/bin/env bash
# Keep the local half of the collection path alive, and keep Vercel pointed at it.
#
#   nohup bash scripts/keep_alive.sh > .keepalive.log 2>&1 &
#
# The public surface lives on Vercel and survives this machine. The LEDGER does
# not: it is a local file (ADR-0005), reached over a signed hand-off through a
# Cloudflare quick tunnel (ADR-0006). That path broke three times in one day and
# each time it broke silently: Vercel kept serving crawlers and simply had nowhere
# to report them. A quick tunnel also gets a NEW hostname every time it restarts,
# so bringing the processes back is not enough; Vercel has to be told.
#
# This loop does what a person kept doing by hand:
#   1. start the Flask surface if it is not answering;
#   2. start the tunnel if it has been unhealthy for several checks in a row;
#   3. if the tunnel hostname differs from the one Vercel was last given, update
#      CANARY_INGEST_URL, redeploy the LAST COMMIT, and prove the path end to end.
#
# What an independent review found wrong with the first version, all fixed here:
#   - it replaced a working tunnel after ONE failed probe, and a quick tunnel's
#     hostname cannot be recovered, so a 20-second Wi-Fi drop cost a redeploy and
#     every report in between;
#   - it deployed production from the working tree, uncommitted edits included;
#   - a probe that kept failing redeployed once a minute with no limit;
#   - it signalled whatever PID a stale pidfile named, and nothing stopped two
#     copies of the loop from running.
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
FAILS_BEFORE_REPLACE=3         # consecutive unhealthy checks before a tunnel is replaced
MAX_DEPLOYS_PER_HOUR=4

set -a; [ -f .env ] && . ./.env; set +a
export CANARY_TRUST_PROXY=cloudflare
# Resolved through canarymaze.paths, never typed here: a ledger path written into
# a script is how a retired ledger got reopened three separate times (F-0004).
export CANARY_DB="${CANARY_DB:-$PWD/$("$PY" -c 'from canarymaze.paths import ledger_path; print(ledger_path())')}"
export PORT

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }

# ---- one loop at a time ------------------------------------------------------
is_proc() {   # is_proc <pid> <substring of its command line>
  [ -n "${1:-}" ] && [ -r "/proc/$1/cmdline" ] && tr '\0' ' ' < "/proc/$1/cmdline" | grep -q -- "$2"
}
if is_proc "$(cat .keepalive.pid 2>/dev/null)" "keep_alive.sh" && [ "$(cat .keepalive.pid)" != "$$" ]; then
  log "another keep_alive loop is already running (pid $(cat .keepalive.pid)); exiting"
  exit 0
fi
echo $$ > .keepalive.pid

# ---- health ------------------------------------------------------------------
flask_ok()   { curl -fsS -o /dev/null --max-time 5 "http://127.0.0.1:$PORT/robots.txt" 2>/dev/null; }
tunnel_url() { grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' .tunnel.log 2>/dev/null | tail -1; }
tunnel_pid() { local p; p="$(cat .tunnel.pid 2>/dev/null)"; is_proc "$p" "cloudflared" && echo "$p"; }

# cloudflared's own readiness endpoint: it answers 200 only while a connection to
# the edge is registered. Asking the process is a better test than asking the
# internet whether it can currently reach the process.
tunnel_ready() {
  local port
  port="$(grep -oE 'metrics server on 127\.0\.0\.1:[0-9]+' .tunnel.log 2>/dev/null | tail -1 | grep -oE '[0-9]+$')"
  [ -n "$port" ] && curl -fsS -o /dev/null --max-time 5 "http://127.0.0.1:$port/ready" 2>/dev/null
}
tunnel_ok() { [ -n "$(tunnel_pid)" ] && [ -n "$(tunnel_url)" ] && tunnel_ready; }

ensure_flask() {
  flask_ok && return 0
  log "flask not answering on :$PORT - starting it"
  setsid nohup "$PY" -m canarymaze.app >> .serve.log 2>&1 < /dev/null &
  echo $! > .flask.pid
  for _ in $(seq 1 15); do flask_ok && { log "flask up (pid $(cat .flask.pid))"; return 0; }; sleep 1; done
  log "flask FAILED to start; see .serve.log"; return 1
}

TUNNEL_FAILS=0
ensure_tunnel() {
  if tunnel_ok; then TUNNEL_FAILS=0; return 0; fi
  TUNNEL_FAILS=$((TUNNEL_FAILS + 1))
  if [ -n "$(tunnel_pid)" ] && [ "$TUNNEL_FAILS" -lt "$FAILS_BEFORE_REPLACE" ]; then
    log "tunnel not ready ($TUNNEL_FAILS/$FAILS_BEFORE_REPLACE) - leaving it; its hostname cannot be recovered"
    return 1
  fi
  log "tunnel down - starting a new one (the hostname will change)"
  local old; old="$(tunnel_pid)"; [ -n "$old" ] && kill "$old" 2>/dev/null
  setsid nohup "$CF" tunnel --url "http://127.0.0.1:$PORT" --no-autoupdate > .tunnel.log 2>&1 < /dev/null &
  echo $! > .tunnel.pid
  for _ in $(seq 1 60); do
    if tunnel_ok; then TUNNEL_FAILS=0; log "tunnel up: $(tunnel_url)"; return 0; fi
    sleep 2
  done
  log "tunnel FAILED to become ready; see .tunnel.log"; return 1
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
# The probe carries the self-test token, so it is recorded as the operator's own
# and can never be counted as evidence about anyone else.
path_ok() {
  local before after
  before="$(ledger_rows)"
  curl -fsS -o /dev/null --max-time 30 \
       -A "canary-maze-keepalive/1.0" \
       -H "X-Canary-Selftest: ${CANARY_SELFTEST_TOKEN:-}" \
       "$PUBLIC/m/q3-supplier-review" 2>/dev/null || return 1
  for _ in 1 2 3 4 5 6 7 8; do
    sleep 1; after="$(ledger_rows)"
    [ "$after" -gt "$before" ] && return 0
  done
  return 1
}

# Deploy exactly what is committed. `git archive` cannot see the working tree, so
# an edit in progress - or a landing page built from a test fixture - cannot ship.
deploy_head() {
  local tmp; tmp="$(mktemp -d)"
  git archive HEAD site | tar -x -C "$tmp" || { rm -rf "$tmp"; return 1; }
  cp -r site/.vercel "$tmp/site/.vercel" 2>/dev/null
  ( cd "$tmp/site" && vercel deploy --prod --yes >/dev/null 2>&1 ); local rc=$?
  rm -rf "$tmp"
  return $rc
}

DEPLOY_TIMES=""          # epoch seconds of recent deploys, for the hourly cap
BACKOFF=0
sync_vercel() {
  local u now recent
  u="$(tunnel_url)"; [ -z "$u" ] && return 1
  [ "$(cat "$STATE" 2>/dev/null)" = "$u" ] && { BACKOFF=0; return 0; }

  now="$(date +%s)"
  if [ "$BACKOFF" -gt "$now" ]; then return 1; fi
  recent=""; for t in $DEPLOY_TIMES; do [ $((now - t)) -lt 3600 ] && recent="$recent $t"; done
  DEPLOY_TIMES="$recent"
  if [ "$(echo $DEPLOY_TIMES | wc -w)" -ge "$MAX_DEPLOYS_PER_HOUR" ]; then
    log "deploy cap reached ($MAX_DEPLOYS_PER_HOUR/hour) - not redeploying; reports are being lost until this is looked at"
    BACKOFF=$((now + 900)); return 1
  fi

  log "tunnel hostname changed -> telling Vercel ($u)"
  DEPLOY_TIMES="$DEPLOY_TIMES $now"
  if ! ( cd site && printf '%s' "$u" | vercel env add CANARY_INGEST_URL production --force >/dev/null 2>&1 ) \
     || ! deploy_head; then
    log "vercel update FAILED - backing off 5 minutes"; BACKOFF=$((now + 300)); return 1
  fi
  if path_ok; then
    echo "$u" > "$STATE"; BACKOFF=0; log "collection path verified end to end"
  else
    log "vercel updated but the end-to-end probe did not land in the ledger - backing off 5 minutes"
    BACKOFF=$((now + 300)); return 1
  fi
}

log "keep_alive started (ledger: $CANARY_DB, public: $PUBLIC)"
while true; do
  ensure_flask && ensure_tunnel && sync_vercel
  sleep "$INTERVAL"
done
