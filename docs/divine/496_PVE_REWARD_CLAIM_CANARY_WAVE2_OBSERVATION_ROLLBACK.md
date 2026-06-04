# 496 — PvE Reward Claim Canary Wave-2 Observation / Rollback (v80)

## Observation
Finestra: 60 minuti. Sorgente: `/app/data/canary_staging/wave2_observation_log_v1.json`.

Metriche raccolte:
- `wave2_claim_attempts_total = 8`
- `wave2_claim_success_total = 3`
- `wave2_claim_reject_total = 4`
- `idempotent_replay_total = 1`
- `duplicate_conflict_total = 1`
- `non_allowlisted_reject_total = 1`
- `over_cap_reject_total = 1`
- `premium_reward_reject_total = 1`
- `db_write_total = 0`
- `live_reward_grant_total = 0`
- `rollback_required_total = 1`
- `error_total = 0`

PASS criteria tutti soddisfatti:
- `db_write_total_zero` ✅
- `live_reward_grant_total_zero` ✅
- `premium_reward_reject_at_least_one` ✅
- `non_allowlisted_reject_at_least_one` ✅
- `over_cap_reject_at_least_one` ✅
- `no_critical_errors` ✅

## Rollback drill
- Policy: `sample_one_canary_tx`
- 1 tx rolled-back (campione)
- `db_rollback = false`, `db_writes = 0`

## Wave3 gate
- **`wave3_gate_ready = true`**
