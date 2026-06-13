# Pre-QA Stabilization 110 — Mutating Route Allowlist / Blocklist


## allowed_safe (27)

| Verb | Path | File |
|------|------|------|
| POST | `/competitive-guards/arena/preflight` | `backend/routes/competitive_guards.py` |
| POST | `/competitive-guards/event/preflight` | `backend/routes/competitive_guards.py` |
| POST | `/competitive-guards/guild/preflight` | `backend/routes/competitive_guards.py` |
| POST | `/competitive-guards/pvp/preflight` | `backend/routes/competitive_guards.py` |
| POST | `/controlled-rewards/achievement/claim` | `backend/routes/controlled_rewards.py` |
| POST | `/controlled-rewards/daily-weekly/claim` | `backend/routes/controlled_rewards.py` |
| POST | `/controlled-rewards/mail/claim` | `backend/routes/controlled_rewards.py` |
| POST | `/daily-login/claim` | `backend/routes/daily_login_claim.py` |
| POST | `/daily-login/claim/preflight` | `backend/routes/daily_login_claim.py` |
| POST | `/daily-quest/claim` | `backend/routes/daily_quest_claim.py` |
| POST | `/daily-quest/claim/preflight` | `backend/routes/daily_quest_claim.py` |
| POST | `/daily-quest/progress/complete` | `backend/routes/daily_quest_tracker.py` |
| POST | `/daily-quest/tracker/preflight` | `backend/routes/daily_quest_tracker.py` |
| POST | `/economy/strict/equipment/equip` | `backend/routes/economy_strict.py` |
| POST | `/economy/strict/equipment/fusion` | `backend/routes/economy_strict.py` |
| POST | `/economy/strict/equipment/unequip` | `backend/routes/economy_strict.py` |
| POST | `/economy/strict/equipment/upgrade` | `backend/routes/economy_strict.py` |
| POST | `/economy/strict/forge/craft` | `backend/routes/economy_strict.py` |
| POST | `/economy/strict/forge/preflight` | `backend/routes/economy_strict.py` |
| POST | `/economy/strict/shop/buy` | `backend/routes/economy_strict.py` |
| POST | `/economy/strict/soul-forge/retire` | `backend/routes/economy_strict.py` |
| POST | `/guild/strict/membership/preview` | `backend/routes/guild_strict.py` |
| POST | `/rewards/claim` | `backend/routes/reward_claim.py` |
| POST | `/rewards/claim/preflight` | `backend/routes/reward_claim.py` |
| POST | `/tower/strict/battle/execute` | `backend/routes/tower_strict.py` |
| POST | `/tower/strict/battle/preview` | `backend/routes/tower_strict.py` |
| POST | `/tower/strict/preflight` | `backend/routes/tower_strict.py` |

## legacy_quarantined (14)

| Verb | Path | File |
|------|------|------|
| POST | `/achievements/claim` | `backend/routes/achievements.py` |
| POST | `/api/gacha/pull` | `backend/server.py` |
| POST | `/api/gacha/pull10` | `backend/server.py` |
| POST | `/events/battle` | `backend/routes/combat.py` |
| POST | `/faction/join` | `backend/routes/guild.py` |
| POST | `/gacha/pull` | `backend/routes/heroes.py` |
| POST | `/gacha/pull10` | `backend/routes/heroes.py` |
| POST | `/guild/create` | `backend/routes/guild.py` |
| POST | `/guild/join/{guild_id}` | `backend/routes/guild.py` |
| POST | `/guild/leave` | `backend/routes/guild.py` |
| POST | `/guild/strict/preflight` | `backend/routes/guild_strict.py` |
| POST | `/pvp/battle` | `backend/routes/combat.py` |
| POST | `/story/battle` | `backend/routes/combat.py` |
| POST | `/team/update-formation` | `backend/battle_engine.py` |

## requires_future_pack (2)

