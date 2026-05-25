# 152B — Track B: Legacy Server Endpoint Behavior Audit

**Verdict:** `TRACK_B_LEGACY_SERVER_ENDPOINT_BEHAVIOR_AUDIT_READY` · audit-only

## Endpoints

### `GET /api/servers` (line 188, `routes/economy.py`)
- Auth: NO
- Reads: `db.users.count_documents`
- Writes: —
- Returns: lista server con load percent
- Source: costante `SERVERS` in economy.py

### `POST /api/server/select` (line 206, `routes/economy.py`)
- Auth: **YES** (`get_current_user`)
- Reads: `SERVERS`, `db.users.count_documents`
- Writes: **`db.users.update_one({id, $set:{server}})`** → muta `users.server`
- Validates: 404 server inesistente · 400 maintenance · 400 server pieno
- Deprecation note: `WARNING DEPRECATED /api/server/select … will be removed after SLC-H live wiring`
- Removal plan: `/app/docs/divine/120D_LEGACY_SERVER_SELECT_REMOVAL_PLAN.md`

## Compatibility layer / dual-write
**ASSENTE**. Nessun `server_profiles` write parallelo. Lo switch UI al nuovo endpoint senza compatibility layer porterebbe a diverging state.

## Risk: HIGH
