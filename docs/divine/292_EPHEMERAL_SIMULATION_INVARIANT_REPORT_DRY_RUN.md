# 292 — Ephemeral Simulation Invariant Report (DRY-RUN)

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_14_EPHEMERAL_SIMULATION_INVARIANT_REPORT_AND_STAGING_DB_BLUEPRINT_PACK_v50`
**Track**: A
**Public Sync Tag**: `PUBLIC_SYNC_TAG_v50_MEGA_ECONOMY_SAFETY_ACCELERATION_14`
**Contract version**: `economy_ephemeral_simulation_invariant_report_dry_run_v1`

## Scopo
Aggregare un report di invarianti deterministico sopra il simulatore ephemeral v49
(`economy_ephemeral_test_db_live_simulation_dry_run.py`) e dimostrare che, eseguendo
**8 famiglie × 9 scenari = 72 scenari** in memoria, **nessuna mutazione reale** di
database, filesystem, ambiente o rete avviene a runtime.

## Utility
- `backend/utils/economy_ephemeral_simulation_invariant_report_dry_run.py`
- API pubblica:
  - `build_invariant_report() -> dict` — esegue il full pre-flight v49 e produce il report.
  - `build_config_block() -> dict` — blocco di configurazione (no I/O).
  - `_test_reset() -> None` — reset dello stato del simulatore v49 (hook per i validator).

## Invarianti hard (devono valere SEMPRE)
- `real_db_writes == 0`
- `production_db_touched == False`
- `mongo_url_used == False`
- `pymongo_used == False`
- `motor_used == False`
- `env_read == False`
- `filesystem_writes == 0`
- `live_apply_allowed == False`
- `live_enforcement_enabled == False`
- `preview_request_blocked == False`
- `persisted == False`
- `no_route_exposure == True`
- `no_server_py_change == True`
- `total_simulated_ephemeral_writes_count > 0` (i write fittizi in-memory devono accadere)
- `scenarios_evaluated == 72`
- `all_invariants_ok == True`

## Vincoli di sicurezza
- NIENTE route, NIENTE wire-up in `server.py`, NIENTE modifiche al frontend.
- NIENTE import di `pymongo`, `motor`, `redis`.
- NIENTE `os.environ`, `os.getenv`, `load_dotenv`.
- NIENTE filesystem write (`open(..., 'w'|'a')` proibito).
- NIENTE connessione reale a MongoDB, Redis o servizi esterni.
- PII safe: `raw_payload_captured == False`.

## Stato
- `dry_run_only = True`
- `db_writes = 0`
- `real_db_writes = 0`
- `live_apply_allowed = False`
- `live_enforcement_enabled = False`
