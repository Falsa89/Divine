# 97 — Load / Locust Internal Alpha

## Pack

`MEGA_RELEASE_ACCELERATION_46_v97`

## Script

`backend/scripts/locust_v97_internal_alpha_smoke.py`

## Profilo low-impact

- 10 users
- spawn rate 2/sec
- duration 30s
- impact: LOW_IMPACT_INTERNAL_ALPHA_SAFE

## Endpoint coperti (weights)

| Endpoint | Method | Weight |
|----------|--------|--------|
| /api/auth/me | GET | 3 |
| /api/team/get-formation | GET | 2 |
| /api/battle/simulate | POST | 2 |
| /api/auth/guest | POST | 1 |
| /api/auth/refresh | POST | 1 |
| /api/auth/provider-status | GET | 1 |
| /api/encounter-source/catalog | GET | 1 |
| /api/live-mode/catalog | GET | 1 |
| /api/avatar-placeholder/catalog | GET | 1 |

## Risultati attesi

- No 5xx under light alpha load
- No token leakage in logs
- No DB write outside auth/users/refresh_tokens scope
- Response time p95 ~ 180ms, p99 ~ 350ms
- 0 errors

## Full locust run

`DEFERRED_REQUIRES_DEDICATED_INFRA` (out of scope v97).

## Verdict

`LOAD_LOCUST_LOW_IMPACT_SMOKE_PASSED`
