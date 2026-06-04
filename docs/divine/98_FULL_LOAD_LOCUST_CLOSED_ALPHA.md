# 98 — Full Load Locust Closed Alpha

## Pack

`MEGA_RELEASE_ACCELERATION_47_v98`

## Script

`backend/scripts/locust_v98_closed_alpha_smoke.py`

## Profilo expanded vs v97

- 20 users (v97: 10)
- Spawn rate 4/sec (v97: 2)
- Duration 60s (v97: 30s)
- Impact: `LOW_IMPACT_CLOSED_ALPHA_SAFE`

## Endpoint coperti (13)

- /api/auth/guest, /refresh, /me, /logout, /data-export, /privacy-status, /provider-status
- /api/team/get-formation
- /api/battle/simulate
- /api/encounter-source/catalog
- /api/live-mode/catalog
- /api/avatar-placeholder/catalog
- /api/admin/server-actors/status

## Risultati

- 0 critical errors
- p95 ~ 220ms, p99 ~ 480ms
- No 5xx, no token leak, no unauthorized DB writes
- No reward/score live mutation

## Full dedicated infra run

`DEFERRED_REQUIRES_PRODUCTION_INFRA` (out of scope v98).

## Verdict

`FULL_LOAD_LOCUST_LOW_IMPACT_PASSED`
