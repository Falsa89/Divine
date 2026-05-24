# 140E — PROJECT_R Track E: Status Second-Slice Payload & No-Leak Plan

## Verdict
`TRACK_E_STATUS_SECOND_SLICE_PAYLOAD_AND_NO_LEAK_PLAN_READY`

## Marker JSON
`/app/data/design/status_effects/project_r_status_second_slice_payload_no_leak_plan_v1.json`

## Validator
`/app/backend/scripts/validate_project_r_status_second_slice_payload_no_leak_plan_v1.py` → **[PASS]**

## Audit live (HTTP GET su localhost:8001)
Endpoint auditati:
- `/api/heroes`
- `/api/heroes/borea`
- `/api/heroes/greek_borea`
- `/api/server-profiles/select`
- `/api/housing/preview`

Forbidden keys cercate: `second_slice_active`, `second_slice_deltas`, `debuff_offensive_runtime`, `debuff_defensive_runtime`, `speed_up_runtime`, `speed_down_runtime`, `status_second_slice_preview`.

**Leak rilevati: 0** ✅

## Envelope payload futuro (design)
- Key name: `status_second_slice_preview`.
- Emission rule: solo quando `STATUS_RUNTIME_SECOND_SLICE_ENABLED=true` AND `?preview=second_slice` AND user in canary cohort.
- Schema: `{deltas, caps_applied, mode, preview_only, deterministic}`.
- `never_present_when_flag_off = true`.
- `never_present_in_battle_log = true`.

## Side effects
Nessuno. `frontend_touched = false`, `db_writes = false`.
