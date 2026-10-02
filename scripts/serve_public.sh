#!/usr/bin/env bash
# Put the canary surface on the public internet, free, in one command.
#
#   bash scripts/serve_public.sh
#
# Starts the Flask surface and a Cloudflare quick tunnel, then prints the public
# HTTPS hostname. No Cloudflare account, no DNS, no certificate, no cost.
#
# Why a tunnel rather than a host: the ledger is append-only SQLite and must
# survive for hours while crawlers arrive. Keeping it on this machine means the
# bundle a judge verifies offline is byte-identical to the one that collected the
# evidence - see docs/memory/decisions/ADR-0005. The cost is that the surface is
# only reachable while this process runs.
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-python3}"
PORT="${PORT:-8000}"
CF="${CF:-$HOME/.local/bin/cloudflared}"

command -v "$CF" >/dev/null 2>&1 || [ -x "$CF" ] || {
  echo "cloudflared not found at $CF"
  echo "  curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o ~/.local/bin/cloudflared && chmod +x ~/.local/bin/cloudflared"
  exit 1; }

# --- the salt ---------------------------------------------------------------
# The server refuses to start on the development salt, because that salt is
# committed in a public repository and serving on it would let any reader forge a
# secret. Generate a real one once and keep it out of git.
if [ -f .env ]; then set -a; . ./.env; set +a; fi
if [ -z "${CANARY_SALT:-}" ]; then
  CANARY_SALT="$("$PY" -c 'import secrets;print(secrets.token_hex(32))')"
  echo "CANARY_SALT=$CANARY_SALT" >> .env
  echo "generated a new CANARY_SALT and appended it to .env (gitignored)."
  echo "KEEP IT: rotating it mid-run orphans every secret already issued."
  export CANARY_SALT
fi

export CANARY_DB="${CANARY_DB:-$PWD/canary.sqlite3}"
echo "ledger: $CANARY_DB"

cleanup() { kill "${APP_PID:-}" "${TUN_PID:-}" 2>/dev/null; }
trap cleanup EXIT INT TERM

"$PY" -m canarymaze.app > .serve.log 2>&1 &
APP_PID=$!
sleep 2
if ! kill -0 "$APP_PID" 2>/dev/null; then
  echo "the surface failed to start:"; tail -20 .serve.log; exit 1
fi
curl -fsS "http://127.0.0.1:$PORT/robots.txt" >/dev/null || { echo "surface not answering on :$PORT"; tail -20 .serve.log; exit 1; }
echo "surface up on :$PORT"

"$CF" tunnel --url "http://127.0.0.1:$PORT" --no-autoupdate > .tunnel.log 2>&1 &
TUN_PID=$!

echo -n "waiting for the tunnel hostname"
URL=""
for _ in $(seq 1 40); do
  URL=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' .tunnel.log 2>/dev/null | head -1)
  [ -n "$URL" ] && break
  echo -n "."; sleep 1
done
echo
[ -z "$URL" ] && { echo "no tunnel hostname appeared; see .tunnel.log"; tail -20 .tunnel.log; exit 1; }

cat <<EOF

  PUBLIC SURFACE:  $URL

  sitemap:  $URL/sitemap.xml
  robots:   $URL/robots.txt   (Disallow nothing - we are measuring what clients
                               do when they are NOT blocked)

  Next, to give crawlers a reason to arrive:
    1. paste $URL/sitemap.xml into a public model product and ask it to read a page
    2. run:  python3 scripts/trigger_paste.py $URL

  Leave this running. Ctrl-C stops the surface and the tunnel; the ledger and any
  bundle you have already exported survive, because they are files.

EOF
wait
