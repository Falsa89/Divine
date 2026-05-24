# 120A — V6 BLOCK A — BP_D1/D3/D4 SIGNOFF RECORD

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V6`  
**Block**: A — `BATTLE_PASS_BP_D1_D3_D4_SIGNOFF_RECORD_PACK`  
**Verdict**: 🟢 `BLOCK_A_BP_D1_D3_D4_SIGNOFF_RECORD_READY`  
**Modalità**: DOC/SIGNOFF RECORD ONLY

---

## 1. Source

Raccomandazioni preparate in V5 BLOCK_A board (`119A_BATTLE_PASS_PRODUCT_DECISION_BOARD.md`).

---

## 2. Decisioni firmate

| Decision | Option | Value | Strength |
|---|---|---|---|
| **BP_D1** PROGRESS_SCOPE | BP_D1_OPT_A | 🟢 **ACCOUNT_WIDE** | strong |
| **BP_D3** CLAIM_SCOPE | BP_D3_OPT_A | 🟢 **ACCOUNT_WIDE_ONCE** | strong |
| **BP_D4** SEASON_SCOPE | BP_D4_OPT_A | 🟢 **GLOBAL_SEASON** | medium |

Tutte le decisioni: **`db_migration_required: false`**.

---

## 3. Regole canonical ora attive

1. `BATTLE_PASS_PROGRESS_ACCOUNT_WIDE_CANONICAL_V1`
2. `BATTLE_PASS_CLAIM_ACCOUNT_WIDE_ONCE_CANONICAL_V1`
3. `BATTLE_PASS_GLOBAL_SEASON_CANONICAL_V1`

Si aggiungono a `BATTLE_PASS_PREMIUM_ACCOUNT_WIDE_CANONICAL_V1` (V4 BLOCK_B) e `VIP_PAID_ACCOUNT_WIDE_CANONICAL_V1` (V2 BLOCK_C).

---

## 4. Pack sbloccato post-signoff

### `BATTLE_PASS_TECHNICAL_HARDENING_POST_SIGNOFF_PACK`

- Risolve V4 BLOCK_A `READY_NOT_APPLIED` R3 (dependency su BP_D1).
- Diff atteso: **4 LOC** su `economy.py:158` (`$set` → `$setOnInsert`).
- Prerequisites rimanenti:
  - Esplicita autorizzazione runtime patch (R2 prompt guardrail su response schema)
  - Ops pack DB-create-index dedicato per `(user_id, season)` index (R4)

---

## 5. Impact SLC-H readiness

Chiude l'item V5 BLOCK_D readiness matrix "Battle pass progress/claim/season decision" da `V5_BLOCK_A_BOARD_READY` a **CLOSED**.

---

## 6. Verdict

🟢 **`BLOCK_A_BP_D1_D3_D4_SIGNOFF_RECORD_READY`**
