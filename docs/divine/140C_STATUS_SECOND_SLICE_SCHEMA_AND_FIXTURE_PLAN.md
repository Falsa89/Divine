# 140C — PROJECT_R Track C: Status Second-Slice Schema & Fixture Plan

## Verdict
`TRACK_C_STATUS_SECOND_SLICE_SCHEMA_AND_FIXTURE_PLAN_READY`

## Marker JSON
`/app/data/design/status_effects/project_r_status_second_slice_schema_fixture_plan_v1.json`

## Validator
`/app/backend/scripts/validate_project_r_status_second_slice_schema_fixture_plan_v1.py` → **[PASS]**

## Schema v1 — campi richiesti (10)
`status_id`, `family`, `stat_target`, `sign`, `duration_rounds`, `stacking_rule`, `caps`, `source`, `mode_constraints`, `is_runtime_active`.

## Canonical fixtures (8, tutte `is_runtime_active = false`)
| status_id | family | stat_target | sign | dur | source |
|---|---|---|---|---:|---|
| st_debuff_off_minor | debuff_offensive | atk_pct | negative | 3 | skill |
| st_debuff_off_major | debuff_offensive | atk_pct | negative | 2 | skill |
| st_debuff_def_minor | debuff_defensive | def_pct | negative | 3 | skill |
| st_debuff_def_major | debuff_defensive | def_pct | negative | 2 | skill |
| st_speed_up_minor | speed_up | speed_pct | positive | 3 | skill |
| st_speed_up_major | speed_up | speed_pct | positive | 2 | skill |
| st_speed_down_minor | speed_down | speed_pct | negative | 3 | skill |
| st_speed_down_major | speed_down | speed_pct | negative | 2 | skill |

Ogni fixture porta i caps di Track B (per_status_max_pct + aggregate_family_max_pct) e i mode_constraints (PvP 0.75, boss 0.50).

## Side effects
Nessuno. `resolver_implemented = false`, `db_writes = false`.
