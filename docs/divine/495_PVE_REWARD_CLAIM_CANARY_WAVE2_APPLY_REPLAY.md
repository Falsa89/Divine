# 495 — PvE Reward Claim Canary Wave-2 Apply / Replay (v80)

## Esecuzione
```
PVE_REWARD_CLAIM_CANARY_MODE=LOCAL_FILE_STAGING \
PVE_REWARD_CLAIM_CANARY_WAVE2=YES_I_UNDERSTAND \
python3 backend/scripts/pve_reward_claim_canary_runner_v1.py \
  --wave2-apply --wave2-observe --wave2-rollback-drill
```

## Happy path
- 3 claim applicati su `canary_user_001/002/003`
- Route coperte: `story_alpha_slice_preview`, `training_combat_onboarding_preview`, `boss_tower_alpha_loop_preview`
- Reward sotto cap, tutti non-premium
- 3 idempotency key, 3 rollback token emessi

## Negative tests (tutti PASS)
| Test | Esito |
|---|---|
| duplicate_idempotency_replay | `idempotent_replay_returned` |
| duplicate_conflicting_hash | `rejected_idempotency_conflict` |
| non_allowlisted_user | `rejected_non_allowlisted_user` |
| premium_reward_reject | `rejected_forbidden_reward_type` |
| over_cap_reward_reject | `rejected_over_cap` |

## Risultati
- `applied_to_local_staging = true`
- `applied_to_live = false`
- `db_writes = 0`
- `local_file_writes = 6` totali (3 da apply + 3 da rollback drill)
- `live_reward_grant = false`
- `wave2_success_count = 3`
- `verdict_local = PVE_REWARD_CLAIM_CANARY_WAVE2_OBSERVED_SAFE`

## Ledger snapshot
- Wave1/v79: 1 entry (rolled_back=true)
- Wave2: 3 entry (1 successivamente rolled_back dal drill)
