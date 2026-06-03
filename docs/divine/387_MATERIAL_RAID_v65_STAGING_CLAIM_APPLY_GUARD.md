# 387 — v65 Staging Claim Apply Guard

Pack: `MEGA_RELEASE_ACCELERATION_14_MATERIAL_RAID_FIRST_CONTROLLED_LIVE_STAGING_CLAIM_PACK_v65`

## Gates (tutti richiesti per --apply)

1. `--apply` esplicito
2. `MATERIAL_RAID_V65_STAGING_APPLY_PHRASE=approvo`
3. `MATERIAL_RAID_V65_STAGING_APPLY_CHECKSUM` matches
4. `/app/data/staging/material_raid_v65/.staging_ready` con `STAGING_ISOLATED_APPROVED=true`
5. `STAGING_MONGO_URL` set e distinto da `MONGO_URL`
6. Checksum self-check

## Caps

`max_users=5`, `per_user_cap=1`, `total_cap=10`, `material_only`, no premium.
