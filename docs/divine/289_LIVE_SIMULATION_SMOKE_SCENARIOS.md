# 289 — LIVE_SIMULATION_SMOKE_SCENARIOS (v49 Track C)

## Sintesi
8 famiglie × 9 scenari di smoke design-only per la simulazione live su DB effimero.
In ogni famiglia/scenario:
- `expected_real_db_writes=0`
- `expected_live_apply_allowed=false`
- `expected_production_db_touched=false`

## Scenari richiesti per famiglia
`happy_path`, `duplicate_same_hash`, `duplicate_diff_hash`, `missing_idempotency_key`,
`rollback_simulation`, `version_mismatch`, `unauthorized`, `audit_event`,
`no_production_db_touched`
