# 499 — PvE Reward Claim Canary Wave-3 Scope (v81)

## Scope
- `wave3_mode = local_file_based`
- `max_wave3_users = 5` (`canary_user_001..005`, alias-only)
- `max_wave3_claims_total = 5`
- `ui_preview_shell = deeplink_only`
- `production_ui_exposure = false`, `no_real_claim_button`, `no_live_claim_endpoint`
- `no_live_db / no_real_reward_grant / no_account_mutation / no_backend_route`
- `no_premium_currency / no_gacha_shop_vip_bp / no_event_currency / no_arena_ranking_reward`
- `rollback_required`, `observation_required`, `kill_switch_required`

## DB writes default
`db_writes_default = 0`
