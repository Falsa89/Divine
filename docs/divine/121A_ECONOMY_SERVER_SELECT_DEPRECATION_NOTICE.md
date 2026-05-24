# 121A — V7 BLOCK_A — ECONOMY_SERVER_SELECT_DEPRECATION_NOTICE

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V7`  
**Block**: A  
**Mode**: `apply_safe_logging_only`  
**Verdict**: 🟢 `BLOCK_A_ECONOMY_SERVER_SELECT_DEPRECATION_NOTICE_APPLIED_SAFE`  
**Timestamp**: 20260524T134500Z  
**Rollback ID**: `v7_block_a_server_select_deprecation_20260524T134500Z`

---

## 1. Scopo

Introdurre un **WARNING-level deprecation log** sull'endpoint legacy `POST /api/server/select` definito in `/app/backend/routes/economy.py` come **Phase 1** del removal plan formalizzato in `120D_LEGACY_SERVER_SELECT_REMOVAL_PLAN.md` (V6 BLOCK_D, piano 4-fasi).

## 2. Surface patched

| Campo | Valore |
|---|---|
| File | `/app/backend/routes/economy.py` |
| Endpoint | `POST /api/server/select` |
| Funzione | `select_server` |
| Linea pre-patch | 196 |
| Tipo | runtime patch — logging only |

## 3. Diff applicato (8 LOC aggiunte)

```python
@router.post("/server/select")
async def select_server(req: SelectServerRequest, current_user: dict = Depends(get_current_user)):
    # V7 BLOCK_A DEPRECATION NOTICE (legacy endpoint; superseded by SLC-H server-profiles when live).
    # See: /app/docs/divine/120D_LEGACY_SERVER_SELECT_REMOVAL_PLAN.md (4-phase removal plan, phase 1).
    # Behavior unchanged; passive warning only.
    import logging as _logging
    _logging.getLogger("divine.deprecation").warning(
        "DEPRECATED /api/server/select called by user_id=%s server_id=%s; "
        "will be removed after SLC-H live wiring per LEGACY_SERVER_SELECT_REMOVAL_PLAN v1",
        current_user.get("id"), req.server_id,
    )
    # ... logica selezione SERVERS invariata ...
```

## 4. Cosa NON cambia

| Aspetto | Stato |
|---|---|
| Selection logic (`SERVERS` lookup) | ✅ INVARIATA |
| Status code 200/404/maintenance | ✅ INVARIATI |
| Response schema | ✅ INVARIATA |
| Side effects (DB read/write) | ✅ INVARIATI (nessuno) |
| Permission/auth contract | ✅ INVARIATO |
| Removal phase | ❌ NON eseguita (solo Phase 1 di 4) |

## 5. Validator

- **Path**: `/app/backend/scripts/validate_v7_economy_server_select_deprecation.py`
- **Type**: read-only (no HTTP, no DB)
- **Suite task_id**: `V7-BLOCK-A-ECONOMY-SERVER-SELECT-DEPRECATION` (OPTIONAL)
- **Verifiche**:
  1. Marker JSON integro + verdict corretto
  2. Commento `V7 BLOCK_A DEPRECATION NOTICE` presente
  3. Logger `divine.deprecation` cablato
  4. Stringa `DEPRECATED /api/server/select` presente
  5. Route definition e funzione `select_server` non rimosse
  6. Logica `next((s for s in SERVERS ...))` non alterata
  7. Forbidden scope rispettato (no behavior change, no removal, no schema change, no DB write)
  8. Cross-reference doc removal plan presente

## 6. Rollback

- **Path**: `/app/backend/scripts/rollback_v7_economy_server_select_deprecation.py`
- **Gating**: `V7_BLOCK_A_ROLLBACK=YES`
- **Idempotenza**: ✅ re-run no-op se gia' rolled-back
- **Comportamento**: rimuove il blocco logging mantenendo il resto della funzione `select_server` intatto. Marker JSON preservato per history.

## 7. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| endpoint behavior change | ❌ No |
| endpoint removal | ❌ No |
| response shape change | ❌ No |
| DB write/migration | ❌ No |
| frontend change | ❌ No |

## 8. Cosa sblocca

Fase 2 del removal plan (`dual-route` mediante `/api/v2/server/select` o equivalente) puo' essere pianificata in pack futuro **dopo** che la metrica di chiamate legacy sara' osservabile via il log `divine.deprecation`.
