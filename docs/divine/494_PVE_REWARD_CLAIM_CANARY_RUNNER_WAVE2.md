# 494 — PvE Reward Claim Canary Runner Wave-2 Mode (v80)

## Nuovi CLI nel runner v1
- `--wave2-preflight`
- `--wave2-apply` (richiede env `PVE_REWARD_CLAIM_CANARY_MODE=LOCAL_FILE_STAGING`
  e `PVE_REWARD_CLAIM_CANARY_WAVE2=YES_I_UNDERSTAND`)
- `--wave2-observe`
- `--wave2-rollback-drill`

## Garanzie
- comportamento v78 (default) e v79 (local staging) **preservato**
- nessun import di `pymongo`, `motor`, `redis`, `MONGO_URL`
- nessun import di `battle_engine`, `server`, `story`, `combat`
- nessuna registrazione di route backend
- scrive **solo** file sotto `/app/data/canary_staging/wave2_*`
- max 3 utenti applicati, max 3 claim totali, 1 per utente

## Output JSON
- `pve_reward_claim_canary_wave2_preflight_result_v1.json`
- `pve_reward_claim_canary_wave2_apply_or_blocked_result_v1.json`
- `pve_reward_claim_canary_wave2_apply_result_v1.json`
- `pve_reward_claim_canary_wave2_ledger_snapshot_v1.json`
- `pve_reward_claim_canary_wave2_replay_negative_test_result_v1.json`
- `pve_reward_claim_canary_wave2_observation_result_v1.json`
- `pve_reward_claim_canary_wave2_rollback_drill_result_v1.json`
