# 278 — ALERT_HISTORY_RING_BUFFER_DRY_RUN (v47 Track A)

## Sintesi
Utility in-memory, per-process, non durabile, che cattura ogni `alert_evaluation`
(v46) come entry PII-safe nel ring buffer.

## Capacità
- Buffer bounded: **MAX_ENTRIES=1024** (FIFO eviction)
- Rolling windows: **60s / 300s / 900s**

## API pubblica
- `record_alert_evaluation(operation_family, alert_evaluation, route_name)` -> str | None
- `peek_alert_history(operation_family=None, limit=25)` -> dict
- `build_config_block()` -> dict
- `build_alert_history_record_envelope(operation_family, alert_evaluation, route_name)` -> dict
- `_test_reset()` (solo per validator)

## Dati registrati (PII-safe)
- timestamp, family, route, overall_level, rates, critical_immediate_observed, alerts proiezione minima (metric/level/window)

## Garanzie strict
- 0 db_writes, persisted=false, alert_sink_live_enabled=false, alert_dispatched=false
- NO DB / Redis / filesystem / persistent ledger
- NO external alert dispatch
- Preview request **mai** bloccata
- raw_payload_captured=false, pii_safe=true
