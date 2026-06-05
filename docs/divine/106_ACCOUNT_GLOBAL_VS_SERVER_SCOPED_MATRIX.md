# v106 — Account-Global vs Server-Scoped Matrix

**Pack**: `MEGA_RELEASE_ACCELERATION_55_v106`
**Source JSON**: `data/design/server_scope/v106_account_global_vs_server_scoped_matrix_v1.json`

## Account-Global (10)

| System | Reason |
|---|---|
| auth_identity | unique cross-server |
| provider_linking | OAuth link per account |
| email/device/session | login surface |
| privacy_account_deletion | GDPR account-wide |
| hard_currency_wallet | premium follows account |
| vip_status | account entitlement |
| global_settings | UI/audio prefs |
| blocked_users_list | safety follows account |
| external_credentials_link | provider link |
| iap_entitlement_global | purchases follow account |

## Server-Scoped (14)

`roster_user_heroes`, `hero_levels_stars_awakening`, `inventory_materials`, `soft_currencies`, `team_formation`, `story_progress`, `tower_progress`, `arena_mmr_rank`, `guild_membership`, `chat_messages`, `live_event_participation`, `bot_server_actor_interaction`, `reward_claim_state_server_bound`, `ranking_leaderboards`.

## Mixed / Needs Decision (8)

| System | Recommended |
|---|---|
| battle_pass | server_bound_with_global_premium_track |
| cosmetics/skins/titles | account_global_unlock_equip_per_server |
| artifact_collection | server_bound |
| housing | server_bound |
| friend_list | account_global |
| account_level_achievements | account_global |
| gacha_history_pity | server_bound_pity_global_ledger |
| shop_purchases | split_by_sku |
