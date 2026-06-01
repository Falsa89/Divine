# 262 — MEGA_ECONOMY_SAFETY_ACCELERATION_6 · Public Route Wireup Repair v42b

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_6_PUBLIC_ROUTE_WIREUP_REPAIR_PACK_v42b`  
**Parent v42 commit**: `f23916b59d8699c6b81f8261a7acfd94dcf4b2c3`  
**Modalità**: DRY_RUN_RUNTIME_INSTRUMENTATION_NO_LIVE_APPLY  
**Runtime activation**: `false`  
**DB writes**: `0`

## Motivo

La verifica pubblica GitHub post-v42 ha mostrato che:

- Le utility v42 (`backend/utils/economy_request_hash_dry_run.py` e
  `backend/utils/economy_observability_dry_run.py`) sono **pubbliche e corrette**.
- Diverse safety route v37–v40 hanno il **wire-up pubblico visibile**.
- **MA** due route specifiche risultavano ancora in versione v40-style sul pubblico:
  - `backend/routes/battle_pass_claim_safety_preview.py`
  - `backend/routes/mail_claim_safety_preview.py`

Questo repair pack tocca **solo** queste due route per forzare il refresh
del blob pubblico, allineando il contenuto pubblico a quello locale v42.

## Cosa NON è questo pack

- NON è un suite-runner sync-fix.
- NON abilita live economy.
- NON tocca altre 6 safety route.
- NON tocca utils, server.py, suite runner, frontend, battle_engine.
- NON cambia endpoint path, feature flag, default 503.

## File modificati (solo 2)

- ✏️ `backend/routes/battle_pass_claim_safety_preview.py`
- ✏️ `backend/routes/mail_claim_safety_preview.py`

## File creati

- ➕ `data/design/economy_safety/mega_economy_safety_acceleration_6_public_route_wireup_repair_v42b_marker_v1.json`
- ➕ `docs/divine/262_MEGA_ECONOMY_SAFETY_ACCELERATION_6_PUBLIC_ROUTE_WIREUP_REPAIR_v42b.md` (questo)

## Modifiche puntuali per route

### Battle Pass (`battle_pass_reward_claim`)

- `/config` (flag ON): include `request_hash_dry_run` + `observability_dry_run` blocks (già presenti localmente da v42, riconfermati)
- `/validate-request`, `/guard-plan-preview`, `/idempotency-preview` (flag ON): includono entrambi gli envelope
- **operation_type fallback** quando `payload.operation` mancante: `battle_pass_free_reward_claim`
- **client idempotency key detection**: rileva sia `client_idempotency_key` che `idempotency_key`
- Namespace `/api/battle-pass-claim-safety-preview` invariato
- Feature flag `BATTLE_PASS_CLAIM_SAFETY_PREVIEW_ENABLED` invariato
- Default 503 invariato
- `safety_flags` invariato
- Allowed operation types invariati
- Guard checks invariati

### Mail (`mail_reward_claim`)

- `/config` (flag ON): include `request_hash_dry_run` + `observability_dry_run` blocks (già presenti localmente da v42, riconfermati)
- `/validate-request`, `/guard-plan-preview`, `/idempotency-preview` (flag ON): includono entrambi gli envelope
- **operation_type fallback** quando `payload.operation` mancante: `mail_single_reward_claim`
- **client idempotency key detection**: rileva sia `client_idempotency_key` che `idempotency_key`
- Namespace `/api/mail-claim-safety-preview` invariato
- Feature flag `MAIL_CLAIM_SAFETY_PREVIEW_ENABLED` invariato
- Default 503 invariato
- `safety_flags` invariato (`mail_state_mutation_enabled=false`)
- Allowed operation types invariati
- Guard checks invariati

## Smoke verificato

- Flag OFF: entrambe le route `/config` ritornano `HTTP 503` (default invariato).
- Flag ON: entrambe le route `/config` includono i due blocchi dry-run.
- Flag ON POST `/validate-request`: entrambe ritornano i due envelope dry-run, con
  `operation_type` correttamente fallback e `client_idempotency_key_present=true`
  quando il payload usa `idempotency_key` come chiave alternativa.
- `db_writes=0` ovunque.
- `claim_enabled=false`, `reward_grant_enabled=false` ovunque.

## Verdict atteso

Locale:

```
MEGA_ECONOMY_SAFETY_ACCELERATION_6_PUBLIC_ROUTE_WIREUP_REPAIR_v42b_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

Pubblico (dopo sync):

```
MEGA_ECONOMY_SAFETY_ACCELERATION_6_DRY_RUN_RUNTIME_INSTRUMENTATION_FUNCTIONAL_PUBLIC_CONTENT_VERIFIED_WITH_SUITE_RUNNER_STALE_CAVEAT
```

## Caveat noti

- `SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION` accettato.
