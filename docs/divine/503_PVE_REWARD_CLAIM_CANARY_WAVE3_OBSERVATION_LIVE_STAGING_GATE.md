# 503 — PvE Reward Claim Canary Wave-3 Observation & Live-Staging Gate (v81)

## Observation
Finestra: 60 minuti. Sorgente: `/app/data/canary_staging/wave3_observation_log_v1.json`.

Metriche raccolte (post run):
- `wave3_claim_attempts_total = 11`
- `wave3_claim_success_total = 5`
- `wave3_claim_reject_total = 5`
- `idempotent_replay_total = 1`
- `duplicate_conflict_total = 1`
- `non_allowlisted_reject_total = 1`
- `over_cap_reject_total = 1`
- `premium_reward_reject_total = 1`
- `malformed_route_reject_total = 1`
- `db_write_total = 0`
- `live_reward_grant_total = 0`
- `rollback_required_total = 1`
- `error_total = 0`

PASS criteria (tutti 7 ✅):
- `db_write_total_zero`
- `live_reward_grant_total_zero`
- `premium_reward_reject_at_least_one`
- `non_allowlisted_reject_at_least_one`
- `over_cap_reject_at_least_one`
- `malformed_route_reject_at_least_one`
- `no_critical_errors`

## Rollback drill
- Policy: `sample_one_canary_tx`
- 1 tx rolled-back
- `db_rollback = false`, `db_writes = 0`

## Live-staging gate
- **`live_staging_gate_ready = true`**
- Significa: **eligible per future dedicated pack design-only**.
- NON significa live DB attivo. Nessuna scrittura su DB reale autorizzata.
