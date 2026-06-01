# 267 — Observability Buffer Peek Dry-Run

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_8_..._v44` · Track B  
**Modalità**: DRY_RUN_RUNTIME_INSTRUMENTATION_NO_LIVE_APPLY

## Scopo

Ring buffer in-memory che accumula i preview di audit_event + metric_sample
per debug delle route safety. PII-safe (mai raw payload / email / IP / device).

## Storage

- max 100 entries **per operation_family**
- TTL 300s
- non condivisa tra worker, non durable su restart
- no DB, no Redis, no filesystem

## Nuovo endpoint per ogni route

`GET /api/<route>/peek-buffer?limit=25` — read-only:

- flag OFF → `HTTP 503` (verificato per tutte le 8 route)
- flag ON → ritorna `buffer.sizes_by_family` + `buffer.entries_by_family`
  (PII-safe, no raw payload)

Nessun **reset** endpoint esposto pubblicamente.

## Smoke

- 3 POST consecutivi su Material Raid → `peek-buffer` ritorna 3 entry ✅
- nessun campo PII presente (email/ip/device_id/etc tutti scrubbed)
- `db_writes=0`, `pii_safe=true`, `not_durable_across_restart=true`
