# 102 — SERVER SELECT AUDIT — v102

> Lingua: Italiano.

## Bug device QA (iPhone 13 / Expo Go) post-v101

- App apre /servers (v101 gate OK) ✅
- /servers non mostra lista server selezionabile ❌
- mancano pulsanti Entra/Seleziona ❌
- mancano dettagli server ❌
- impossibile completare flow Login → Server → Home ❌

## File auditati

| File | Stato pre-v102 | Azione v102 |
| --- | --- | --- |
| `frontend/app/servers.tsx` | read-only locked preview, nessuna lista | **REWRITE completo** in UI selezionabile reale |
| `frontend/app/index.tsx` | gate routing v101 OK | confermato funzionante |
| `frontend/app/(tabs)/menu.tsx` | solo "Esci dal gioco" ambiguo | aggiunto **CAMBIA SERVER** + rinominato **LOGOUT ACCOUNT** + bridge logout |
| `frontend/context/AuthContext.tsx` | legacy logout clear token + v101 key | invariato (bridge avviene in menu) |
| `frontend/src/auth/AuthContext.tsx` | v96 OAuth/SecureStore separato | marker import nel bridge logout (unification deferred v103) |
| `backend/routes/server_profiles.py` | GET/POST /select → 503 quando flag OFF | non modificato; frontend usa fallback dichiarato |

## Classificazione

| Risorsa | Status pre-v102 | Status post-v102 |
| --- | --- | --- |
| `frontend/app/servers.tsx` | `read_only_locked` | `selectable` |
| `/api/server-profiles/select` | `backend_source_unavailable_503` | `local_fallback_required` → dichiarato `SERVER PROFILE FALLBACK` |
| Logout button | `logout_incomplete` | `route_ready_v102` |
| AuthContext legacy + v96 | `auth_context_mismatch` | `auth_context_mismatch_bridged` (FULL deferred v103) |

## Blocker pre-v102 risolti

1. `servers.tsx` era read-only locked → **RISOLTO** con rewrite
2. Mancavano pulsanti Entra → **RISOLTO** con card + button per server
3. Mancava write `v101_selected_server_id` su tap → **RISOLTO**
4. Logout ambiguo → **RISOLTO** (LOGOUT ACCOUNT esplicito + CAMBIA SERVER separato)
5. AuthContext senza bridge → **RISOLTO** via bridge logout in menu (FULL unification deferred v103)

## Safety

```
db_destructive_writes              = false
legacy_apply_cleanup               = false
reward_economy_inventory_mutation  = false
token_raw_logs                     = false
provider_secrets                   = false
fake_PASS                          = false
validator_weakening                = false
```
