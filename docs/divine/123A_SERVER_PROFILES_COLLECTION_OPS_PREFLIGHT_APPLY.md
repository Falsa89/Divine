# 123A — PROJECT_A Track A — SERVER_PROFILES_COLLECTION_OPS_PREFLIGHT_APPLY

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_A`  
**Track**: A  
**Mode**: `ops_apply_idempotent_inert_no_runtime`  
**Verdict**: 🟢 `TRACK_A_SERVER_PROFILES_COLLECTION_APPLIED_SAFE`  
**Rollback ID**: `project_a_track_a_server_profiles_collection_20260524T150000Z`

---

## 1. Scopo

Applicare in **modalita' ops live** ma **inert** la creazione della collezione `server_profiles` + 3 indici canonical, riutilizzando il contratto definito in V6 BLOCK_C / V7 BLOCK_C / V8 BLOCK_A. Nessuna runtime activation, nessun endpoint, nessun feature flag.

## 2. Upstream chain

- V6 BLOCK_C: schema proposal (10 fields)
- V7 BLOCK_C: 3 indici canonical definition
- V8 BLOCK_A: collection creation plan + dry-run gated
- **Project A Track A**: **APPLIED** (questo report)

## 3. Pre-flight checks (live)

| Check | Atteso | Valore | Esito |
|---|---|---|---|
| Backend health (`/api/heroes` count) | 100 | 100 | ✅ |
| Mongo reachable | true | true | ✅ |
| `server_profiles` pre-state | ABSENT | ABSENT | ✅ |
| Total collections pre | 40 | 40 | ✅ |

## 4. Applied ops

### Collection

```
db.create_collection('server_profiles')   # action: CREATED (idempotent)
```

### 3 Indici canonical

| Nome | Fields | Unique | Action |
|---|---|---|---|
| `idx_user_server` | `(user_id ASC, server_id ASC)` | ✅ True | CREATED |
| `idx_user_active` | `(user_id ASC, is_archived ASC)` | ❌ False | CREATED |
| `idx_server_active` | `(server_id ASC, is_archived ASC)` | ❌ False | CREATED |

## 5. Post-flight state (live)

| Risorsa | Valore |
|---|---|
| Total collections | **41** (era 40, +1 server_profiles) |
| `server_profiles` present | ✅ True |
| `server_profiles` doc count | **0** (inert) |
| `server_profiles` indexes | `['_id_', 'idx_user_server', 'idx_user_active', 'idx_server_active']` |

## 6. Runtime state (post-apply)

| Aspetto | Valore |
|---|---|
| `SERVER_PROFILES_RUNTIME_ENABLED` | ❌ **unset** (no runtime activation) |
| Endpoint `/api/server-profiles/*` | ❌ **NOT exposed** |
| Backend route files changed | **0** |
| Frontend changes | **0** |
| Data rows written | **0** |

## 7. Smoke post-apply

| Endpoint | Atteso | Risultato |
|---|---|---|
| `GET /api/heroes` | 100 | ✅ 100 |
| `GET /api/heroes/primordial_gaia` | 404 | ✅ 404 |
| `GET /api/heroes/borea` | 200 inert | ✅ 200 |
| `GET /api/heroes/greek_borea` | 200 inert | ✅ 200 |

## 8. Rollback

- **Path**: `/app/backend/scripts/rollback_project_a_server_profiles_collection.py`
- **Gating env**: `PROJECT_A_TRACK_A_ROLLBACK=YES`
- **Idempotente**: ✅ (no-op se collection gia' assente)
- **Safe-only-if-empty**: ABORTA se `server_profiles.count_documents() != 0`
- **Comportamento**: `drop_indexes()` + `drop_collection('server_profiles')`. Marker JSON preservato per history.

## 9. Validator

- **Path**: `/app/backend/scripts/validate_project_a_server_profiles_ops_v1.py`
- **Suite task_id**: `PROJECT-A-TRACK-A-SERVER-PROFILES-OPS` (OPTIONAL)
- **Type**: live read-only check via pymongo (collection presente, 3 indici attesi, unique constraint, 0 docs, runtime flag unset)
- **Esito V_A**: ✅ PASS

## 10. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| SLC-H endpoint implementation | ❌ No |
| Active server switching | ❌ No |
| Second server opening | ❌ No |
| Feature flag enable | ❌ No |
| User migration/backfill | ❌ No |
| Frontend/UI | ❌ No |

## 11. Cosa sblocca

- **V8 BLOCK_D dual-route Phase 2** Phase 2 precondition #1 (server_profiles collection populated for all active users): collection **esiste**, popolamento sara' on-demand al primo login post-implementation.
- Implementation pack futuro `SERVER_PROFILES_DUAL_ROUTE_IMPLEMENTATION_PACK` puo' procedere con `dual_write_phase` design.
- SLC-H readiness: avanza da `PLAN_READY` (V8) a `COLLECTION_LIVE_INERT` (questo).
