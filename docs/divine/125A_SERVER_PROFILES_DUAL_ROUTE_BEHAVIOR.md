# 125A — PROJECT_C Track A — SERVER_PROFILES_DUAL_ROUTE_BEHAVIOR

**Verdict**: 🟢 `TRACK_A_SERVER_PROFILES_DUAL_ROUTE_BEHAVIOR_APPLIED_FLAG_OFF`

## Scopo
Aggiungere il primo **behavior layer** dietro lo skeleton V_B Track A. Flag `SERVER_PROFILES_RUNTIME_ENABLED` resta **unset** → default live invariato (503 + disabled).

## Behavior helper
`_read_only_select_response_for_user(user_id)`: pure helper che esegue lookup read-only su `server_profiles` (lazy import `server.db`), restituisce envelope inert con `fallback_used=True` quando user_id missing o doc assente. **No DB write**, **no users.server mutation**, **no active server switching**, **no dual-write**.

## Smoke live (flag unset, default state)
| Endpoint | Atteso | Risultato |
|---|---|---|
| GET /api/server-profiles/select | 503 + disabled | ✅ |
| POST /api/server-profiles/select | 503 + disabled | ✅ |
| GET /api/heroes | 100 | ✅ |

## Flag ON path (unit-verified, NOT live in V_C)
Returns 200 envelope `{status: flag_on_behavior_layer_read_only, data: {success:False, fallback_used:True, ...}, mutation_executed:False, active_server_switched:False, dual_write_executed:False}`.

## Invarianti
- `server_profiles` doc count: **0** (invariato)
- `users.server` field: **non toccato**
- DB writes V_C Track A: **0**
- Feature flag: **unset**

## Rollback
`/app/backend/scripts/rollback_project_c_server_profiles_behavior.py` (gated `PROJECT_C_TRACK_A_ROLLBACK=YES`; segnala restore manuale via git).

## Forbidden scope rispettato
active_server_switching ❌, dual_write_db_behavior ❌, actual_server_selection_mutation ❌, feature_flag_enable ❌, users_server_backfill ❌, frontend ❌, second_server ❌.
