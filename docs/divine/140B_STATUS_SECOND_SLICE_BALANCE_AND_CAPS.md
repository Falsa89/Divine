# 140B — PROJECT_R Track B: Status Second-Slice Balance & Caps

## Verdict
`TRACK_B_STATUS_SECOND_SLICE_BALANCE_AND_CAPS_READY`

## Marker JSON
`/app/data/design/status_effects/project_r_status_second_slice_balance_caps_v1.json`

## Validator
`/app/backend/scripts/validate_project_r_status_second_slice_balance_caps_v1.py` → **[PASS]**

## Per-status caps (pct)
| Famiglia | min | default | max |
|---|---:|---:|---:|
| debuff_offensive | 5.0 | 15.0 | 30.0 |
| debuff_defensive | 5.0 | 15.0 | 30.0 |
| speed_up | 5.0 | 15.0 | 25.0 |
| speed_down | 5.0 | 15.0 | 25.0 |

## Aggregate caps (pct)
- Aggregate offensive debuff cap: **40.0%**
- Aggregate defensive debuff cap: **40.0%**
- Aggregate speed cap: **30.0%**

## Mode caps
- PvP stricter multiplier: **0.75**
- Boss/endgame guard multiplier: **0.50**
- Campaign default: 1.0

## Stacking policy
- Same family, same target: **strongest_wins**.
- Different family, same target: additive entro aggregate cap.
- Max simultaneous active statuses per unit: **4**.
- Opposing pairs cancel: `(speed_up, speed_down)`, `(buff_offensive, debuff_offensive)`, `(buff_defensive, debuff_defensive)`.

## Decay/duration policy
- Default duration: 3 round.
- Min/max duration: 1-6 round.
- Decay curve: lineare per round, calcolata solo all'inizio del round.

## Side effects
Nessuno. Nessun formula change, nessun runtime touch, nessun DB write.
