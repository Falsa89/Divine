#!/bin/bash
# OPS-B — Persistent repo copy of the Expo wrapper.
# /usr/local/bin/start-expo.sh is restored from this file by
# /app/ops/restore_start_expo_wrapper.sh.
# Kept ALIGNED with OPS-A audit: HMR preserved (no environment override).
set -e
cd /app/frontend
fuser -k 3000/tcp 2>/dev/null || true
pkill -9 -f "expo start" 2>/dev/null || true
pkill -9 -f "metro" 2>/dev/null || true
sleep 1
export NODE_OPTIONS="--max-old-space-size=4096"
export EXPO_NO_TELEMETRY=1
exec npx expo start --port 3000
