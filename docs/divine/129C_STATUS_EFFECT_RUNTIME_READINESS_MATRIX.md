# 129C — Status Effect Runtime Readiness Matrix (Track C)

**Verdict:** `TRACK_C_STATUS_EFFECT_RUNTIME_READINESS_MATRIX_READY`

## Matrice (10 categorie canonical)
| Category | Handler | Boss | Stacking | Cleanse | VFX | Coverage | Blockers |
|---|---|---|---|---|---|---|---|
| buff_offensive | battle_stat_modifier | normal | refresh | cleansable | buff_icon | phase2_ut_pass | battle_engine_wiring, vfx_pipeline |
| buff_defensive | battle_stat_modifier | normal | refresh | cleansable | buff_icon | phase2_ut_pass | battle_engine_wiring |
| buff_support | battle_stat_modifier | normal | stack_capped | cleansable | buff_icon | phase2_ut_pass | battle_engine_wiring |
| debuff_offensive | battle_stat_modifier | reduced | refresh | cleansable | debuff_icon | phase2_ut_pass | battle_engine_wiring |
| debuff_defensive | battle_stat_modifier | reduced | refresh | cleansable | debuff_icon | phase2_ut_pass | battle_engine_wiring |
| control | battle_control_handler | immune | none | hard_cc_immunity_rules | control_icon | phase2_ut_pass | battle_engine_wiring, boss_immunity_matrix |
| dot | battle_tick_handler | reduced | stack_capped | cleansable | dot_icon | phase2_ut_pass | battle_engine_wiring, tick_loop_integration |
| hot | battle_tick_handler | normal | stack_capped | cleansable | hot_icon | phase2_ut_pass | battle_engine_wiring, tick_loop_integration |
| shield | battle_shield_handler | normal | refresh | non_cleansable | shield_icon | phase2_ut_pass | battle_engine_wiring |
| meta | battle_meta_handler | immune | none | source_locked | meta_icon | phase2_ut_pass | battle_engine_wiring, meta_handler_design |

## First safe runtime slice (consigliato)
`buff_offensive + buff_defensive` — minor rischio, riusa stat modifier
esistente, niente tick loop.

## Vincoli rispettati
- NO battle behavior mutation; NO runtime status activation;
  NO battle_engine/battle_core/combat.tsx changes.
