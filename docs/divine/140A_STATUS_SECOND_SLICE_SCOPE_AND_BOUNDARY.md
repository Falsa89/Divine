# 140A — PROJECT_R Track A: Status Second-Slice Scope & Boundary

## Verdict
`TRACK_A_STATUS_SECOND_SLICE_SCOPE_AND_BOUNDARY_READY`

## Marker JSON
`/app/data/design/status_effects/project_r_status_second_slice_scope_v1.json`

## Validator
`/app/backend/scripts/validate_project_r_status_second_slice_scope_v1.py` → **[PASS]**

## Scope second-slice (4 famiglie)
- `debuff_offensive`
- `debuff_defensive`
- `speed_up`
- `speed_down`

## Esplicitamente esclusi
DoT, Poison, Burn, Bleed, Freeze, Stun, Sleep, Hard CC, Shield, Barrier, HoT, Revive, Immunity/Cleanse runtime, **Borea Marchio live logic**, Boss-special status logic.

## Boundary rules
- Nessun tick loop.
- Nessun DoT/HoT.
- Nessun hard CC.
- Nessun shield/barrier.
- Second slice opera su **stat-multiplier deltas applied pre-fight** (coerente col seam pattern della first slice).

## Relazione con la first slice
- First slice: `buff_offensive`, `buff_defensive`.
- Second slice: `debuff_offensive`, `debuff_defensive`, `speed_up`, `speed_down`.
- Overlap: nessuno (ortogonali).
- Flag first-slice (`STATUS_RUNTIME_BUFF_SLICE_ENABLED`): invariato.

## Side effects
Nessuno. `battle_engine_touched=false`, `battle_core_touched=false`, `frontend_touched=false`, `db_writes=false`.
