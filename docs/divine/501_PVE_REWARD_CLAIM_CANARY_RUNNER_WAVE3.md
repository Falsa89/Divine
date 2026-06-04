# 501 — PvE Reward Claim Canary Runner Wave-3 Mode (v81)

## Nuovi CLI
- `--wave3-preflight`
- `--wave3-apply` (richiede `PVE_REWARD_CLAIM_CANARY_MODE=LOCAL_FILE_STAGING` e `PVE_REWARD_CLAIM_CANARY_WAVE3=YES_I_UNDERSTAND`)
- `--wave3-observe`
- `--wave3-rollback-drill`

## Garanzie
- Compat v78/v79/v80 preservata
- Nessun import di `pymongo`, `motor`, `redis`, `MONGO_URL`, `battle_engine`, `server`
- Scrive **solo** sotto `/app/data/canary_staging/wave3_*`
- Max 5 utenti, 1 claim per utente, 5 totali
- Reject obbligatori: duplicate replay (idempotent), duplicate conflict, non_allowlisted, premium, over_cap, **malformed_route**
