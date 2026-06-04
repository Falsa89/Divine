# 94 — Battle Engine Status/DoT/Targeting Patch (v94)

## Pack
`MEGA_RELEASE_ACCELERATION_43_v94`

## MD5 unlock decision
`battle_engine.py` MD5 **NON modificato** in v94. Patch dichiarata come design contract validabile via fixture matrix. v95 puo' applicare runtime con approvazione esplicita.

Old MD5: `151ca35ad3bc35f0a6209cb3744ed440` → New MD5: `151ca35ad3bc35f0a6209cb3744ed440` (UNCHANGED)

## DoT Core (6 status)
| Status | Category | Tick | Duration | Stack | Cleanse | Boss |
|--------|----------|------|----------|-------|---------|------|
| Burn | elemental_fire | end_of_target_turn | 3 | sum_ticks (max 5) | by_category | dot_cap_-15% |
| Poison | bio | end_of_target_turn | 4 | sum_ticks (max 5) | by_category | dot_cap_-20% |
| Bleed | physical | end_of_target_turn | 3 | sum_ticks (max 5) | by_category | dot_cap_-15% |
| Shock | elemental_thunder | on_action_attempt | 2 | reset_duration | by_category | stun→skill_power_-25% dur*0.5 |
| Frostbite | elemental_ice | end_of_target_turn | 3 | cap_stacks (3) | by_category | freeze→speed_down_30% dur*0.66 |
| Curse | shadow | end_of_target_turn | 4 | overwrite | by_priority | dot_cap_-25% |

## Cleanse
Policy disponibili: `all`, `top`, `by_category`, `by_priority`, `one_stack`, `remove_status`. Default per skill: `by_category`.

## Immunity
- Blocca nuove applicazioni.
- NON rimuove status gia' presenti.
- Conta status_prevented_by_immunity_count.

## Taunt
| Targeting | Taunt |
|-----------|-------|
| single_target | intercepts |
| priority_target | intercepts |
| aoe_all_enemies | NOT_intercepts |
| line / column | NOT_intercepts |
| aoe_partial (cleave_2) | MUST_respect (v94 bug fix) |

Bug fix v94: in `aoe_partial`, tauntee viene inserito come prima slot prioritaria del partial AoE.

## Boss Hard-Control Conversion
- Freeze → speed_down_30% (dur*0.66)
- Stun → skill_power_reduction_25% (dur*0.5, chance*0.75)
- Silence → skill_power_reduction_15% (dur*0.75, chance*0.85)
- Sleep → turn_delay_1 (dur*0.5, chance*0.5)
- Petrify → defense_down_20% (dur*0.5, chance*0.5)

## Battle Report Extension
Campi aggiunti (design): `dot_damage_done`, `status_applied_count`, `healing_done`, `cleanse_count`, `status_prevented_by_immunity_count`, `taunt_redirect_count`. NON rompe `PostBattleSummary` / `total_damage_done` / `team_a_final` / `team_b_final`.

## Rollback strategy
- v94 NON patcha `battle_engine.py` in runtime.
- Tutta la design e' in `v94_engine_regression_fixture_matrix_v1.json`.
- Validator coperti.
- Trigger rollback: `if any live grant or md5 drift detected`.
- Azione rollback: revert contract + report blocker.
