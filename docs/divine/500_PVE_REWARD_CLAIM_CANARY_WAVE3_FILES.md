# 500 — PvE Reward Claim Canary Wave-3 Files (v81)

## Statici
- `/app/data/canary_staging/wave3_allowlist_v1.json` (5 alias, no PII)
- `/app/data/canary_staging/wave3_reward_fixtures_v1.json` (non-premium, caps 500/50/100/3, 5 route)
- `/app/data/canary_staging/wave3_plan_v1.json` (5 happy path + 6 negative test descriptors)

## Generati dal runner
- `/app/data/canary_staging/wave3_local_ledger_v1.json` (`wave=3`, `canary=true`, `isolated_from_live=true`)
- `/app/data/canary_staging/wave3_rollback_tokens_v1.json`
- `/app/data/canary_staging/wave3_observation_log_v1.json`

## Route coperte
- `story_alpha_slice_preview`
- `training_combat_onboarding_preview`
- `boss_tower_alpha_loop_preview`
- `first_session_onboarding_preview`
- `alpha_menu_preview`
