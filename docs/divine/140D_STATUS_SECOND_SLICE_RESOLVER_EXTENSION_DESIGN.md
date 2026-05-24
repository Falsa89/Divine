# 140D — PROJECT_R Track D: Status Second-Slice Resolver Extension Design

## Verdict
`TRACK_D_STATUS_SECOND_SLICE_RESOLVER_EXTENSION_DESIGN_READY`

## Marker JSON
`/app/data/design/status_effects/project_r_status_second_slice_resolver_extension_design_v1.json`

## Validator
`/app/backend/scripts/validate_project_r_status_second_slice_resolver_extension_design_v1.py` → **[PASS]**

## File esistenti referenziati (presenti, NON modificati)
- `/app/backend/game_logic/status_first_slice_resolver_pure.py`
- `/app/backend/game_logic/status_prefight_runtime_seam.py`

## Evidence first slice
- Project M Track B: single-point wiring in `battle_engine.py` gated da `STATUS_RUNTIME_BUFF_SLICE_ENABLED`.
- Project N Track B/F: canary flag flip + rollback drill OK.
- Project O Track B/F: dev-live flag flip + rollback drill OK.

## Strategia estensione (design)
- **Preferred layout**: file isolato `/app/backend/game_logic/status_second_slice_resolver_pure.py` — **NON creato** in questo pack.
- **Interface signature**: `resolve_second_slice(unit_stats: dict, active_statuses: list[dict], mode: str) -> dict` (stat_pct_deltas).
- **Determinismo**: pura, nessun I/O, nessun DB, nessun random.
- **Cap enforcement**: applica `per_status_caps` + `aggregate_caps` + `mode_multipliers` da Track B.
- **Interazione con first slice**: il second-slice resolver gira **dopo** il first-slice nel medesimo prefight seam; i deltas sono fusi con regola di cancellazione delle coppie opposte.
- **Flag gating futuro**: `STATUS_RUNTIME_SECOND_SLICE_ENABLED` (default `false`).

## Staged path (6 fasi)
1. Design (Project R) — questo pack.
2. Pure resolver implementation (Project S, separato).
3. Single-point wiring behind flag (Project T).
4. Canary env flip (Project U).
5. Dev-live (Project V).
6. Prod rollout (Project W, richiede tutte le firme `PROD_ROLLOUT_*`).

## Audit indipendente (validator)
- `/app/backend/game_logic/status_second_slice_resolver_pure.py` **non esiste** ✅
- `/app/backend/battle_engine.py` non contiene: `import status_second_slice_resolver_pure`, `STATUS_RUNTIME_SECOND_SLICE_ENABLED` ✅

## Side effects
Nessuno.
