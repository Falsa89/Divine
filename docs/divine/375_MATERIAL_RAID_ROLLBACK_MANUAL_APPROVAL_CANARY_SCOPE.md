# 375 — Rollback + Manual Approval + Canary Scope

Pack: `MEGA_RELEASE_ACCELERATION_12_MATERIAL_RAID_CLAIM_SAFETY_AND_STAGING_BLUEPRINT_SUPER_PACK_v63`

## Rollback / compensation

- `rollback_required=true`
- `rollback_test_required_before_live=true`
- `compensation_required_if_partial_grant=true`

## Manual approval matrix

- `manual_approval_required=true`
- `approval_phrase_required=true`
- `checksum_required=true`

## Canary scope

- material_raid_only
- `max_users_first_wave=1..5`
- `max_claims_per_user=1`
- `max_total_claims_first_wave=10`
- `premium_currency_allowed=false`
