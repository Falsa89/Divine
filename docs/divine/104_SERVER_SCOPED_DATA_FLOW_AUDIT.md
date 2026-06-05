# v104 — Server-Scoped Data Flow Audit

**Pack**: `MEGA_RELEASE_ACCELERATION_53_v104_SERVER_SCOPED_RUNTIME_DATA_AND_CHAT_ISOLATION_FIX`

## Sintesi

Dopo il QA manuale post-v103 su iPhone 13 / Expo Go, la navigazione server funziona ma
**i dati runtime non sono isolati per server**. Selezionare S1 o S2 mostra lo stesso
profilo, roster, currencies, inventory, team e chat.

Questo documento elenca tutte le superfici di gioco che leggono dati account/game e
classifica lo stato dell'isolamento per `server_id`.

## Verdict

`SERVER_DATA_ISOLATION_BACKEND_PENDING`

La UI dichiara apertamente questo stato tramite banner persistente su `/servers`.
Nessuna finzione di separazione cross-server è introdotta.

## Superfici auditate (13)

| Superficie | reads_selected_server_id | sends_to_backend | backend_filters | fallback_declared | risk |
|---|---|---|---|---|---|
| `/(tabs)/home` | ❌ | ❌ | ❌ | ❌ | NOT_SERVER_SCOPED |
| `/(tabs)/heroes` | ❌ | ❌ | ❌ | ❌ | NOT_SERVER_SCOPED |
| `/inventory` | ❌ | ❌ | ❌ | ❌ | NOT_SERVER_SCOPED |
| `/treasury` | ❌ | ❌ | ❌ | ❌ | NOT_SERVER_SCOPED |
| team formation | ❌ | ❌ | ❌ | ❌ | NOT_SERVER_SCOPED |
| pre-battle/battle | ❌ | ❌ | ❌ | ❌ | NOT_SERVER_SCOPED |
| arena opponents | ❌ | ❌ | ❌ | ❌ | BACKEND_PENDING |
| chat | ❌ | ❌ | ❌ | ❌ | NOT_SERVER_SCOPED |
| bot/server actors | ❌ | ❌ | ❌ | ❌ | BACKEND_PENDING |
| live/event/guild | ❌ | ❌ | ❌ | ❌ | BACKEND_PENDING |
| `/servers` | ✅ | ❌ | ❌ | ✅ | OK |
| auth/session | ✅ | ❌ | ❌ | ✅ | PARTIAL |
| `GET /api/server-profiles/list` | n/a | n/a | n/a | ✅ | OK |

## Obbligo UI

- Banner persistente su `/servers` contenente la stringa letterale `SERVER_DATA_ISOLATION_BACKEND_PENDING`.
- Nessuna finzione di dati per-server.
- Nomi server tutti `[QA] ` prefissati.

## Path forward (post-v104)

Vedere `104_SERVER_SCOPED_USER_DATA_MODEL.md` per la strategia di migrazione safe verso
la collection `player_server_profiles` con chiave composta `(account_id, server_id)`.

## Safety

- `fake_different_server_data = false`
- `fake_production_data = false`
- `fake_PASS = false`
- `validator_weakening = false`
- `db_destructive_writes = false`
