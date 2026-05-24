# 140F — PROJECT_R Track F: Status Second-Slice Rollback & Kill-Switch Design

## Verdict
`TRACK_F_STATUS_SECOND_SLICE_ROLLBACK_AND_KILL_SWITCH_DESIGN_READY`

## Marker JSON
`/app/data/design/status_effects/project_r_status_second_slice_rollback_killswitch_v1.json`

## Validator
`/app/backend/scripts/validate_project_r_status_second_slice_rollback_killswitch_v1.py` → **[PASS]**

## Flag futuro proposto
- **Nome**: `STATUS_RUNTIME_SECOND_SLICE_ENABLED`
- **Default**: `false`
- **Persisted nel `.env` live in questo pack**: **NO** ✅
- Audit indipendente: `STATUS_RUNTIME_SECOND_SLICE_ENABLED` non e' presente in `/app/backend/.env` ✅

## Kill-switch strategy
- Emergency: `STATUS_RUNTIME_SECOND_SLICE_ENABLED=false`.
- Effetto disabilitato: resolver ritorna empty deltas; prefight seam = no-op; payload envelope assente.
- Rollback time target: **≤ 60s**.
- Non richiede DB revert.
- Non richiede redeploy.
- **Single env var flip**.

## Staged rollout path (6 fasi)
1. Design (Project R) — questo pack.
2. Pure resolver (Project S).
3. Single-point wiring behind flag (Project T).
4. Canary 1% (Project U).
5. Dev-live 100% (Project V).
6. Prod 1% → 5% → 25% → 100% (Project W, gated su firme prod).

## Firme prod richieste per enable persistente
1. `PROD_ROLLOUT_USER_APPROVAL`
2. `PROD_ROLLOUT_QA_APPROVAL`
3. `PROD_ROLLOUT_OPS_APPROVAL`
4. `PROD_ROLLOUT_ROLLBACK_OWNER_APPROVAL`
5. `PROD_ROLLOUT_BALANCE_APPROVAL`
6. `STATUS_RUNTIME_SECOND_SLICE_PROD_OK`

## Side effects
Nessuno. `env_flag_created_in_live_env = false`, `db_writes = false`.
