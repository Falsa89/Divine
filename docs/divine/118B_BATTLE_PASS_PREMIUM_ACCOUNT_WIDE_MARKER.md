# 118B — V4 BLOCK B — BATTLE PASS PREMIUM ACCOUNT-WIDE CANONICAL MARKER

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V4`  
**Block**: B — `BATTLE_PASS_PREMIUM_ACCOUNT_WIDE_CANONICAL_MARKER`  
**Verdict**: 🟢 `BLOCK_B_BATTLE_PASS_PREMIUM_ACCOUNT_WIDE_MARKER_READY`  
**Modalità**: AUDIT/DOC ONLY (nessun runtime patch)

---

## 1. Regola canonical introdotta

**Rule ID**: `BATTLE_PASS_PREMIUM_ACCOUNT_WIDE_CANONICAL_V1`

> La purchase del Battle Pass premium e l'entitlement `is_premium` sono **ACCOUNT_WIDE_ONCE**. Una sola tx per stagione per account, condivisa tra tutti i server profiles. Allineato con `VIP_PAID_ACCOUNT_WIDE_CANONICAL_V1` (V2 BLOCK_C).

---

## 2. Derivazione

| Sorgente | Valore |
|---|---|
| Audit di origine | V3 BLOCK_B `BATTLE_PASS_PRODUCT_DECISION_AUDIT` |
| Decision ID | **BP_D2** |
| Strength | strong |

---

## 3. Superfici coperte

| ID | Endpoint | Linea | Decisione |
|---|---|---|---|
| BP-S03 | `POST /api/battlepass/buy-premium` | 158 | 🔵 `NO_SERVER_SCOPE_BY_DESIGN` |

---

## 4. Superfici esplicitamente NON coperte da questo marker

| ID | Motivo |
|---|---|
| BP-S01 (auto-init) | Scope dipende da BP_D1 ancora aperto |
| BP-S02 (claim) | Scope dipende da BP_D1 + BP_D3 |
| BP-S04 (add-exp) | Scope dipende da BP_D1 |

---

## 5. Implicazioni implementative

- L'upsert su `battle_pass.is_premium` NON deve ricevere `server_id`.
- La canonical conferma il default attuale: **nessun micro-batch runtime richiesto**.
- Solo il marker canonical è introdotto.

---

## 6. Verdict

🟢 **`BLOCK_B_BATTLE_PASS_PREMIUM_ACCOUNT_WIDE_MARKER_READY`**
