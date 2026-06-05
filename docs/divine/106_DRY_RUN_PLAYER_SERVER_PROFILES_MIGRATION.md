# v106 — Dry-Run Migration Result

**Pack**: `MEGA_RELEASE_ACCELERATION_55_v106`
**Source JSON**: `data/design/server_scope/v106_dry_run_player_server_profiles_result_v1.json`

## Execution

- Script: `backend/scripts/dry_run_v106_player_server_profiles_migration.py`
- DB inspected: **YES** (MongoDB `divine_waifus`)
- DB writes performed: **0**
- Default `server_id` per backfill: **`s1`**

## Estimated profiles to create

**160** (numero attuale di account in `users` collection).

## Migration plan summary

- `users` → resta account-global.
- `user_heroes` → snapshot in `psp.roster` (server_id=s1).
- `teams` → snapshot in `psp.team_formation`.
- `inventory` → riferimento `psp.inventory_ref` (server_id=s1).
- `currencies` soft → `psp.currencies` · hard → account_global.
- `story_progress`, `tower_progress`, `arena_profile`, `guild_membership`, `live_event_state` → snapshot in psp.
- `chat_messages` → collection separata con channel_key prefix `{server_id}:` (v109).

## Safety

- `no_db_writes = true`
- `no_destructive_migration = true`
- `no_reward_grant = true`
- `no_premium_currency_grant = true`
- `no_original_collections_deleted = true`
