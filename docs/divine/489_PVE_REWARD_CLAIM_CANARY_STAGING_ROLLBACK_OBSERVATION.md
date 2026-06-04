# 489 — PvE Reward Claim Canary Staging Rollback & Observation (v79)

## Rollback drill (file-only)
- Comando: `python3 backend/scripts/pve_reward_claim_canary_runner_v1.py --local-rollback-drill`
- Esito: 1 transazione canary rolled-back
- `db_rollback = false`, `db_writes = 0`
- Token segnato come `used`, entry ledger flaggato `rolled_back=true` con timestamp

## Observation
- Fonte: `/app/data/canary_staging/observation_log_v1.json`
- Finestra: 60 minuti
- Metriche raccolte:
  - `local_claim_attempts_total = 3`
  - `local_claim_success_total = 1`
  - `local_claim_reject_total = 2`
  - `premium_reward_reject_total = 1`
  - `non_allowlisted_reject_total = 1`
  - `duplicate_conflict_total = 0`
  - `db_write_total = 0`
  - `live_reward_grant_total = 0`
  - `rollback_required_total = 1`
  - `error_total = 0`

## Wave2 gate
- `wave2_gate_ready = true` (local_apply clean + rollback drill + observation pass)
