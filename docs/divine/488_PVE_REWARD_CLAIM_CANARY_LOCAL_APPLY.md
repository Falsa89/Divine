# 488 — PvE Reward Claim Canary Local Apply (v79)

## Esecuzione
```
PVE_REWARD_CLAIM_CANARY_APPLY=YES_I_UNDERSTAND \
PVE_REWARD_CLAIM_CANARY_MODE=LOCAL_FILE_STAGING \
python3 backend/scripts/pve_reward_claim_canary_runner_v1.py --local-apply
```

## Risultato
- `applied_to_local_staging = true`
- `applied_to_live = false`
- `db_writes = 0`
- `local_file_writes = 3` (in questa esecuzione di apply; rollback drill aggiunge ulteriori 3)
- `live_reward_grant = false`
- `verdict_local = PVE_REWARD_CLAIM_CANARY_LOCAL_STAGING_APPLIED_SAFE`

## Negative tests inclusi
- Premium currency in payload → reject `forbidden_reward_type:premium_currency`
- Utente non in allowlist (`intruder_user_999`) → reject `non_allowlisted_user`

## Happy path
- 1 entry ledger per `canary_user_001` (route `story_alpha_slice_preview`)
- Reward: `gold=100, account_exp=10, hero_exp=20, basic_material=1` (sotto cap)
- Token rollback emesso
