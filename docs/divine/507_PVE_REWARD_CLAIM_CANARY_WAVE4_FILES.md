# 507 — PvE Reward Claim Canary Wave-4 Files (v82)

## Statici
- `/app/data/canary_staging/wave4_allowlist_v1.json` (8 alias, no PII)
- `/app/data/canary_staging/wave4_reward_fixtures_v1.json` (non-premium, caps 500/50/100/3, 8 route)
- `/app/data/canary_staging/wave4_plan_v1.json` (8 happy path + 7 negative descriptor)

## Generati dal runner
- `wave4_local_ledger_v1.json` (`wave=4`, `canary=true`, `isolated_from_live=true`)
- `wave4_rollback_tokens_v1.json`
- `wave4_observation_log_v1.json`

## Route coperte (8)
story_alpha_slice_preview, training_combat_onboarding_preview, boss_tower_alpha_loop_preview,
first_session_onboarding_preview, alpha_menu_preview, reward_claim_summary_preview,
event_arena_alpha_gate_preview, event_arena_first_alpha_slice_preview
