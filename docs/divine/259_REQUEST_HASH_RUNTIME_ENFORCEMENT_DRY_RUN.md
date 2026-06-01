# 259 — Request Hash Runtime Enforcement Dry-Run

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_6_DRY_RUN_RUNTIME_INSTRUMENTATION_PACK_v42` · Track A  
**Modalità**: DRY_RUN_RUNTIME_INSTRUMENTATION_NO_LIVE_APPLY  
**Runtime activation**: `false`  
**DB writes**: `0`

### Scopo

Introdurre runtime dry-run del contratto `shared_request_hash_idempotency_contract_v1`
(v41) nelle 8 safety preview route, in modalità **solo response/log**, senza
ledger, senza persistenza, senza live enforcement.

### Utility modulo

`backend/utils/economy_request_hash_dry_run.py`

Funzioni:

- `canonicalize_payload_for_hash(payload, operation_family)` → dict
- `compute_request_hash(payload, operation_family)` → str (sha256 hex, 32 char)
- `compute_server_idempotency_key(payload, operation_family)` → str (sha256 hex, 24 char)
- `build_request_hash_dry_run_envelope(payload, operation_family)` → dict
- `build_config_block()` → dict per `/config`

### Comportamento

- normalizzazione JSON deterministica (keys sorted ascending)
- stripping campi volatili (clock, telemetry, UA)
- stripping campi PII (email, ip, device_id, push_token, phone, ...)
- hash sha256 lowercase hex troncato 32 char (request_hash)
- server_idempotency_key sha256 troncato 24 char
- **no DB writes**, **no persistenza**, **no ledger**, **no live enforcement**

### Wire-up

Le 8 safety preview route ricevono:

1. `/config` (quando flag ON): blocco `request_hash_dry_run` con
   `request_hash_dry_run_enabled=true`, `request_hash_contract`,
   `ledger_write_enabled=false`, `live_enforcement_enabled=false`,
   `db_writes=0`.
2. POST validate / guard / idempotency (quando flag ON): envelope completo
   `request_hash_dry_run` con `request_hash`, `server_idempotency_key_preview`,
   `pii_stripped=true`, `volatile_fields_stripped=true`, `ledger_write_enabled=false`,
   `db_writes=0`.

### Smoke verificato

- 8/8 route con flag OFF: `/config` ritorna `503` come prima (default invariato)
- 8/8 route con flag ON: envelope completo presente, `db_writes=0` ovunque

### Vincoli rispettati

- nessun cambio di endpoint path
- nessun cambio di feature flag
- nessun cambio del default 503
- nessun import di librerie esterne
- nessun DB write
- fallback shim incluso in ogni route (se utils mancante, envelope `enabled=false`)
