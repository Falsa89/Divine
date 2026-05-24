# 142G — PROJECT_T Track G: Dev Canary RC Gate

## Verdict
`TRACK_G_SECOND_SLICE_DEV_CANARY_RC_GATE_READY`

## Marker JSON
`/app/data/design/project_management/project_t_second_slice_dev_canary_rc_gate_v1.json`

## Validator
`/app/backend/scripts/validate_project_t_second_slice_dev_canary_rc_gate_v1.py` → **[PASS]**

## Next pack
**`PROJECT_U_STATUS_SECOND_SLICE_CANARY_ENV_FLAG_FLIP_PACK`**

Il Pack U eseguirà il **canary env flag flip** in ambiente dev (NON prod) tramite `STATUS_RUNTIME_SECOND_SLICE_ENABLED=true` nel `.env`. **Prod è esplicitamente escluso**.

## Load target (canary)
- Requests/sec: 50
- Durata: 60s
- Endpoint: in-process battle simulate sample fixtures
- Target P95 latency: ≤ 100ms

## No-leak target (canary)
Forbidden payload keys: `status_second_slice_preview` outside dry_run path, `__second_slice_seam_version` in non-preview payloads.
Forbidden backend log keywords: `second_slice_deltas`, `status_second_slice_runtime_seam ERROR`.

## Rollback target
- Rollback time: ≤ 60s.
- Metodo: single env var flip + `sudo supervisorctl restart backend`.
- Script: `/app/backend/scripts/rollback_project_t_status_second_slice_battle_engine_wiring.py` (per restore battle_engine se necessario).

## Env flag in `.env`
**NON flipped** in Pack T. ✅

## Side effects
Nessuno. DB writes: 0.
