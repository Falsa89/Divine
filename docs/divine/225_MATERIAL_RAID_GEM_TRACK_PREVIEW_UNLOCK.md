# 225 — MATERIAL RAID GEM TRACK PREVIEW UNLOCK (MEGA_BATCH_ACCELERATION_1 TRACK B)

`gem_material_raid` passa da `locked_deferred` a `open_preview`.

## Track state dopo pack

- gear_material_raid: open_preview
- hero_growth_raid: open_preview
- **gem_material_raid: open_preview** (sbloccato in questo pack)
- rune_material_raid: locked_deferred
- artifact_divine_material_raid: locked_deferred

## Gem reward preview (design-only, replace_before_release)

| Stage | gem_dust_common | gem_shard_rare |
|---|---|---|
| I | 40 | 0 |
| II | 100 | 1 |
| III | 180 | 3 |
| IV | 320 | 7 |
| V | 550 | 14 |

## Garanzie

- preview-only, non-final
- materials_granted = false, reward_claim_enabled = false
- db_writes = 0
- no user_materials, no premium users.gems, no stamina/tickets/paid attempts
- no Gem Socket commit, no Rune/Artifact/Divine Weapon runtime changes
