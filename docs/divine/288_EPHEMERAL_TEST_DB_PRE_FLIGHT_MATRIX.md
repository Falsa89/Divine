# 288 — EPHEMERAL_TEST_DB_PRE_FLIGHT_MATRIX (v49 Track B)

## Sintesi
Matrice design-only pre-flight per il live simulation su DB effimero.

## Stato globale
- `real_db_connection_allowed=false`, `mongo_url_allowed=false`, `pymongo_allowed=false`, `motor_allowed=false`
- `env_read_allowed=false`, `filesystem_writes_allowed=false`
- `production_db_touched=false`
- `ephemeral_db_required=true`, `rollback_simulation_required=true`
- `live_enabled=false`, `safe_to_enable_live=false`
- `db_writes=0`, `real_db_writes=0`

## Famiglie (8/8)
Per ogni famiglia: stessi flag + `required_collections` (incluso sempre `idempotency_ledger` e `audit_log`).
- BP +`no_bp_delta_runtime=true`; Mail +`no_mail_state_mutation=true`.

## Blockers globali (10)
Incluso `real_db_connection_forbidden_at_runtime`, `mongo_url_must_not_be_read`, `pymongo_must_not_be_imported`, ecc.
