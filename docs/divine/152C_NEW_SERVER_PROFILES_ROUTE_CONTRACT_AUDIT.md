# 152C — Track C: New `server_profiles` Route Contract Audit

**Verdict:** `TRACK_C_NEW_SERVER_PROFILES_ROUTE_CONTRACT_AUDIT_READY` · audit-only

## Route file
- `/app/backend/routes/server_profiles.py`
- MD5: `7c12a8d1fc1e1b6a9e63cacfab5c14f4`
- Prefix: `/api/server-profiles`

## Endpoints
| endpoint | flag OFF | flag ON | mutation |
|---|---|---|---|
| GET `/select` | **503** `{status:'disabled'}` | read-only envelope | NO |
| POST `/select` | **503** | read-only envelope (`mutation_executed:false`) | **NO (inert by design)** |

## Feature flags
- **Primary**: `SERVER_PROFILES_RUNTIME_ENABLED` (default OFF → 503).
- **Secondary**: `SERVER_PROFILES_PREVIEW_ENABLED` (double-gate; preview env solo se RUNTIME ON).

Stato corrente: **entrambi i flag NOT set** (verificato via 503 sui due endpoint).

## Data model
- Collection: `server_profiles` (0 doc assumed).
- Indici unique necessari per il live: `(user_id, is_archived)`.

## Safety vs legacy
- Mai muta `users.server`.
- Doppio flag-gate previene attivazione accidentale.
- Archive flag per rollback safe.
- Auth non ancora wired — da aggiungere PRIMA del flag flip.

## Risk: LOW (nello stato attuale inerte)
