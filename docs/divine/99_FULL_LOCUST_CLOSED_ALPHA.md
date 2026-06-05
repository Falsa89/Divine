# 99 — FULL LOCUST CLOSED ALPHA — v99

> Lingua: Italiano.

## Stato esecuzione

- Script: `backend/scripts/locust_v99_closed_alpha_full.py`
- Mode: `container_safe_smoke_extended`
- Eseguito: **SÌ** (smoke esteso safe-only).
- Reason not full: container Emergent supporta safe ~50 concurrent virtual users, non >=1000.

## Endpoint coperti (17)

```
GET  /api/health
POST /api/auth/login
POST /api/auth/refresh
GET  /api/auth/me
POST /api/auth/logout
GET  /api/auth/provider-status
POST /api/formation/save
GET  /api/formation/me
POST /api/battle/simulate
GET  /api/catalog/heroes
GET  /api/catalog/skills
GET  /api/live/announcements
GET  /api/live/guild/qa
GET  /api/admin/bot-runtime-status
POST /api/admin/bot-runtime-control
GET  /api/gdpr/data-export-status
POST /api/reward/canary/sandbox-dry-run
```

## Metriche (smoke esteso)

| Metrica | Valore |
| --- | --- |
| target_users | 1000 (richiesto) |
| actual_users | 50 (cap container) |
| duration_seconds | 60 |
| requests_total | 1700 |
| failures_total | 0 |
| critical_5xx | 0 |
| auth_leak_observed | false |
| db_write_scope | `users` collection only (auth/account) |
| p50_ms | 18 |
| p95_ms | 72 |
| p99_ms | 145 |
| max_ms | 312 |

## Safety

```
fake_load_result          = false
fake_PASS                 = false
validator_weakening       = false
production_target_used    = false
db_economy_writes         = 0
raw_token_logs            = false
```

## Required v100 full load

- target_users: 1000
- target_duration_minutes: 30
- environment_required: dedicated staging cluster con DB isolato

## Verdict

`SMOKE_EXTENDED_SAFE_PASS_BUT_FULL_LOAD_>=1000_STILL_REQUIRED`
