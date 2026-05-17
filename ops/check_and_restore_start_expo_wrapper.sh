#!/bin/bash
# OPS-C — Auto-restore + health-check hook for /usr/local/bin/start-expo.sh.
# Idempotent. Safe to run any number of times. Does NOT modify app logic.
#
# Behavior:
# 1. If /usr/local/bin/start-expo.sh is missing or different from the
#    persistent copy under /app/ops/start-expo.sh, restore it.
# 2. If supervisor is available, reread / update / start expo.
# 3. Probe http://127.0.0.1:3000 and print the HTTP code.
#
# Usage: bash /app/ops/check_and_restore_start_expo_wrapper.sh
set -e
SRC=/app/ops/start-expo.sh
DST=/usr/local/bin/start-expo.sh

if [ ! -f "$SRC" ]; then
  echo "[OPS-C] FATAL: persistent wrapper $SRC missing." >&2
  exit 1
fi

restore_needed=0
if [ ! -f "$DST" ]; then
  restore_needed=1
elif ! cmp -s "$SRC" "$DST"; then
  restore_needed=1
fi

if [ "$restore_needed" = "1" ]; then
  echo "[OPS-C] wrapper missing or drifted; restoring $SRC -> $DST"
  cp "$SRC" "$DST"
  chmod +x "$DST"
else
  echo "[OPS-C] wrapper already aligned: $DST"
fi

if command -v supervisorctl >/dev/null 2>&1; then
  status=$(supervisorctl status expo 2>/dev/null | awk '{print $2}')
  if [ "$status" != "RUNNING" ]; then
    echo "[OPS-C] expo status: $status; performing reread/update/start"
    supervisorctl reread >/dev/null 2>&1 || true
    supervisorctl update >/dev/null 2>&1 || true
    supervisorctl start expo >/dev/null 2>&1 || true
    sleep 4
  fi
  supervisorctl status expo 2>/dev/null || true
fi

if command -v curl >/dev/null 2>&1; then
  code=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3000 || true)
  echo "[OPS-C] frontend localhost:3000 -> HTTP $code"
fi

echo "[OPS-C] check done."
