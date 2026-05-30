# 205E — MATERIAL COST POLICY

**Track**: E | **Verdict**: `TRACK_E_MATERIAL_COST_POLICY_READY`

## Cost preview per stage (design-only, replace_before_release = true)

| stage    | materiali per +level                                | gold per +level |
|----------|-----------------------------------------------------|-----------------|
| early    | `gear_dust_common x5`                               | 200             |
| mid      | `gear_dust_common x12 + gear_shard_uncommon x1`     | 600             |
| late     | `gear_shard_uncommon x3 + gear_core_rare x1`        | 1800            |
| endgame  | `gear_core_rare x4 + gear_essence_epic x1`          | 5400            |

## Stage gates (preview)

- early→mid: `hero_level >= 30` OR `ascension_tier >= 1`
- mid→late: `hero_level >= 60` AND `forge_enhance_unlocked`
- late→endgame: `hero_level >= 90` AND `forge_reforge_unlocked` AND `optional_costellazione_gate`

## Vincoli

- **NO** inventario materiali runtime in questo pack.
- **NO** shop unlock, **NO** economy mutation.
