#!/usr/bin/env bash
# ULTRA-COMBO V25 — Restore the Redis supervisor service entry (idempotent).
# Used when only the supervisor conf is missing/stale but the binary is fine.
set -u
CONF=/etc/supervisor/conf.d/redis.conf
if [ ! -f "$CONF" ]; then
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
  echo "[restore] supervisor conf written"
else
  echo "[restore] supervisor conf already present"
fi
supervisorctl reread >/dev/null 2>&1
supervisorctl update >/dev/null 2>&1
supervisorctl start redis >/dev/null 2>&1 || true
sleep 1
supervisorctl status redis
exit 0
