# 481 — PvE Reward Claim Canary Runner v1

## Script
`backend/scripts/pve_reward_claim_canary_runner_v1.py`

## Comportamento
- **Default**: dry-run + scrittura `apply_or_blocked` result (in stato attuale → BLOCKED).
- `--apply` consentito **solo** se:
  - `/app/data/canary_staging` esiste
  - env `PVE_REWARD_CLAIM_CANARY_APPLY=YES_I_UNDERSTAND`
  - tutti i design artifact (contract, scope_lock, idempotency, ledger, rollback,
    observation, kill_switch) sono presenti

## Output prodotti
- `data/design/economy/pve_reward_claim_canary_dry_run_result_v1.json`
- `data/design/economy/pve_reward_claim_canary_apply_or_blocked_result_v1.json`

## Esecuzione attuale (v78)
- Gate 0: `staging_dir_exists=false`, `apply_flag_present=false`
- Verdetto runner: `PVE_REWARD_CLAIM_CANARY_BLOCKED_NOT_APPLIED_SAFE`
- `applied=false`, `db_writes=0`
- Nessun import di `battle_engine`, `server`, `story`, `combat`
