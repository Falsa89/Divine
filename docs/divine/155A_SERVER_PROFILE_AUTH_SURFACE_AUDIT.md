# 155A — Server Profile Auth Surface Audit

**Verdict:** `TRACK_A_SERVER_PROFILE_AUTH_SURFACE_AUDIT_READY` · audit-only

## Auth surface esistente
- Helper: `get_current_user` in `/app/backend/server.py` (~line 100)
- Scheme: JWT Bearer (Authorization header)
- Algorithm: HS256 · secret: `JWT_SECRET` env
- Identity lookup: `db.users.find_one({'id': payload.user_id})`
- Errori: 401 (Token mancante / scaduto / invalido / utente non trovato)

## Perché il nuovo POST server_profiles non è ancora pronto
- Router costruito senza `Depends(get_current_user)` iniettato
- 503 flag-gating cortocircuita la richiesta prima di qualsiasi auth check
- Senza auth, un client non autenticato verrebbe servito l'envelope futuro

## Requisiti auth concreti
- GET `/preview` → `Depends(get_current_user)`; ritorna SOLO dati di `current_user`
- POST `/select` → `Depends(get_current_user)`; body NO `user_id`, identità da JWT; mismatch ownership → reject

## Gaps identificati (4)
| Gap | Severity | Blocker flip |
|---|---|---|
| Depends(get_current_user) missing su nuovo POST/GET | HIGH | ✅ |
| Ownership check `server_profile_id` vs `current_user.id` | HIGH | ✅ |
| Rate-limit per user | MEDIUM | ❌ |
| Audit log auth failures | LOW | ❌ |

**Flag flip authorized**: ❌
