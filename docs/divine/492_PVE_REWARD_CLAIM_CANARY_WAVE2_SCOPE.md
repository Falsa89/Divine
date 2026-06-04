# 492 — PvE Reward Claim Canary Wave-2 Scope (v80)

## Scope
- `wave2_mode = local_file_based`
- `max_wave2_users = 3` (alias-only: `canary_user_001..003`)
- `max_wave2_claims_total = 3`
- `no_live_db`, `no_real_reward_grant`, `no_account_mutation`
- `no_backend_route`, `no_premium_currency`, `no_gacha_shop_vip_bp`
- `no_event_currency`, `no_arena_ranking_reward`
- `no_broad_rollout`, `no_production_ui_exposure`, `no_env_mutation`
- `rollback_required`, `observation_required`, `kill_switch_required`
- `previous_v79_tx_may_be_rolled_back = true`

## DB writes default
`db_writes_default = 0`
