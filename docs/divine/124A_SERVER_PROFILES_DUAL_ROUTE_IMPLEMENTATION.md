# 124A — PROJECT_B Track A — SERVER_PROFILES_DUAL_ROUTE_IMPLEMENTATION

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_B`  
**Track**: A  
**Mode**: `inert_flag_gated_skeleton_runtime_off_by_default`  
**Verdict**: 🟢 `TRACK_A_SERVER_PROFILES_DUAL_ROUTE_SKELETON_APPLIED_SAFE`

---

## 1. Scopo

Introdurre il primo **skeleton di contratto** per la dual-route SLC-H designata in V8 BLOCK_D. Le 2 route (`GET` + `POST /api/server-profiles/select`) sono **registrate** ma **inerti**: ogni chiamata restituisce HTTP 503 con payload `status=disabled` finche' il feature flag `SERVER_PROFILES_RUNTIME_ENABLED` non viene attivato (che in V_B NON viene attivato).

## 2. Architettura inert

```
client → GET/POST /api/server-profiles/select
         ↓
  if SERVER_PROFILES_RUNTIME_ENABLED != "true":
         → HTTP 503 { status: "disabled", phase: "PROJECT_B_TRACK_A_INERT_SKELETON", ... }
  else:
         → HTTP 503 { status: "flag_on_but_implementation_deferred", ... }  # ancora inert
         (la logica reale viene introdotta in un pack di implementazione successivo)
```

## 3. Files changed

| File | Modifica | LOC |
|---|---|---|
| `/app/backend/routes/server_profiles.py` | **NEW** — modulo inert con 2 route flag-gated | +84 |
| `/app/backend/server.py` | +6 — import + `app.include_router(server_profiles_router)` | +6 |

**Total runtime files toccati**: 2 (1 new + 1 additive include).

## 4. Smoke verification (live)

| Endpoint | Atteso | Risultato |
|---|---|---|
| `GET /api/server-profiles/select` | 503 + `status=disabled` | ✅ 503, disabled |
| `POST /api/server-profiles/select` | 503 + `status=disabled` | ✅ 503, disabled |
| `GET /api/heroes` | 100 | ✅ 100 (invariato) |
| `GET /api/heroes/primordial_gaia` | 404 | ✅ 404 |

## 5. Invarianti preservate

| Invariante | Status |
|---|---|
| `SERVER_PROFILES_RUNTIME_ENABLED` | ❌ **unset** |
| `users.server` field | ✅ invariato (no migration, no backfill) |
| Legacy `POST /api/server/select` behavior | ✅ invariato |
| `server_profiles` collection doc count | **0** (resta inert da V_A Track A) |
| DB writes in Track A | **0** |
| Frontend changes | **0** |

## 6. Rollback

- **Path**: `/app/backend/scripts/rollback_project_b_server_profiles_dual_route.py`
- **Gating env**: `PROJECT_B_TRACK_A_ROLLBACK=YES`
- **Comportamento**: rimuove il blocco import+include da `server.py` e cancella `routes/server_profiles.py`. Idempotente. Richiede `supervisorctl restart backend` per finalizzare.

## 7. Validator

- **Path**: `/app/backend/scripts/validate_project_b_server_profiles_dual_route.py`
- **Suite task_id**: `PROJECT-B-TRACK-A-SERVER-PROFILES-DUAL-ROUTE` (OPTIONAL)
- **Type**: HTTP smoke + source check
- **Verifiche**: 503 GET/POST, payload disabled, feature flag unset in env, heroes=100, server.py wired

## 8. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| Active server switching | ❌ No |
| POST create/select live behavior | ❌ No (sempre 503) |
| Second server opening | ❌ No |
| Feature flag enable | ❌ No (unset) |
| DB writes | ❌ No (0) |
| Frontend/UI | ❌ No |

## 9. Cosa sblocca

- Phase 2 dual-route compat (V8 BLOCK_D design) ha ora il **contract surface** disponibile.
- Implementation pack futuro (`SERVER_PROFILES_DUAL_ROUTE_BEHAVIOR_PACK`) puo' attivare il flag e iniettare la logica dietro lo skeleton senza ulteriori modifiche al routing.
