# 502 — PvE Reward Claim Canary Wave-3 Apply / Replay (v81)

## Esecuzione
```
PVE_REWARD_CLAIM_CANARY_MODE=LOCAL_FILE_STAGING \
PVE_REWARD_CLAIM_CANARY_WAVE3=YES_I_UNDERSTAND \
python3 backend/scripts/pve_reward_claim_canary_runner_v1.py \
  --wave3-apply --wave3-observe --wave3-rollback-drill
```

## Happy path (5/5)
| User | Route | TX ID |
|---|---|---|
| canary_user_001 | story_alpha_slice_preview | canary-wave3-tx-000001 |
| canary_user_002 | training_combat_onboarding_preview | canary-wave3-tx-000002 |
| canary_user_003 | boss_tower_alpha_loop_preview | canary-wave3-tx-000003 |
| canary_user_004 | first_session_onboarding_preview | canary-wave3-tx-000004 |
| canary_user_005 | alpha_menu_preview | canary-wave3-tx-000005 |

## Negative tests (6/6 PASS)
| Test | Esito |
|---|---|
| duplicate_idempotency_replay | idempotent_replay_returned |
| duplicate_conflicting_hash | rejected_idempotency_conflict |
| non_allowlisted_user | rejected_non_allowlisted_user |
| premium_reward_reject | rejected_forbidden_reward_type |
| over_cap_reward_reject | rejected_over_cap |
| **malformed_route_reject** | **rejected_malformed_route** |

## Risultati
- `applied_to_local_staging = true`, `applied_to_live = false`
- `wave3_success_count = 5`
- `db_writes = 0`, `local_file_writes = 6` totali (3 apply + 3 rollback drill)
- `live_reward_grant = false`
- `verdict_local = PVE_REWARD_CLAIM_CANARY_WAVE3_OBSERVED_SAFE`
