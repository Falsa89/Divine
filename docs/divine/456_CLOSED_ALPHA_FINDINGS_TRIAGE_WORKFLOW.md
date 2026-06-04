# 456 — Closed Alpha Findings Triage Workflow (v75)

Pack: `MEGA_RELEASE_ACCELERATION_24_v75`

## Buckets

- P0: crash / data corruption / guardrail violation
- P1: flow blocker (non crash)
- P2: flow degraded ma completabile
- P3: polish/copy/layout non blocker

## SLA

- P0: 60 min
- P1: 1440 min (24h)
- P2: 4320 min (72h)
- P3: null (no SLA)

## Decision matrix

- P0 -> halt + rollback + escalate + hotfix plan
- P1 -> plan fix in v76 o earlier pack
- P2 -> plan fix in v76-v77 batch
- P3 -> aggregate in polish batch

Forbidden: public live ticketing, persistent app-side DB writes, automatic backend route creation, automated invites/notifications.

`db_writes=0`.
