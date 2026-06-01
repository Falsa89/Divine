# 270 — OBSERVABILITY_RING_BUFFER_AGGREGATION_DRY_RUN (v45 Track A)

## Sintesi
Utility in-memory, per-process, non durabile, per aggregare eventi telemetry
osservativi su rolling windows 60s / 300s / 900s. Solo summaries PII-safe.

## Garanzie strict
- NO DB writes. NO Redis. NO filesystem. NO persistent ledger.
- Non condivisa fra worker; non durabile fra restart.
- Solo summaries PII-safe (mai raw payload / PII / token / payment).
- 0 db_writes, persisted=false, live_enforcement_enabled=false.
- La preview request non viene MAI bloccata dalla telemetry.

## API pubblica
- `record_telemetry_event(operation_family, detection_statuses, route_name, ...)` -> str | None
- `build_aggregation_snapshot(operation_family=None)` -> dict
- `build_config_block()` -> dict
- `build_replay_conflict_telemetry_envelope(operation_family, detection_statuses, route_name)` -> dict
- `_test_reset()` (solo per validator)

## Capacità
- Ring buffer bounded: MAX_EVENTS=4096 (oldest evicted FIFO).
- Statuses tracciati (8): `new_key_preview`, `same_key_same_hash_replay_preview`,
  `same_key_diff_hash_conflict_preview`, `missing_key_preview`, `new_client_key_preview`,
  `same_client_key_same_hash_replay_preview`, `same_client_key_diff_hash_conflict_preview`,
  `missing_client_key_preview`.

## Tag
`PUBLIC_SYNC_TAG_v45_MEGA_ECONOMY_SAFETY_ACCELERATION_9`
