# Redis Rate-Limit Recovery — Ops Runbook (V25)

This directory contains **idempotent** scripts to recover the Redis backend
that powers `/api/affinity/gift-spend` rate-limiting in Stage 4 Internal Beta.

## Files

| File | Purpose |
|---|---|
| `ensure_redis_rate_limit.sh` | Full-stack recovery: install (if missing) + supervisor conf + start + PONG + backend verify |
| `restore_redis_supervisor_service.sh` | Restore only the supervisor program entry |

## Usage

```bash
# Standard recovery (idempotent — safe to call many times)
bash /app/ops/ensure_redis_rate_limit.sh

# Only re-write supervisor entry
bash /app/ops/restore_redis_supervisor_service.sh
```

## Safety guarantees

- **No DB mutation** — these scripts touch no MongoDB collection.
- **No broad rollout** — feature flags are untouched.
- **No code changes** — `affinity_gift_spend.py`, `battle_engine.py`, `combat.tsx` untouched.
- **Borea safety preserved** — recovery does NOT modify hero hidden list.

## Recovery flow

```
  ┌──────────────────────────────┐
  │ ensure_redis_rate_limit.sh  │
  └────────────┬─────────────────┘
               │
     ┌─────────▼─────────┐
     │ supervisorctl OK? │── no ──▶ exit 2
     └─────────┬─────────┘
               │ yes
     ┌─────────▼─────────┐
     │ redis-server bin? │── no ──▶ apt-get install ─┐
     └─────────┬─────────┘                            │
               │ yes                                  │
     ┌─────────▼─────────────────────────────────────▼┐
     │ /etc/supervisor/conf.d/redis.conf present?     │── no ──▶ write conf + reread + update
     └─────────┬───────────────────────────────────────┘
               │
     ┌─────────▼─────────┐
     │ redis RUNNING?    │── no ──▶ supervisorctl start redis
     └─────────┬─────────┘
               │
     ┌─────────▼─────────┐
     │ PONG (5x retry)   │── no ──▶ exit 3
     └─────────┬─────────┘
               │ yes
     ┌─────────▼──────────────────────────────────────┐
     │ verify canary-status rate_limit_backend=redis  │
     └─────────┬──────────────────────────────────────┘
               │
               ▼
            exit 0
```

## Failure modes addressed

- Container restart → binary disappears (observed in V24)
- Supervisor conf wiped
- Redis process crash
- Manual stop

## Closes

- **BLK-B-01** (ephemeral container Redis init/restore)
- **BLK-D-01** (Redis restart runbook)
