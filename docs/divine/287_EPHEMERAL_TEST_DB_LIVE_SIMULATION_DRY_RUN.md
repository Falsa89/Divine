# 287 — EPHEMERAL_TEST_DB_LIVE_SIMULATION_DRY_RUN (v49 Track A)

## Sintesi
Utility in-memory che simula un DB **effimero** per le 8 operation families.
**NESSUNA** connessione reale: no `pymongo`, no `motor`, no `redis`, no `MONGO_URL`,
no `os.environ`/`getenv`/`load_dotenv`, no filesystem writes.

## Collections simulate (in-memory dict)
`users`, `user_materials`, `inventory`, `gear`, `runes`, `artifacts`,
`divine_weapons`, `battle_pass_claims`, `mail_claims`, `idempotency_ledger`, `audit_log`

## Scenari (9)
`happy_path`, `duplicate_same_hash`, `duplicate_diff_hash`, `missing_idempotency_key`,
`rollback_simulation`, `version_mismatch`, `unauthorized`, `audit_event`,
`no_production_db_touched`

## Garanzie strict
- `real_db_writes=0` SEMPRE
- `production_db_touched=false` SEMPRE
- `mongo_url_used=false`, `pymongo_used=false`, `motor_used=false`, `env_read=false`, `filesystem_writes=0`
- `live_apply_allowed=false`, `persisted=false`
- Tutte le scritture sono mock e contate in `simulated_ephemeral_writes_count`

## API
- `run_simulation_scenario(operation_family, scenario, payload)` -> dict
- `run_all_scenarios_for_family(operation_family)` -> dict
- `run_full_pre_flight()` -> dict (8 famiglie × 9 scenari)
- `build_config_block()` -> dict
- `_test_reset()` -> None
