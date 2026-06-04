# 508 — PvE Reward Claim Canary Runner Wave-4 Mode (v82)

## Nuovi CLI
- `--wave4-preflight`
- `--wave4-apply` (richiede `PVE_REWARD_CLAIM_CANARY_MODE=LOCAL_FILE_STAGING` + `PVE_REWARD_CLAIM_CANARY_WAVE4=YES_I_UNDERSTAND`)
- `--wave4-observe`
- `--wave4-rollback-drill`

## Garanzie
- Compat v78–v81 preservata
- Nessun import `pymongo`/`motor`/`redis`/`MONGO_URL`/`battle_engine`/`server`
- Scrive solo `/app/data/canary_staging/wave4_*`
- Max 8 utenti, 1 claim/utente, 8 totali
- Reject obbligatori: duplicate replay (idempotent), duplicate conflict, non_allowlisted,
  premium, over_cap, malformed_route, **event_arena_ranking_reward**
- Nuova `FORBIDDEN_REWARD_KEYS_WAVE4` include `arena_ranking_reward`
