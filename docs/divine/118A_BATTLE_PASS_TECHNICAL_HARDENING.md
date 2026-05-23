# 118A — V4 BLOCK A — BATTLE PASS TECHNICAL HARDENING (READY_NOT_APPLIED)

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V4`  
**Block**: A — `BATTLE_PASS_TECHNICAL_HARDENING_PACK`  
**Verdict**: 🟡 `BLOCK_A_BATTLE_PASS_TECHNICAL_HARDENING_READY_NOT_APPLIED`  
**Modalità**: AUDIT-ONLY safe-apply deferred

---

## 1. Target inspected

| Campo | Valore |
|---|---|
| ID | **BP-S03** |
| File | `/app/backend/routes/economy.py` |
| Endpoint | `POST /api/battlepass/buy-premium` |
| Linea | **158** |
| Op | `db.battle_pass.update_one({'user_id': uid}, {'$set': {'is_premium': True}}, upsert=True)` |

Upsert create payload attuale: `{user_id, is_premium}` (mancano i 5 default `exp/level/claimed_free/claimed_premium/season`).

---

## 2. Forma safer ipotizzata

```python
db.battle_pass.update_one(
    {"user_id": uid},
    {
        "$setOnInsert": {"exp": 0, "level": 1, "claimed_free": [], "claimed_premium": [], "season": 1},
        "$set": {"is_premium": True}
    },
    upsert=True
)
```

Diff stimato: **4 LOC**.

---

## 3. Perché READY_NOT_APPLIED

| ID | Motivo |
|---|---|
| **R1_DOC_SHAPE_DIFFERS** | La forma safer crea un doc con 5 default; è un cambio di stato strutturale osservabile in DB. |
| **R2_PROMPT_GUARDRAIL** | Il prompt esplicita 'preserve all battle pass rewards, premium/free behavior, entitlement logic, prices, cadence, and response schema'. |
| **R3_DEPENDS_ON_BP_D1** | V3 BLOCK_B aveva identificato BP_D1 (progress scope) come prerequisito product decision. Hardenare prima cristallizza una specifica forma che potrebbe rendere necessaria DB migration se BP_D1 = PER_SERVER. |
| **R4_INDEX_REQUIRES_LIVE_DB** | L'aggiunta di indici (user_id, season) richiederebbe `create_index` (write su DB) classificabile come 'live index creation that writes to DB' vietata. |

---

## 4. Path alternativo raccomandato

**Nome**: `BATTLE_PASS_TECHNICAL_HARDENING_POST_BP_D1_DECISION`

Prerequisiti:
1. Product decision board signoff BP_D1 (account-wide vs per-server)
2. Esplicita autorizzazione a modificare il doc-shape sull'upsert
3. Approvazione runtime patch DB-create-index (richiede pack ops dedicato)

Diff atteso: 4 LOC su `economy.py:158`.

---

## 5. Verdict

🟡 **`BLOCK_A_BATTLE_PASS_TECHNICAL_HARDENING_READY_NOT_APPLIED`**

Nessun rollback richiesto (nessuna patch applicata).
