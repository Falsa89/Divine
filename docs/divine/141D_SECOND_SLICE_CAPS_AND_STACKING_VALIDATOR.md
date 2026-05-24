# 141D — PROJECT_S Track D: Second-Slice Caps & Stacking Validator

## Verdict
`TRACK_D_SECOND_SLICE_CAPS_AND_STACKING_VALIDATOR_READY`

## Marker JSON
`/app/data/design/status_effects/project_s_second_slice_caps_stacking_v1.json`

## Validator
`/app/backend/scripts/validate_project_s_second_slice_caps_stacking_v1.py` → **[PASS]**

## Adversarial cases verificati
| Caso | Atteso | Risultato |
|---|---|---|
| 10× max debuff_offensive | clamp aggregate -40 atk_pct | ✅ |
| Opposing speed pair at cap (25 vs 25) | net 0 speed_pct | ✅ |
| Extreme opposing speed (100 vs 100) | clamp per-status → net 0 | ✅ |
| PvP mode (40% off debuff ×0.75) | -30 atk_pct | ✅ |
| Boss mode (40% off debuff ×0.50) | -20 atk_pct | ✅ |
| Negative stat inversion check | atk_pct mai > 0 | ✅ |
| Multiplicative runaway (1000× def debuff) | clamp aggregate -40 def_pct | ✅ |

## Invarianti dimostrate
- **Per-status cap enforced** ✅
- **Aggregate cap enforced** (offensive/defensive/speed) ✅
- **Mode multipliers enforced** (pvp 0.75, boss 0.50) ✅
- **Additive stacking only** ✅
- **No multiplicative runaway** ✅
- **No negative stat inversion** (debuff non genera mai delta positivo) ✅
- **Opposing speed pair cancels** ✅

## Side effects
Nessuno. `balance_runtime_changed=false`, `db_writes=false`.
