# 380 — Material Raid Canary Dry-Run Scenarios

Pack: `MEGA_RELEASE_ACCELERATION_13_MATERIAL_RAID_STAGING_DRY_RUN_AND_CANARY_SIMULATION_PACK_v64`

## Fixture

- `max_users_first_wave=5`
- `max_total_claims_first_wave=10`
- `max_claims_per_user=1`
- `premium_currency_allowed=false`
- `material_only=true`
- utenti placeholder `test_user_001..test_user_005`

## Scenario matrix (10 categorie)

first valid / duplicate same payload / duplicate conflicting /
missing key / over per-user cap / over total canary cap /
reward hash mismatch / rollback token preview /
observation threshold warning / observation threshold critical.
