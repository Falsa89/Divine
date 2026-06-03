# 374 — Material Raid Staging DB Blueprint + Ledger Draft

Pack: `MEGA_RELEASE_ACCELERATION_12_MATERIAL_RAID_CLAIM_SAFETY_AND_STAGING_BLUEPRINT_SUPER_PACK_v63`

## Collections proposte (blueprint only, nessuna migrazione applicata)

- `material_raid_claim_ledger_staging`
- `material_raid_claim_idempotency_keys_staging`
- `material_raid_claim_audit_events_staging`

## Reward grant boundary

- `reward_preview != reward_grant`
- grant solo dopo approvazione live esplicita
- nessuna premium currency nel primo canary
- material-only suggerito nel primo canary

## Invarianti

- `blueprint_only=true`, `migration_created=false`, `migration_applied=false`
- `collections_created=false`, `indexes_created=false`
- `db_writes=0`
