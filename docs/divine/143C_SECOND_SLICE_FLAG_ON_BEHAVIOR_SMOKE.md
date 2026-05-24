# 143C — PROJECT_U Track C: Flag-ON Behavior Smoke

## Verdict
`TRACK_C_SECOND_SLICE_FLAG_ON_BEHAVIOR_SMOKE_READY`

## Behavior verificato (replay in-process)
| Caso | Atteso | Osservato |
|---|---|---|
| `debuff_offensive` 15% campaign | atk -15 | ✅ |
| `debuff_defensive` 15% campaign | def -15 | ✅ |
| `speed_up` 15% campaign | speed +15 | ✅ |
| `speed_down` 15% campaign | speed -15 | ✅ |
| PvP cap (40% offensive ×0.75) | atk -30 | ✅ |
| Boss cap (40% defensive ×0.50) | def -20 | ✅ |
| Out-of-scope `dot` + `freeze` 100% | tutti 0 | ✅ |

## Guardie negative
- **No DoT/tick** ✅
- **No hard CC** ✅
- **No Borea Marchio live** ✅
- **Battle behavior per chiamanti non-flagged** invariata (identity)

## API smoke (flag ON)
```
GET /api/heroes:                    200 (count=100)
GET /api/heroes/primordial_gaia:    404
GET /api/heroes/borea:              200 (inert)
GET /api/heroes/greek_borea:        200 (inert)
GET /api/server-profiles/select:    503
GET /api/housing/preview:           503
```

## Validator
`/app/backend/scripts/validate_project_u_second_slice_flag_on_behavior_smoke_v1.py` → **[PASS]**
