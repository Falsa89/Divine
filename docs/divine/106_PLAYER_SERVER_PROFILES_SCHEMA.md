# v106 — player_server_profiles Schema v1

**Pack**: `MEGA_RELEASE_ACCELERATION_55_v106`
**Source JSON**: `data/design/server_scope/player_server_profiles_schema_v1.json`

## Collection

`player_server_profiles`

## Primary Key

**Composta**: `(account_id, server_id)`

## profile_id format

`<account_id>:<server_id>` (es. `64f0a3b9d4...:s1`)

## Document shape

```json
{
  "profile_id": "<account_id>:<server_id>",
  "account_id": "<string>",
  "server_id": "<string>",
  "display_name": "<string>",
  "account_level": 1,
  "account_exp": 0,
  "created_at": "<iso>",
  "last_played_at": "<iso>",
  "starter_profile": true,
  "roster": [],
  "team_formation": [],
  "inventory_ref": null,
  "currencies": {"gold": 0, "server_tokens": 0},
  "story_progress": {},
  "tower_progress": {},
  "arena_profile": {"mmr": 1000, "rank_tier": "unranked"},
  "guild_profile": {"guild_id": null, "role": null},
  "live_event_state": {},
  "flags": {
    "server_scoped": true,
    "migrated_from_account_wide": false,
    "legacy_quarantine_present": false
  },
  "migration_metadata": {
    "migrated_at": null,
    "migration_pack": null,
    "source_user_id": null,
    "backup_manifest_id": null
  }
}
```

## Indici (5)

| Name | Fields | Unique |
|---|---|---|
| `psp_account_server_unique` | `(account_id, server_id)` | ✅ |
| `psp_server_id` | `(server_id)` | ❌ |
| `psp_account_id` | `(account_id)` | ❌ |
| `psp_server_last_played` | `(server_id, last_played_at)` | ❌ |
| `psp_server_level` | `(server_id, account_level)` | ❌ (per rankings v108+) |

## Separation rules

- `users` resta identità globale.
- `player_server_profiles` contiene stato game/server.
- **No password_hash duplicato.**
- **No OAuth raw token duplicato.**
- **No provider secrets.**
- **No premium provider data.**

## Forbidden fields

`password_hash`, `oauth_access_token`, `oauth_refresh_token`, `provider_client_secret`, `raw_payment_method`, `raw_iap_receipt_token`.

## Safety nello starter

- `account_level=1`
- **No premium currency grant.**
- **No random starter heroes.**
- **No legacy heroes.**
- **No reward grant on create.**
