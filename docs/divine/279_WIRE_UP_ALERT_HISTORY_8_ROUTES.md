# 279 — WIRE-UP ALERT HISTORY su 8 safety route (v47 Track B)

## Sintesi
Wire-up del contratto v47 alert history sulle 8 safety preview route.

## Modifiche per route
- `/config` espone `alert_history_dry_run` (config block)
- POST response includono `alert_history_record_dry_run` (entry_id_preview + recorded_overall_level + dispatched=false)
- `/peek-buffer` include `alert_history_snapshot` (windows + recent_entries + by_level counts)

## Invarianti rispettati
- NESSUN cambio endpoint path / feature flag / default 503 / safety flag
- NESSUN cambio `backend/server.py`
- NESSUN cambio frontend
- 0 DB writes, 0 Redis, 0 filesystem, 0 persistent ledger
- NO external alert dispatch (`alert_dispatched=false`, `alert_sink_live_enabled=false`)
- Preview request mai bloccata
