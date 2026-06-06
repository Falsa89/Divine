# v110 PSP PREP — Backup and Snapshot Plan

**Pack**: `MEGA_RELEASE_ACCELERATION_70_v110_PSP_APPLY_AND_LEGACY_CLEANUP_PREP_GATED_NOT_APPLIED`
**Track**: D
**Public sync tag**: `PUBLIC_SYNC_TAG_v110_PSP_APPLY_AND_LEGACY_CLEANUP_PREP_GATED_NOT_APPLIED`

## Strategia

- **Tool**: `mongodump`
- **DB**: `divine_waifus`
- **Target path**: `/app/backups/v110_pre_psp_apply/<YYYYMMDD_HHmmss>/`
- **Snapshot eseguito in questo pack**: **NO** (`snapshot_executed_in_this_pack=false`)
- **Required before apply**: `true`
- **Required before rollback**: `true`

## Collezioni in scope (21)

`users`, `user_heroes`, `team_formation`, `user_inventory`, `user_equipment`, `battlepass_progress`, `vip_progress`, `user_mail`, `achievements`, `user_cosmetics`, `guild_membership`, `guild_wars`, `chat_messages`, `dm_messages`, `rankings`, `arena_mmr`, `live_events`, `bots`, `battle_instances`, `player_server_profiles`, `migration_logs`.

## Masking rules

| Regola | Valore |
|---|---|
| mask_secrets | true |
| mask_iap_receipts_token | true |
| mask_oauth_tokens | true |
| mask_email_for_export | true |
| never_export_passwords | true |

## Verifica integrità

- verify_dump_integrity: true
- verify_collection_count_match: true
- verify_document_sample_diff: true
- keep_minimum_versions: 3
- retention_days: 30

## Riferimento JSON

`/app/data/design/v110_psp_migration/v110_backup_manifest_plan_v1.json`
