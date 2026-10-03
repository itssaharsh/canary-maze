#!/usr/bin/env bash
# Deploy exactly what is committed under site/ - never the working tree.
#
# `git archive` cannot see uncommitted files, so an edit in progress, or a landing
# page built from a test fixture, cannot reach production. The watchdog used to
# run `vercel deploy` in site/ as it sat on disk.
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git diff --quiet HEAD -- site; then
  echo "note: site/ has uncommitted changes; they are NOT being deployed" >&2
fi
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
git archive HEAD site | tar -x -C "$tmp"
cp -r site/.vercel "$tmp/site/.vercel"
( cd "$tmp/site" && vercel deploy --prod --yes ) 2>&1 | grep -oE 'https://[a-z0-9-]+\.vercel\.app' | tail -1
