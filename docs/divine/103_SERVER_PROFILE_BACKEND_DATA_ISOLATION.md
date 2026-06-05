# 103 — SERVER PROFILE BACKEND DATA ISOLATION — v103

> Lingua: Italiano.

## QA feedback iPhone 13 post-v102

- Server list e card OK ✅
- ENTRA porta in Home OK ✅
- CAMBIA SERVER funziona OK ✅
- Server fallback/fake **troppo credibili** (nomi senza [QA]) ❌
- Tutti i server caricano stessi dati account (no isolation) ❌
- LOGOUT ACCOUNT rimbalza brevemente in /servers ❌

## Fix applicati v103

### Backend
- **NEW**: `backend/routes/v103_server_profiles.py` → endpoint `GET /api/server-profiles/list` safe read-only.
- Restituisce 5 server con `is_qa_fallback=true`, `is_production_data=false`, `backend_data_isolation_implemented=false` dichiarati apertamente.
- `backend/server.py` aggiornato con `include_router(v103_server_profiles_router)`.

### Frontend
- `frontend/app/servers.tsx`: tutti i nomi prefissati `[QA]` (Aurora, Crepuscolo, Eclissi, Alba, Nebbia).
- Banner fallback ora dichiara: `⚠️ LISTA SERVER QA/FALLBACK · DATI NON DI PRODUZIONE` + sotto-testo che spiega che isolation backend e' PENDING.

### Server-scoped data isolation
- **NON IMPLEMENTATA** (dichiarata `DECLARED_PENDING`).
- Reason: richiede schema DB multi-shard (account_id + server_id composite key), refactor di tutti gli endpoint `/api/*/me`, migration. **Deferred a v104+**.
- UI dichiara apertamente la natura QA dei profili server per non ingannare l'utente.

## Safety

```
db_destructive_writes              = false
fake_production_server_data        = false
fake_different_per_server_profiles = false
token_raw_logs                     = false
provider_secrets                   = false
fake_PASS                          = false
validator_weakening                = false
```
