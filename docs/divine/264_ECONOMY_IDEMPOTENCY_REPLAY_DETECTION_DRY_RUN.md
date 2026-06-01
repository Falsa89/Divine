# 264 — Economy Idempotency Replay Detection Dry-Run

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_7_DRY_RUN_REPLAY_DETECTION_PACK_v43` · Track A  
**Modalità**: DRY_RUN_RUNTIME_INSTRUMENTATION_NO_LIVE_APPLY  
**Runtime activation**: `false`  
**DB writes**: `0`

## Scopo

Aggiunge un layer dry-run di **replay/conflict detection** per idempotency
alle 8 safety preview route. La detection si basa sul `server_idempotency_key`
e sul `request_hash` già calcolati da v42 (request hash dry-run).

## Utility

`backend/utils/economy_idempotency_replay_detection_dry_run.py`

Funzioni esposte:

- `build_replay_detection_dry_run_envelope(...)` → dict
- `build_config_block()` → dict per `/config`
- `_test_reset(...)`, `_test_snapshot_size()` (solo per test, mai HTTP)

## Detection statuses

| status | quando |
|--------|--------|
| `new_key_preview` | prima volta che vediamo questa idem key (per operation_family) |
| `same_key_same_hash_replay_preview` | stessa idem key, stesso request_hash |
| `same_key_diff_hash_conflict_preview` | stessa idem key, request_hash diverso |
| `missing_key_preview` | nessuna idem key (o nessun hash) fornito |

## Storage

- **In-memory only** (OrderedDict locked con `threading.Lock`)
- **MAX_ENTRIES = 256** (LRU evict-oldest)
- **TTL = 60s** (expire on read/insert)
- **NON condivisa** tra worker (per-process)
- **NON durable** su restart (reset by design)
- **NO DB, NO Redis, NO file**

## Wire-up sulle 8 route

In ogni route:

- `/config` (flag ON) include `idempotency_replay_detection_dry_run` block
- POST endpoint (validate / guard|grant / idempotency) includono envelope
- Riusa `server_idempotency_key` e `request_hash` calcolati da v42
- **Non altera** v42 `request_hash_dry_run` / `observability_dry_run`
- **Non blocca** la preview request neanche su conflict

## Invarianti

- `preview_request_blocked = false` sempre
- `db_writes = 0` sempre
- `persistent_ledger_enabled = false`
- `redis_enabled = false`
- `live_enforcement_enabled = false`
- `not_shared_across_workers = true`
- `not_durable_across_restart = true`

## Smoke verificato

- 4 detection statuses verificati deterministicamente in isolamento
- 8/8 route ON: `/config` espone il replay block; POST `/validate*` espone
  l'envelope con `new_key_preview` (prima chiamata) e
  `same_key_same_hash_replay_preview` (chiamata ripetuta identica)
- 8/8 route OFF: `/config` ritorna `HTTP 503` (default invariato)
- Cache size bounded (LRU): verificato con max_entries=4 e 20 insert → size ≤ 4
- Cross-family: stessa idem key in famiglia diversa → `new_key_preview`

## Nota su conflict via HTTP

Con la derivazione v42 attuale (`server_idempotency_key =
sha256(operation_family|user_id|client_idempotency_key|canonical_payload)`),
la idem key cambia se il payload cambia, quindi il caso
`same_key_diff_hash_conflict_preview` è di fatto non raggiungibile via HTTP
senza una derivazione client-side della idem key indipendente dal payload.
L'utility lo gestisce correttamente in isolamento, copertura riservata
a un possibile v44 (client idem key indipendente dal payload, opt-in).
