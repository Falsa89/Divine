# 141C — PROJECT_S Track C: Second-Slice Golden Fixture Matrix

## Verdict
`TRACK_C_SECOND_SLICE_GOLDEN_FIXTURE_MATRIX_READY`

## Marker JSON
`/app/data/design/status_effects/project_s_second_slice_golden_fixture_matrix_v1.json`

## Validator
`/app/backend/scripts/validate_project_s_second_slice_golden_fixture_matrix_v1.py` → **[PASS]**

## 14/14 fixture matchano l'output del resolver puro

| # | Nome | Mode | Expected (atk/def/speed) |
|---:|---|---|---|
| 1 | empty list | campaign | 0 / 0 / 0 |
| 2 | single debuff_offensive | campaign | -15 / 0 / 0 |
| 3 | single debuff_defensive | campaign | 0 / -15 / 0 |
| 4 | single speed_up | campaign | 0 / 0 / +15 |
| 5 | single speed_down | campaign | 0 / 0 / -15 |
| 6 | per-status cap clamps single | campaign | -30 / 0 / 0 (input 9999%) |
| 7 | aggregate offensive cap saturation | campaign | -40 / 0 / 0 (2×30%) |
| 8 | aggregate defensive cap saturation | campaign | 0 / -40 / 0 (2×30%) |
| 9 | speed aggregate cap saturation | campaign | 0 / 0 / +30 (2×25%) |
| 10 | pvp multiplier 0.75x | pvp | -15 / 0 / 0 (input -20×0.75) |
| 11 | boss multiplier 0.5x | boss | -10 / 0 / 0 (input -20×0.5) |
| 12 | out-of-scope ignored (dot, freeze) | campaign | 0 / 0 / 0 |
| 13 | malformed negative/string/null → safe clamp | campaign | 0 / 0 / 0 |
| 14 | mixed valid + invalid + opposing | campaign | -10 / 0 / +15 |

## Test eseguiti
Il validator carica le 14 fixture, importa il resolver puro, esegue ciascuna e confronta con tolleranza `1e-9`. Tutte verde.

## Side effects
Nessuno. `runtime_imported=false`, `db_writes=false`.