| Verb | Path | File |
|------|------|------|
| POST | `/api/psp/starter/claim` | `backend/server.py` |
| POST | `/delete-account-request` | `backend/routes/v96_auth.py` |

## dev_only (1)

| Verb | Path | File |
|------|------|------|
| POST | `/guest` | `backend/routes/v96_auth.py` |

## uncategorized (86)

| Verb | Path | File |
|------|------|------|
| POST | `/affinity/gift-spend` | `backend/routes/affinity_gift_spend.py` |
| POST | `/alpha-battle-preview` | `backend/routes/material_raid_preview.py` |
| POST | `/alpha-reward-summary-preview` | `backend/routes/material_raid_preview.py` |
| POST | `/api/admin/bots/run-cycle` | `backend/server.py` |
| POST | `/api/login` | `backend/server.py` |
| POST | `/api/psp/ensure` | `backend/server.py` |
| POST | `/api/register` | `backend/server.py` |
| POST | `/apple` | `backend/routes/v96_auth.py` |
| POST | `/artifacts/fuse` | `backend/routes/artifacts.py` |
| POST | `/artifacts/pull` | `backend/routes/artifacts.py` |
| POST | `/artifacts/pull10` | `backend/routes/artifacts.py` |
| POST | `/battle/simulate` | `backend/battle_engine.py` |
| POST | `/clear-preview` | `backend/routes/material_raid_preview.py` |
| POST | `/constellations/equip` | `backend/routes/artifacts.py` |
| POST | `/constellations/fuse` | `backend/routes/artifacts.py` |
| POST | `/constellations/pull` | `backend/routes/artifacts.py` |
| POST | `/constellations/pull10` | `backend/routes/artifacts.py` |
| POST | `/create-preview` | `backend/routes/story_battle_instance_preview.py` |
| POST | `/dm/threads` | `backend/routes/social.py` |
| POST | `/dm/threads/{thread_id}/messages` | `backend/routes/social.py` |
| POST | `/dm/threads/{thread_id}/read` | `backend/routes/social.py` |
| POST | `/enchant/preview` | `backend/routes/gear_forge_preview.py` |
| POST | `/enhance/preview` | `backend/routes/gear_forge_preview.py` |
| POST | `/equipment/unequip/{equipment_id}` | `backend/routes/equipment.py` |
| POST | `/friends/accept` | `backend/routes/social.py` |
| POST | `/friends/remove/{friend_id}` | `backend/routes/social.py` |
| POST | `/friends/request` | `backend/routes/social.py` |
| POST | `/fusion/preview` | `backend/routes/gear_forge_preview.py` |
| POST | `/google` | `backend/routes/v96_auth.py` |
| POST | `/grant-plan-preview` | `backend/routes/material_raid_claim_safety_preview.py` |
| POST | `/guard-plan-preview` | `backend/routes/artifact_upgrade_safety_preview.py` |
| POST | `/guard-plan-preview` | `backend/routes/battle_pass_claim_safety_preview.py` |
| POST | `/guard-plan-preview` | `backend/routes/divine_weapon_upgrade_safety_preview.py` |
| POST | `/guard-plan-preview` | `backend/routes/gear_forge_fusion_safety_preview.py` |
| POST | `/guard-plan-preview` | `backend/routes/gem_socket_commit_safety_preview.py` |
| POST | `/guard-plan-preview` | `backend/routes/mail_claim_safety_preview.py` |
| POST | `/guard-plan-preview` | `backend/routes/rune_scroll_talisman_safety_preview.py` |
| POST | `/idempotency-preview` | `backend/routes/artifact_upgrade_safety_preview.py` |
| POST | `/idempotency-preview` | `backend/routes/battle_pass_claim_safety_preview.py` |
| POST | `/idempotency-preview` | `backend/routes/divine_weapon_upgrade_safety_preview.py` |
| POST | `/idempotency-preview` | `backend/routes/gear_forge_fusion_safety_preview.py` |
| POST | `/idempotency-preview` | `backend/routes/gem_socket_commit_safety_preview.py` |
| POST | `/idempotency-preview` | `backend/routes/mail_claim_safety_preview.py` |
| POST | `/idempotency-preview` | `backend/routes/material_raid_claim_safety_preview.py` |
| POST | `/idempotency-preview` | `backend/routes/rune_scroll_talisman_safety_preview.py` |
| POST | `/instance/preview` | `backend/routes/v108_authoritative_pre_instance.py` |
| POST | `/instance/resolve-preview` | `backend/routes/v108_authoritative_runtime_resolve.py` |
| POST | `/launch` | `backend/routes/v107a_battle_launch.py` |
| POST | `/logout` | `backend/routes/v96_auth.py` |
| POST | `/logout-all` | `backend/routes/v96_auth.py` |
| POST | `/notifications/read-all` | `backend/routes/push_notifications.py` |
| POST | `/playback-preview` | `backend/routes/battle_replay_preview.py` |
| POST | `/playback-preview` | `backend/routes/generic_visual_battle_runner_preview.py` |
| POST | `/plaza/chat` | `backend/routes/social.py` |
| POST | `/power-preview` | `backend/routes/gem_socket_preview.py` |
| POST | `/push/register` | `backend/routes/push_notifications.py` |
| POST | `/push/test` | `backend/routes/push_notifications.py` |
| POST | `/reforge/preview` | `backend/routes/gear_forge_preview.py` |
| POST | `/refresh` | `backend/routes/v96_auth.py` |
| POST | `/replace-preview` | `backend/routes/gem_socket_preview.py` |
| POST | `/reward-preview` | `backend/routes/material_raid_preview.py` |
| POST | `/sanctuary/affinity/gain` | `backend/routes/sanctuary.py` |
| POST | `/sanctuary/complete-tutorial` | `backend/routes/sanctuary.py` |
| POST | `/sanctuary/constellation/attempt` | `backend/routes/sanctuary.py` |
| POST | `/sanctuary/constellation/skip/{hero_id}` | `backend/routes/sanctuary.py` |
| POST | `/sanctuary/home-hero` | `backend/routes/sanctuary.py` |
| POST | `/select` | `backend/routes/server_profiles.py` |
| POST | `/socket-preview` | `backend/routes/gem_socket_preview.py` |
| POST | `/title/set` | `backend/routes/combat.py` |
| POST | `/tower/battle` | `backend/routes/combat.py` |
| POST | `/unsocket-preview` | `backend/routes/gem_socket_preview.py` |
| POST | `/user/faction-v2/select` | `backend/routes/player_faction_v2.py` |
| POST | `/validate-claim-request` | `backend/routes/material_raid_claim_safety_preview.py` |
| POST | `/validate-payload` | `backend/routes/generic_visual_battle_runner_preview.py` |
| POST | `/validate-payload` | `backend/routes/story_battle_instance_preview.py` |
| POST | `/validate-replay-payload` | `backend/routes/battle_replay_preview.py` |
| POST | `/validate-request` | `backend/routes/artifact_upgrade_safety_preview.py` |
| POST | `/validate-request` | `backend/routes/battle_pass_claim_safety_preview.py` |
| POST | `/validate-request` | `backend/routes/divine_weapon_upgrade_safety_preview.py` |
| POST | `/validate-request` | `backend/routes/gear_forge_fusion_safety_preview.py` |
| POST | `/validate-request` | `backend/routes/gem_socket_commit_safety_preview.py` |
| POST | `/validate-request` | `backend/routes/mail_claim_safety_preview.py` |
| POST | `/validate-request` | `backend/routes/rune_scroll_talisman_safety_preview.py` |
| POST | `/wallet/spend` | `backend/routes/soul_forge.py` |
| POST | `/{hero_id}/upgrade/preview` | `backend/routes/gear_cap_preview.py` |
| POST | `/{hero_id}/upgrade/preview` | `backend/routes/hero_elevation_preview.py` |