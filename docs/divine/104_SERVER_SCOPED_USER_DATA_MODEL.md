# v104 — Server-Scoped User Data Model

**Pack**: `MEGA_RELEASE_ACCELERATION_53_v104_SERVER_SCOPED_RUNTIME_DATA_AND_CHAT_ISOLATION_FIX`

## Stato

`DECLARED_PENDING`

Lo schema multi-shard NON è ancora migrato. Le guardrail v104 vietano esplicitamente
*destructive DB writes* e *blind migration*. Questo documento definisce il modello
target e il piano di migrazione safe.

## Modello preferito

**Collection**: `player_server_profiles`
**Primary key composita**: `(account_id, server_id)`

```json
{
  "account_id": "<string>",
  "server_id": "<string>",
  "account_level": 1,
  "roster": [],
  "inventory": {},
  "currencies": {},
  "team_formation": [],
  "story_progress": {},
  "arena_profile": {},
  "created_at": "<iso8601>",
  "last_played_at": "<iso8601>"
}
```

## Indici richiesti

| keys | unique |
|---|---|
| `(account_id, server_id)` | ✅ |
| `(server_id)` | ❌ |
| `(server_id, last_played_at)` | ❌ |

## Piano di migrazione safe

1. Definire collection `player_server_profiles` in staging.
2. Backfill dual-read da `users` collection con `server_id='qa-eu-01'` default S1.
3. Dry-run con observability rollup.
4. Cutover graduale gated da feature flag `server_scoped_runtime_enabled`.
5. Rollback plan documentato prima di apply.

## Runtime contract (finché isolation non è ready)

- `selected_server_id` letto da `AsyncStorage` chiave `v101_selected_server_id`.
- Loader strategy: condividere stato account con banner pending esplicito.
- Banner token obbligatorio: `SERVER_DATA_ISOLATION_BACKEND_PENDING`.
- Nessuna finzione di dati per-server.

## Forbidden

- Destructive DB writes
- Blind migration
- Premium currency grant
- Random starter heroes
- Legacy heroes nel template starter
- Fake per-server profile data

## Hook frontend introdotto

`frontend/src/hooks/useServerScope.ts`

Fornisce a tutti i loader un accesso uniforme a:
- `selected_server_id`
- `selected_server_name`
- `is_isolation_pending` (sempre `true` finché backend non è pronto)
- `isolation_pending_token = 'SERVER_DATA_ISOLATION_BACKEND_PENDING'`
