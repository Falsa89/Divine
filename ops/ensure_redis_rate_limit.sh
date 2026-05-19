#!/usr/bin/env bash
# ULTRA-COMBO V25 — Idempotent Redis rate-limit ensure script.
# Closes BLK-B-01 (ephemeral container Redis init/restore).
#
# Safe-by-design:
#   • NO database mutation.
#   • NO broad rollout, NO public UI.
#   • Multiple runs are no-ops if everything is already healthy.
#   • Reinstall redis-server via apt only when binary is missing.
#
# Exit codes:
#   0 = healthy (or made healthy)
#   1 = environment lacks apt (cannot self-heal) — manual intervention required
#   2 = supervisor not available
#   3 = redis still down after all attempts
set -u

log() { echo "[ensure-redis-rl] $*"; }

# 1. Detect supervisor
if ! command -v supervisorctl >/dev/null 2>&1; then
  log "ERROR: supervisorctl not found"
  exit 2
fi

# 2. Detect redis-server binary; install if missing
if ! command -v redis-server >/dev/null 2>&1; then
  log "redis-server binary missing — attempting idempotent install"
  if command -v apt-get >/dev/null 2>&1; then
    DEBIAN_FRONTEND=noninteractive apt-get install -y redis-server >/dev/null 2>&1 || {
      log "apt-get install failed"; exit 1; }
  else
    log "ERROR: no apt-get; cannot self-heal in this environment"
    exit 1
  fi
else
  log "redis-server already present: $(command -v redis-server)"
fi

# 3. Detect supervisor redis conf
CONF=/etc/supervisor/conf.d/redis.conf
if [ ! -f "$CONF" ]; then
  log "WARN: $CONF missing — writing safe default"
  cat > "$CONF" <<'EOC'
[program:redis]
command=/usr/bin/redis-server --port 6379 --bind 127.0.0.1 --protected-mode no --save "" --appendonly no
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/redis.err.log
stdout_logfile=/var/log/supervisor/redis.out.log
user=root
priority=5
EOC
  supervisorctl reread >/dev/null 2>&1
  supervisorctl update >/dev/null 2>&1
fi

# 4. Ensure supervisor redis is RUNNING (idempotent)
STATUS=$(supervisorctl status redis 2>/dev/null | awk '{print $2}')
log "current supervisor redis status: ${STATUS:-UNKNOWN}"
case "$STATUS" in
  RUNNING) : ;;
  STARTING) sleep 2 ;;
  STOPPED|EXITED|FATAL|BACKOFF|""|UNKNOWN)
    log "starting redis via supervisor"
    supervisorctl start redis >/dev/null 2>&1 || true
    sleep 2
    ;;
esac

# 5. Verify PONG
for i in 1 2 3 4 5; do
  if redis-cli ping 2>/dev/null | grep -q PONG; then
    log "PONG attempt=$i"
    PONG_OK=1
    break
  fi
  sleep 1
done
if [ -z "${PONG_OK:-}" ]; then
  log "ERROR: Redis still unreachable after retries"
  exit 3
fi

# 6. Verify backend canary-status backend=redis (best-effort, optional)
BACKEND_RL=$(curl -s --max-time 3 http://localhost:8001/api/affinity/gift-spend/canary-status 2>/dev/null | python3 -c 'import sys,json
try: d=json.load(sys.stdin); print(d.get("rate_limit_backend","-"))
except Exception: print("-")' 2>/dev/null || echo '-')
log "backend rate_limit_backend=$BACKEND_RL"

log "OK — Redis rate-limit operational"
exit 0
