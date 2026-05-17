#!/bin/bash
# OPS-C-WIRING — boot startup check. Calls check_and_restore safely.
# Idempotent. No app runtime mutation.
set -e
HOOK=/app/ops/check_and_restore_start_expo_wrapper.sh
if [ -x "$HOOK" ]; then
  bash "$HOOK" || true
else
  echo "[OPS-C-WIRING] hook not present: $HOOK" >&2
fi
echo "[OPS-C-WIRING] startup_check done."
