# 121B — V7 BLOCK_B — BATTLE_PASS_TECHNICAL_HARDENING_POST_SIGNOFF

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V7`  
**Block**: B  
**Mode**: `apply_safe_setoninsert_only`  
**Verdict**: 🟢 `BLOCK_B_BATTLE_PASS_TECHNICAL_HARDENING_POST_SIGNOFF_APPLIED_SAFE`  
**Timestamp**: 20260524T134500Z  
**Rollback ID**: `v7_block_b_battle_pass_hardening_20260524T134500Z`

---

## 1. Scopo

Applicare il technical hardening sul pattern di upsert di `battle_pass` dentro `POST /api/battlepass/buy-premium`, sostituendo il legacy `$set: {is_premium: True}` con la composizione canonica `$setOnInsert + $set` che garantisce **doc shape consistente** su insert (5 default canonici).

Questo e' lo **stesso hardening** che V4 BLOCK_A aveva inquadrato come `READY_NOT_APPLIED` (residui R1/R2/R4); ora **autorizzato** dal signoff record V6 BLOCK_A (BP_D1=ACCOUNT_WIDE, BP_D3=ACCOUNT_WIDE_ONCE, BP_D4=GLOBAL_SEASON).

## 2. Surface patched

| Campo | Valore |
|---|---|
| File | `/app/backend/routes/economy.py` |
| Endpoint | `POST /api/battlepass/buy-premium` |
| Funzione | `buy_premium_pass` |
| Linea pre-patch | 158 |
| Collezione DB | `battle_pass` |

## 3. Diff applicato (10 LOC aggiunte, 1 rimossa)

**Pre (V4 legacy)**:
```python
await db.battle_pass.update_one({"user_id": uid}, {"$set": {"is_premium": True}}, upsert=True)
```

**Post (V7 hardened)**:
```python
# V7 BLOCK_B post-signoff hardening: $set -> $setOnInsert default doc shape.
# Authorized by V6 BLOCK_A signoff record (BP_D1=ACCOUNT_WIDE, BP_D3=ACCOUNT_WIDE_ONCE, BP_D4=GLOBAL_SEASON).
# Behavior preserved: downstream consumers already use .get() with same defaults; doc shape now consistent on insert.
await db.battle_pass.update_one(
    {"user_id": uid},
    {
        "$setOnInsert": {"exp": 0, "level": 1, "claimed_free": [], "claimed_premium": [], "season": 1},
        "$set": {"is_premium": True},
    },
    upsert=True,
)
```

## 4. Cosa NON cambia

| Aspetto | Stato |
|---|---|
| Reward logic (free/premium lanes) | ✅ INVARIATA |
| Cost (500 gemme) | ✅ INVARIATA |
| Error message `Servono {cost} gemme!` | ✅ INVARIATA |
| Response shape (`{"success": True}`) | ✅ INVARIATA |
| Entitlement (is_premium=True) | ✅ INVARIATA |
| Downstream `.get()` con default | ✅ INVARIATO (ora pero' i default sono in DB anche su new insert) |
| Cadence / season cycle | ✅ INVARIATA |
| DB index su `(user_id, season)` | ❌ NON CREATO (deferred a ops pack DB-write dedicato) |

## 5. Residui V4 BLOCK_A indirizzati

| ID | Descrizione | Stato post-V7 |
|---|---|---|
| R1 | doc shape differs | **ADDRESSED** — con BP_D1=ACCOUNT_WIDE la unified doc shape e' il target esplicito |
| R2 | prompt guardrail | **ADDRESSED** — V7 prompt autorizza esplicitamente il patch post-signoff; response invariata |
| R3 | BP_D1 dependency | **CLOSED** via V6 BLOCK_A signoff |
| R4 | index live | **DEFERRED** — index `(user_id, season)` non creato in V7 (richiede ops pack) |

## 6. Validator

- **Path**: `/app/backend/scripts/validate_v7_battle_pass_technical_hardening.py`
- **Type**: read-only (no HTTP, no DB)
- **Suite task_id**: `V7-BLOCK-B-BATTLE-PASS-HARDENING-POST-SIGNOFF` (OPTIONAL)
- **Verifiche chiave**:
  1. Marker integro + `runtime_patch_applied=True`
  2. `$setOnInsert` con i 5 default canonici presenti
  3. `$set: {"is_premium": True}` preservato
  4. `cost = 500` invariato
  5. Ordering `$setOnInsert` prima di `upsert=True`
  6. V6 BLOCK_A signoff record cross-reference esistente
  7. No reward/lane/cost/response/behavior change

## 7. Rollback

- **Path**: `/app/backend/scripts/rollback_v7_battle_pass_technical_hardening.py`
- **Gating**: `V7_BLOCK_B_ROLLBACK=YES`
- **Idempotenza**: ✅ re-run no-op se gia' rolled-back
- **Comportamento**: ripristina il pattern legacy single-line `$set` (no behavior change in entrambe le direzioni). Marker preservato.

## 8. V4 validator V7-aware

Il validator `validate_v4_battle_pass_technical_hardening.py` e' stato **aggiornato** per essere **V7-aware**:
- Se il marker V7 BLOCK_B esiste con `runtime_patch_applied=True`, il validator si aspetta il nuovo pattern `$setOnInsert` e l'apply autorizzato.
- Altrimenti continua a verificare la presenza del pattern legacy (no unauthorized apply).
- Il marker storico V4 (`READY_NOT_APPLIED`) **resta invariato** come record storico.

## 9. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| reward change | ❌ No |
| premium/free lane logic change | ❌ No |
| cost change | ❌ No |
| response schema change | ❌ No |
| DB migration/backfill | ❌ No |
| DB index creation | ❌ No (deferred) |
| Character Bible mutation | ❌ No |
