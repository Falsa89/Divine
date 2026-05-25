# 155D — Data Model Gap & Seed Preconditions

**Verdict:** `TRACK_D_SERVER_PROFILE_DATA_MODEL_GAP_AND_SEED_PRECONDITIONS_READY` · design-only

## Stato attuale
- `server_profiles`: 0 doc (assumed)
- `users.server`: string|null
- Mapping `users ↔ server_profile_id`: **NON ESISTE**
- Indici unique: **NON VERIFICATI/CREATI**

## Data model proposto `server_profiles`
```
{ _id, id, user_id, server_id, server_name_snapshot,
  is_archived, account_level, account_progress{xp,power},
  last_played_at, created_at, updated_at }
```

## Indici
- `(user_id, server_id, is_archived)` **UNIQUE** — `uq_user_server_archive`
- `(user_id, last_played_at)` — `ix_user_last_played`
- `(user_id)` — `ix_user`

## Users collection delta
- mantieni `users.server` durante dual-write
- aggiungi futuro `users.active_server_profile_id`
- deprecazione `users.server` post grace

## Preconditions seed (6)
1. collection writable (auth seed pack)
2. unique index presente
3. upsert idempotente su `(user_id, server_id, is_archived=false)`
4. ogni doc reversibile via `(user_id, server_id, created_at)`
5. nessuna scrittura concorrente su `users.server` (locked UI garantisce)
6. snapshot `server_name` al backfill

## Rollback safe seed (5)
phase 0 dry-run → phase 1 backfill + audit log → phase 2 verify counts → phase 3 store seed_id → rollback per seed_id

## Orphan prevention
Non flippare RUNTIME prima del seed. Fallback su `users.server` se profile missing. Solo "Available" se utente senza nulla.
