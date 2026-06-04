# 487 — PvE Reward Claim Canary Runner — Local Staging Mode (v79)

## Patch al runner v78
`backend/scripts/pve_reward_claim_canary_runner_v1.py` esteso con:
- `--local-preflight`
- `--local-apply` (richiede env `PVE_REWARD_CLAIM_CANARY_APPLY=YES_I_UNDERSTAND`
  e `PVE_REWARD_CLAIM_CANARY_MODE=LOCAL_FILE_STAGING`)
- `--local-rollback-drill`

## Garanzie
- **Nessun import** di `battle_engine`, `server`, `story`, `combat`
- **Nessun import** di `pymongo`, `motor`, `redis`
- **Nessun uso** di `MONGO_URL`
- **Nessuna registrazione** di route backend
- Comportamento default (v78) **preservato**: dry-run + apply_or_blocked safe
- Local apply scrive solo file sotto `/app/data/canary_staging/`
- `db_writes` sempre `0`, `live_reward_grant` sempre `false`
