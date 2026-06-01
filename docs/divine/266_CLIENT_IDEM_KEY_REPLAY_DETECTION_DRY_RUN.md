# 266 — Client Idem Key Replay Detection Dry-Run

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_8_..._v44` · Track A  
**Modalità**: DRY_RUN_RUNTIME_INSTRUMENTATION_NO_LIVE_APPLY  
**Runtime activation**: `false` · **DB writes**: `0`

## Scopo

Detection parallela a v43 (server-key) basata sulla **client key**. La chiave
di cache include solo `(operation_family, user_id, server_id, client_idempotency_key)`.
L'hash confrontato è il `request_hash` v42 (che include il payload).

## Stati detection

- `new_client_key_preview`
- `same_client_key_same_hash_replay_preview`
- `same_client_key_diff_hash_conflict_preview`
- `missing_client_key_preview`

## Vincoli

- in-memory only, max 256, TTL 60s
- non condivisa tra worker, non durable su restart
- no DB, no Redis, no filesystem, no persistent ledger
- preview request **mai bloccata**
- `live_enforcement_enabled = false`

## Smoke (Material Raid + Battle Pass + Mail)

- POST same CK + same payload → `same_client_key_same_hash_replay_preview` ✅
- POST same CK + DIFFERENT payload → `same_client_key_diff_hash_conflict_preview` ✅ (raggiungibile via HTTP, a differenza di v43 server-key)
- preview request mai bloccata, `db_writes=0`
