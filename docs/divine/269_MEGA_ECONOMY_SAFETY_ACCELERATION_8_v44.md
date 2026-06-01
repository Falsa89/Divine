# 269 — MEGA_ECONOMY_SAFETY_ACCELERATION_8 v44 · Rollup

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_8_CLIENT_KEY_BUFFER_AND_CANARY_REHEARSAL_PACK_v44`  
**Modalità**: DRY_RUN_RUNTIME_INSTRUMENTATION_NO_LIVE_APPLY  
**Runtime activation**: `false` · **DB writes**: `0`

## Tracce

- **Track A** — client-key replay detection utility + wire-up 8 route + envelope/config + validator + doc 266
- **Track B** — observability buffer peek utility + wire-up 8 route + nuovo endpoint `/peek-buffer` (gated) + validator + doc 267
- **Track C** — material_raid canary QA rehearsal design-only + validator + doc 268
- **Track D** — 4 tuple OPTIONAL count=1 nel suite runner + public sync tag

## Suite tuples

- `PROJECT-CLIENT-IDEM-KEY-REPLAY-DETECTION-DRY-RUN`
- `PROJECT-OBSERVABILITY-BUFFER-PEEK-DRY-RUN`
- `PROJECT-MATERIAL-RAID-CANARY-QA-REHEARSAL-DRY-RUN`
- `MEGA-ECONOMY-SAFETY-ACCELERATION-8-v44-ROLLUP`

Public sync tag: `PUBLIC_SYNC_TAG_v44_MEGA_ECONOMY_SAFETY_ACCELERATION_8`.

## Invarianti

- 5 file core MD5-locked invariati
- v42/v43 utils bit-identici
- 8/8 route: esistenti endpoint path/feature flag/default 503/safety_flags invariati
- 8/8 route: nuovo `/peek-buffer` endpoint **aggiunto** (non sostituisce nulla, gated dallo stesso flag)
- `server.py` non modificato
- v42 request_hash + observability envelope intatti
- v43 server-key replay envelope intatto
- DB writes totali = 0
- preview request mai bloccato
- canary pilot signoff = pending

## Verdict locale atteso

```
MEGA_ECONOMY_SAFETY_ACCELERATION_8_CLIENT_KEY_BUFFER_AND_CANARY_REHEARSAL_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```
