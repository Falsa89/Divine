#!/bin/bash
# OPS-C-SUPERVISOR-WIRING — Rollback script.
# Removes /etc/supervisor/conf.d/startup_check.conf and reloads supervisor.
# Safe to run multiple times.
set -eu

DST=/etc/supervisor/conf.d/startup_check.conf

if [ -f "$DST" ]; then
  rm -f "$DST"
  echo "[OPS-C-SUP-RBK] removed $DST"
else
  echo "[OPS-C-SUP-RBK] $DST not present; nothing to remove."
fi

if command -v supervisorctl >/dev/null 2>&1; then
  supervisorctl reread || true
  supervisorctl update || true
  echo "[OPS-C-SUP-RBK] supervisor reloaded."
  supervisorctl status backend expo || true
fi

echo "[OPS-C-SUP-RBK] rollback complete."
