# 509 — PvE Reward Claim Canary Wave-4 Apply / Replay (v82)

## Esecuzione
```
PVE_REWARD_CLAIM_CANARY_MODE=LOCAL_FILE_STAGING \
PVE_REWARD_CLAIM_CANARY_WAVE4=YES_I_UNDERSTAND \
python3 backend/scripts/pve_reward_claim_canary_runner_v1.py \
  --wave4-apply --wave4-observe --wave4-rollback-drill
```

## Happy path (8/8)
| User | Route | TX ID |
|---|---|---|
| canary_user_001 | story_alpha_slice_preview | canary-wave4-tx-000001 |
| canary_user_002 | training_combat_onboarding_preview | canary-wave4-tx-000002 |
| canary_user_003 | boss_tower_alpha_loop_preview | canary-wave4-tx-000003 |
| canary_user_004 | first_session_onboarding_preview | canary-wave4-tx-000004 |
| canary_user_005 | alpha_menu_preview | canary-wave4-tx-000005 |
| canary_user_006 | reward_claim_summary_preview | canary-wave4-tx-000006 |
| canary_user_007 | event_arena_alpha_gate_preview | canary-wave4-tx-000007 |
| canary_user_008 | event_arena_first_alpha_slice_preview | canary-wave4-tx-000008 |

## Negative tests (7/7 PASS)
| Test | Esito |
|---|---|
| duplicate_idempotency_replay | idempotent_replay_returned |
| duplicate_conflicting_hash | rejected_idempotency_conflict |
| non_allowlisted_user | rejected_non_allowlisted_user |
| premium_reward_reject | rejected_forbidden_reward_type |
| over_cap_reward_reject | rejected_over_cap |
| malformed_route_reject | rejected_malformed_route |
| **event_arena_ranking_reward_reject** | **rejected_event_arena_ranking_reward** |

## Risultati
- `applied_to_local_staging = true`, `applied_to_live = false`
- `wave4_success_count = 8`
- `db_writes = 0`, `local_file_writes = 6` (3 apply + 3 rollback drill)
- `live_reward_grant = false`
- `verdict_local = PVE_REWARD_CLAIM_CANARY_WAVE4_OBSERVED_SAFE`
