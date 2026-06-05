# v106 — Rollback Player Server Profiles

**Pack**: `MEGA_RELEASE_ACCELERATION_55_v106`
**Source JSON**: `data/design/server_scope/v106_rollback_plan_v1.json`

## Status default

`ROLLBACK_NOT_EXECUTED_PLAN_DOCUMENTED`

Rollback NON eseguibile senza i flag:

- `V106_PLAYER_SERVER_PROFILES_ROLLBACK=YES`
- `V106_ROLLBACK_BACKUP_MANIFEST_CONFIRMED=YES`

## Strategie

### 1. `reverse_via_backup_restore` (preferita)

1. Verify backup manifest SHA256 integrity.
2. Restore original collections from backup snapshot.
3. Archive (NOT delete) `player_server_profiles` → `player_server_profiles_archived_<ts>`.
4. Drop indices `psp_*`.
5. Smoke test loaders.

### 2. `soft_disable_psp_only` (fallback)

1. Set feature flag `server_scoped_runtime_enabled=false`.
2. Loader fall back a vecchio path account-wide.
3. `player_server_profiles` resta letta solo da metrics.

## Forbidden durante rollback

- delete record non riconosciuti
- truncate `users` / `user_heroes` / `inventory`
- grant premium currency
- reward grant
