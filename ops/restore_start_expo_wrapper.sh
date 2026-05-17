#!/bin/bash
# OPS-B — Restore /usr/local/bin/start-expo.sh from the persistent
# repo copy /app/ops/start-expo.sh, then reload supervisor.
# Idempotent. Safe to run any time the wrapper is missing.
set -e
SRC=/app/ops/start-expo.sh
DST=/usr/local/bin/start-expo.sh

if [ ! -f "$SRC" ]; then
  echo "FATAL: persistent wrapper $SRC missing." >&2
  exit 1
fi

echo "[OPS-B] copying $SRC -> $DST"
cp "$SRC" "$DST"
chmod +x "$DST"
ls -la "$DST"

echo "[OPS-B] supervisor reread / update / restart expo"
if command -v supervisorctl >/dev/null 2>&1; then
  supervisorctl reread || true
  supervisorctl update || true
  supervisorctl restart expo || supervisorctl start expo || true
  sleep 5
  supervisorctl status expo || true
fi

if command -v curl >/dev/null 2>&1; then
  code=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3000 || true)
  echo "[OPS-B] frontend localhost:3000 -> HTTP $code"
fi

echo "[OPS-B] restore done."
