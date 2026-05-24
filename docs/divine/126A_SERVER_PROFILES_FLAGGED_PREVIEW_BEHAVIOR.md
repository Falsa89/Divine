# 126A — PROJECT_D Track A — SERVER PROFILES FLAGGED PREVIEW BEHAVIOR

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_D`  
**Verdict**: 🟢 `TRACK_A_SERVER_PROFILES_FLAGGED_PREVIEW_APPLIED_INERT`  
**Rollback**: `/app/backend/scripts/rollback_project_d_server_profiles_flagged_preview.py` (gated `PROJECT_D_TRACK_A_ROLLBACK=YES`)

## Scopo

Aggiungere un helper `_preview_dry_run_envelope` puro dietro **doppio flag** (`SERVER_PROFILES_RUNTIME_ENABLED` AND `SERVER_PROFILES_PREVIEW_ENABLED`) per il futuro path preview/dry-run di server profiles. **Le route GET/POST default NON chiamano questo helper** → default live 503 preservato.

## Doppio flag-gate

| Layer | Flag | Default live |
|---|---|---|
| L1 — Runtime | `SERVER_PROFILES_RUNTIME_ENABLED` | unset (false) |
| L2 — Preview | `SERVER_PROFILES_PREVIEW_ENABLED` | unset (false) |
| Preview-eligible | L1 AND L2 entrambi `true` | **No** |

Finché anche solo uno dei due è OFF, l'envelope preview rimane non-attivato.

## Smoke live (entrambi flag unset)

| Endpoint | Atteso | Risultato |
|---|---|---|
| GET /api/server-profiles/select | 503 + disabled | ✅ |
| POST /api/server-profiles/select | 503 + disabled | ✅ |
| GET /api/heroes | 100 | ✅ |
| GET /api/heroes/primordial_gaia | 404 | ✅ |

## Unit-verification helper preview

Con entrambi flag ON (env locale, non live): `_preview_dry_run_envelope(None)` ritorna envelope con `preview=True`, `dry_run=True`, `mutation_executed=False`, `active_server_switched=False`, `dual_write_executed=False`, `second_server_opened=False`.

## Invarianti

- `server_profiles` count = 0 (immutato)
- `users.server` non toccato
- DB writes V_D Track A = 0
- Default route behavior **invariato** (validator ne fa enforcement)

## Forbidden scope rispettato

Active server switching ❌, dual-write ❌, actual server selection mutation ❌, feature flag enable ❌, users.server backfill ❌, frontend ❌, second server ❌, DB migration ❌.
