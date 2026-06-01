# 265 — MEGA_ECONOMY_SAFETY_ACCELERATION_7 v43 · Rollup

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_7_DRY_RUN_REPLAY_DETECTION_PACK_v43`  
**Modalità**: DRY_RUN_RUNTIME_INSTRUMENTATION_NO_LIVE_APPLY  
**Runtime activation**: `false`  
**DB writes**: `0`

## Tracce eseguite

- **Track A** — utility `economy_idempotency_replay_detection_dry_run.py` + validator
- **Track B** — wire-up nelle 8 safety preview route (3 endpoint POST + /config per ciascuna)
- **Track C** — design JSON + 2 doc (264 + 265) + rollup marker
- **Track D** — 2 tuple OPTIONAL count=1 nel suite runner + diag public sync tag

## Suite tuples aggiunte (2 OPTIONAL, count=1 ciascuna)

- `PROJECT-ECONOMY-IDEMPOTENCY-REPLAY-DETECTION-DRY-RUN`
- `MEGA-ECONOMY-SAFETY-ACCELERATION-7-v43-ROLLUP`

## Public sync tag

`PUBLIC_SYNC_TAG_v43_MEGA_ECONOMY_SAFETY_ACCELERATION_7`

## Invarianti

- 5 file core MD5-locked invariati
- v42 utils (`economy_request_hash_dry_run.py`, `economy_observability_dry_run.py`) bit-identici a v42
- 8/8 route con endpoint path invariati
- 8/8 route con feature flag invariati
- 8/8 route con default 503 invariato
- 8/8 route con `safety_flags` invariati
- `server.py` non modificato per v43
- v42 `request_hash_dry_run` + `observability_dry_run` envelope invariati
- v42c helper `_v42_operation_type` / `_v42_client_idempotency_key_present` ancora presenti in BP + Mail
- DB writes totali = 0
- live commit / live claim / reward grant = false
- preview request mai bloccato
- replay cache in-memory, TTL 60s, max 256, non-shared, non-durable

## Verdict locale atteso

```
MEGA_ECONOMY_SAFETY_ACCELERATION_7_DRY_RUN_REPLAY_DETECTION_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

## Caveat noti

- `SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION` accettato.
- 18 OPTIONAL fail attesi nella suite master. Nessun REQUIRED fail.
- `same_key_diff_hash_conflict_preview` non raggiungibile via HTTP con la
  derivazione idem key v42 attuale (la idem key dipende dal payload). L'utility
  lo gestisce correttamente in isolamento (verificato dal validator).
