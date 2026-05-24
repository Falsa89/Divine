# 141A — PROJECT_S Track A: Second-Slice Pure Resolver Spec Lock

## Verdict
`TRACK_A_SECOND_SLICE_PURE_RESOLVER_SPEC_LOCK_READY`

## Marker JSON
`/app/data/design/status_effects/project_s_second_slice_resolver_spec_lock_v1.json`

## Validator
`/app/backend/scripts/validate_project_s_second_slice_resolver_spec_lock_v1.py` → **[PASS]**

## Spec bloccato (da Project R, lift-and-shift)
- **In-scope families (4):** `debuff_offensive`, `debuff_defensive`, `speed_up`, `speed_down`.
- **Excluded families (16):** DoT, Poison, Burn, Bleed, Freeze, Stun, Sleep, Hard CC, Shield, Barrier, HoT, Revive, Immunity, Cleanse, Borea Marchio, Boss special.
- **Stat mapping:**
  - `debuff_offensive` → `atk_pct` (negative)
  - `debuff_defensive` → `def_pct` (negative)
  - `speed_up` → `speed_pct` (positive)
  - `speed_down` → `speed_pct` (negative)
- **Per-status caps (pct):** 30/30/25/25.
- **Aggregate caps (pct):** offensive 40, defensive 40, speed 30.
- **Mode multipliers:** campaign 1.0, pvp 0.75, boss 0.50.

## Hard requirements per il modulo
- Deterministic, side-effect free, no DB/HTTP imports, no battle_engine import, no mutable global state.

## Side effects
Nessuno. `module_created_in_track_a=false`, `runtime_activated=false`.
