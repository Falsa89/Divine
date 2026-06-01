# 263 — MEGA_ECONOMY_SAFETY_ACCELERATION_6 · Observability Param Repair v42c

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_6_OBSERVABILITY_PARAM_REPAIR_PACK_v42c`  
**Parent v42 commit**: `f23916b59d8699c6b81f8261a7acfd94dcf4b2c3`  
**Parent v42b commit**: `59b908685b7c7fa3659e79757470bd94a94e2b53`  
**Modalità**: PUBLIC_CONTENT_REPAIR_OBSERVABILITY_PARAMETER_ONLY  
**Runtime activation**: `false`  
**DB writes**: `0`

## Motivo

La verifica pubblica GitHub post-v42b ha mostrato:

**OK pubblicamente**:
- Battle Pass e Mail route importano/usano le v42 utility
- `/config` include `request_hash_dry_run` + `observability_dry_run`
- POST endpoint includono entrambi gli envelope
- endpoint paths, feature flag, safety flag, default 503 invariati

**Mismatch pubblico residuo**:
1. Il parametro `operation_type` di `_v42_obs_envelope(...)` usa ancora la
   stringa `operation_family` (`battle_pass_reward_claim` / `mail_reward_claim`)
   invece dei fallback specifici (`battle_pass_free_reward_claim` /
   `mail_single_reward_claim`).
2. `client_idempotency_key_present` controlla solo `client_idempotency_key`
   e non rileva `idempotency_key` come chiave alternativa.

Questo pack **estrae** i refinement in **2 helper named** per route,
rendendoli espliciti e stabili nel sorgente pubblico.

## Cosa NON è questo pack

- NON è un suite-runner sync-fix.
- NON abilita live economy.
- NON cambia endpoint path / feature flag / default 503 / safety flag.
- NON tocca utils, server.py, suite runner, altre 6 route, frontend.

## File modificati (solo 2)

- ✏️ `backend/routes/battle_pass_claim_safety_preview.py`
- ✏️ `backend/routes/mail_claim_safety_preview.py`

## File creati

- ➕ `data/design/economy_safety/mega_economy_safety_acceleration_6_observability_param_repair_v42c_marker_v1.json`
- ➕ `docs/divine/263_MEGA_ECONOMY_SAFETY_ACCELERATION_6_OBSERVABILITY_PARAM_REPAIR_v42c.md` (questo)

## Helper named aggiunti per route

### Battle Pass

```python
def _v42_operation_type(req: Dict[str, Any]) -> str:
    if isinstance(req, dict):
        return str(req.get("operation_type") or req.get("operation") or "battle_pass_free_reward_claim")
    return "battle_pass_free_reward_claim"


def _v42_client_idempotency_key_present(req: Dict[str, Any]) -> bool:
    return bool(
        isinstance(req, dict)
        and (req.get("client_idempotency_key") or req.get("idempotency_key"))
    )
```

### Mail

Identici, fallback `mail_single_reward_claim`.

## Call sites aggiornati

Ogni `_v42_obs_envelope(...)` in ciascuno dei 3 endpoint POST
(`validate-request`, `guard-plan-preview`, `idempotency-preview`) di entrambe
le route passa ora:

```python
"<operation_family>",
_v42_operation_type(req),         # <-- via helper named
"<route_suffix>",
...
client_idempotency_key_present=_v42_client_idempotency_key_present(req),  # <-- via helper named
```

Totale: **6 chiamate** `_v42_operation_type(req)` (3 BP + 3 Mail) +
**6 chiamate** `_v42_client_idempotency_key_present(req)` (3 BP + 3 Mail).

## Smoke verificato

- Flag OFF: entrambe le route `/config` ritornano `HTTP 503` (default invariato).
- Flag ON `/config`: include sia `request_hash_dry_run` sia `observability_dry_run`.
- Flag ON POST `/validate-request` con payload privo di `operation`/`operation_type`:
  - Battle Pass: `audit_event.operation = "battle_pass_free_reward_claim"` ✅
  - Mail: `audit_event.operation = "mail_single_reward_claim"` ✅
- Flag ON POST con `idempotency_key` (NON `client_idempotency_key`):
  - Battle Pass: `client_idempotency_key_present = true` ✅
  - Mail: `client_idempotency_key_present = true` ✅

## Validator results

Tutti i 3 validator v42 ancora PASS:

- `validate_request_hash_runtime_enforcement_dry_run_v1.py` → PASS
- `validate_economy_observability_runtime_dry_run_v1.py` → PASS
- `validate_mega_economy_safety_acceleration_6_v42_rollup.py` → PASS

Suite master: `pass=744, fail=18, miss=0` (identica a v42b).

## Verdict

Locale:

```
MEGA_ECONOMY_SAFETY_ACCELERATION_6_OBSERVABILITY_PARAM_REPAIR_v42c_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

Pubblico (atteso dopo sync):

```
MEGA_ECONOMY_SAFETY_ACCELERATION_6_DRY_RUN_RUNTIME_INSTRUMENTATION_FUNCTIONAL_PUBLIC_CONTENT_VERIFIED_WITH_SUITE_RUNNER_STALE_CAVEAT
```

## Caveat noti

- `SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION` accettato.
