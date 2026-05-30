# 207B — FORGE SCHEMA AND CONFIG

**Track**: B | **Verdict**: `TRACK_B_FORGE_SCHEMA_AND_CONFIG_READY`

## 4 subsystem canonici

| id | label | role |
|---|---|---|
| enhance | Potenzia | Alza +level fino al cap +50 (staged 10/20/35/50) |
| fusion  | Fondi    | Quality-up con pezzi same-slot in eccesso |
| reforge | Riforgia | Reroll sub-stat (preserva +level e quality) |
| enchant | Incanta  | Aggiunge proprietà magiche (design-only futuro) |

## Fusion rules preview

- `min_fodder_for_quality_up = 3`
- `same_slot_required = true`
- `same_or_lower_quality_required = true`
- guards future commit: `fodder_not_equipped`, `fodder_not_locked_or_favorite`, `base_not_in_active_team`

## Cost preview enhance

Replicato da `data/design/gear_cap_plus_50/E_material_cost_policy_v1.json`.

## Cost preview fusion

| Transizione | Gold | Materiali |
|---|---|---|
| common→uncommon | 500 | `gear_dust_common x10` |
| uncommon→rare | 1500 | `gear_shard_uncommon x3` |
| rare→epic | 4500 | `gear_core_rare x2` |
| epic→legendary | 13500 | `gear_essence_epic x2` |
| legendary→mythic | 40500 | `gear_essence_epic x6` |

Valori design-only, `replace_before_release = true`.
