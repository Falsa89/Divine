# 274 — TELEMETRY_ALERTING_THRESHOLDS_DRY_RUN (v46 Track A)

## Sintesi
Utility dry-run che valuta uno snapshot v45 (rolling window 60s) e produce
una classificazione alert (ok/warn/critical). NESSUN sink esterno, NESSUN
dispatch, NESSUNA persistenza.

## Soglie
- replay_rate: warn >= 0.20, critical >= 0.50
- conflict_rate: warn >= 0.05, critical >= 0.15
- missing_key_rate: warn >= 0.10, critical >= 0.25

## Critical immediate (forza critical indipendentemente dai rate)
- `db_writes_observed_total > 0`
- `reward_grants_observed_total > 0`
- `mutation_observed_total > 0`
- `bp_delta_observed_total > 0`
- `live_enforcement_observed_total > 0`

## API pubblica
- `evaluate_alerts_from_snapshot(snapshot) -> dict`
- `build_alerting_thresholds_config() -> dict`
- `_test_reset() -> None` (solo per validator)

## Garanzie strict
- `alert_sink_live_enabled=false`, `alert_dispatched=false`, `external_sink_used=false`
- `db_writes=0`, `persisted=false`, `live_enforcement_enabled=false`, `preview_request_blocked=false`
- NO DB / Redis / filesystem / persistent ledger
- PII-safe; non consuma raw payload

## Wire-up sulle 8 route
- `/config` espone `alerting_thresholds_dry_run`
- POST response include `telemetry_alert_evaluation_dry_run`
- `/peek-buffer` include `alert_evaluation`
