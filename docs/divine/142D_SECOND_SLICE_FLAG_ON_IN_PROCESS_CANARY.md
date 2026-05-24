# 142D — PROJECT_T Track D: Flag-ON In-Process Canary

## Verdict
`TRACK_D_SECOND_SLICE_FLAG_ON_IN_PROCESS_CANARY_READY`

## Marker JSON
`/app/data/design/status_effects/project_t_second_slice_flag_on_canary_v1.json`

## Validator
`/app/backend/scripts/validate_project_t_second_slice_flag_on_canary_v1.py` → **[PASS]**

## Canary mode
**In-process only**: la env var `STATUS_RUNTIME_SECOND_SLICE_ENABLED=true` viene settata SOLO dentro un subprocess Python isolato avviato dal validator. Il `.env` reale rimane invariato.

## Validator subprocess test results
| Caso | Atteso | Risultato |
|---|---|---|
| `debuff_offensive` (15%) | `atk_pct=-15, def_pct=0, speed_pct=0` | ✅ |
| `debuff_defensive` (15%) | `atk_pct=0, def_pct=-15, speed_pct=0` | ✅ |
| `speed_up` (15%) | `atk_pct=0, def_pct=0, speed_pct=15` | ✅ |
| `speed_down` (15%) | `atk_pct=0, def_pct=0, speed_pct=-15` | ✅ |
| out-of-scope `dot` (100%) | `{0,0,0}` (ignored) | ✅ |
| per-status cap clamp (9999% debuff_off) | `atk_pct=-30` | ✅ |
| flag ON + `dry_run=False` | **identity** (no live activation) | ✅ |

## Env var leak verification
Dopo l'esecuzione del subprocess, `os.environ` del validator NON contiene `STATUS_RUNTIME_SECOND_SLICE_ENABLED`. ✅

## Side effects
- `/app/backend/.env`: invariato.
- DB writes: 0.
- Live runtime: invariato.
