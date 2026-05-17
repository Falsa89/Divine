#!/bin/bash
# OPS-C-SUPERVISOR-WIRING — Apply script (SAFE, with backup + rollback).
#
# Behavior:
#   1. Take a timestamped backup of /etc/supervisor/conf.d/.
#   2. Copy /app/ops/supervisor_startup_check_snippet.conf to
#      /etc/supervisor/conf.d/startup_check.conf (only if absent or
#      content-divergent).
#   3. supervisorctl reread && supervisorctl update.
#   4. Verify [program:startup_check] is registered AND [program:expo]
#      and [program:backend] still appear in `supervisorctl status`.
#   5. If verification fails, automatically invoke the rollback script.
#
# This script does NOT run during V10 unless the user explicitly invokes
# it (V10 acceptance allows "ready_not_applied").
set -euo pipefail

SRC=/app/ops/supervisor_startup_check_snippet.conf
DST=/etc/supervisor/conf.d/startup_check.conf
BACKUP_DIR=/app/backups/supervisor
ROLLBACK=/app/ops/rollback_supervisor_startup_check_wiring.sh
TS=$(date -u +%Y%m%dT%H%M%SZ)

if [ ! -f "$SRC" ]; then
  echo "[OPS-C-SUP] FATAL: source snippet missing: $SRC" >&2
  exit 2
fi

mkdir -p "$BACKUP_DIR"
cp -rp /etc/supervisor/conf.d "$BACKUP_DIR/conf.d.$TS"
echo "[OPS-C-SUP] backup taken at $BACKUP_DIR/conf.d.$TS"

if [ -f "$DST" ] && cmp -s "$SRC" "$DST"; then
  echo "[OPS-C-SUP] $DST already matches source; skipping copy."
else
  cp "$SRC" "$DST"
  echo "[OPS-C-SUP] copied $SRC -> $DST"
fi

supervisorctl reread
supervisorctl update
sleep 2

# Verify
if ! supervisorctl status startup_check >/dev/null 2>&1; then
  echo "[OPS-C-SUP] FATAL: startup_check not registered after update. Rolling back." >&2
  bash "$ROLLBACK" || true
  exit 3
fi
for prog in backend expo; do
  if ! supervisorctl status "$prog" | grep -qE 'RUNNING|STARTING'; then
    echo "[OPS-C-SUP] FATAL: $prog NOT running after update. Rolling back." >&2
    bash "$ROLLBACK" || true
    exit 4
  fi
done

echo "[OPS-C-SUP] startup_check oneshot wired successfully."
supervisorctl status startup_check backend expo || true
