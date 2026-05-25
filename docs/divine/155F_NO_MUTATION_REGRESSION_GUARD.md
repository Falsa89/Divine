# 155F — No-Mutation Regression Guard

**Verdict:** `TRACK_F_SERVER_PROFILES_NO_MUTATION_REGRESSION_GUARD_READY`

## Scan live
- Scope: `/app/frontend/app`, `/app/frontend/components`, `/app/frontend/utils`
- Pattern proibiti: `/api/server/select`, `selectServer`, `select_server`, `Server Selezionato`
- Hits totali: **0**

## API smoke
- GET/POST `/api/server-profiles/select` = **503** ✅

## Feature flags
- RUNTIME/PREVIEW: unset/false ✅
- DUAL_WRITE: not introduced ✅

## File invariants
- servers.tsx MD5 `4e08d0186ed31785e912b8f69d30e9cb` (invariato dal pack precedente)
- menu.tsx MD5 `f3108ff37a15e910c8595ecd9ea56b03`

## DB state
- writes_executed: 0 · users.server writes: 0 · server_profiles writes: 0
