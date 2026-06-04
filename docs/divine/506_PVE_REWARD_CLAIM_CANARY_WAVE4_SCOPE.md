# 506 — PvE Reward Claim Canary Wave-4 Scope (v82)

## Scope
- `wave4_mode = local_file_based`
- `max_wave4_users = 8` (`canary_user_001..008`, alias-only)
- `max_wave4_claims_total = 8`
- `live_staging_design_only = true`, `live_staging_db_apply_allowed = false`
- `no_live_db / no_real_reward_grant / no_account_mutation / no_backend_route`
- `no_premium_currency / no_gacha_shop_vip_bp / no_event_currency / no_arena_ranking_reward`
- `production_ui_exposure = false`, `no_real_claim_button`
- `rollback_required / observation_required / kill_switch_required`

## DB writes default
`db_writes_default = 0`
