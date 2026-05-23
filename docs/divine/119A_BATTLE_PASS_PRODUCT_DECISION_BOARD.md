# 119A — V5 BLOCK A — BATTLE PASS PRODUCT DECISION BOARD (BP_D1/D3/D4)

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V5`  
**Block**: A — `PRODUCT_DECISION_BOARD_REVIEW_BATTLE_PASS_BP_D1_BP_D3_BP_D4`  
**Verdict**: 🟢 `BLOCK_A_BP_PRODUCT_DECISION_BOARD_READY`  
**Modalità**: DOC/AUDIT DECISION BOARD ONLY

---

## 1. Context summary

- **BP_D2**: ✅ chiusa (V4 BLOCK_B → `BATTLE_PASS_PREMIUM_ACCOUNT_WIDE_CANONICAL_V1`)
- **V4 BLOCK_A technical hardening**: deferito a causa di BP_D1 + doc shape + live index

---

## 2. BP_D1 — Progress scope

| Opzione | Pros | Cons | DB migration | Hardening unlocked |
|---|---|---|---|---|
| **BP_D1_OPT_A** `ACCOUNT_WIDE` | Default attuale; UX semplice; BP_D2 coerente | Multi-server faster progression | ❌ No | ✅ Yes |
| **BP_D1_OPT_B** `PER_SERVER` | Engagement fair per-server; anti-grinding | Migration richiesta; inconsistente con BP_D2 | ✅ Yes | ❌ No |

**Recommendation**: 🟢 **`BP_D1_OPT_A` (ACCOUNT_WIDE)** — strength **medium-strong**.

**Rationale**: Coerente con BP_D2 ACCOUNT_WIDE_ONCE (V4 canonical). Evita DB migration. Anti multi-server grinding si indirizza via daily caps server-bound (già FREE_SERVER_BOUND classification dei daily_claims).

---

## 3. BP_D3 — Claim scope (gated by BP_D1)

| Opzione | Requires |
|---|---|
| **BP_D3_OPT_A** `ACCOUNT_WIDE_ONCE` | BP_D1=ACCOUNT_WIDE |
| **BP_D3_OPT_B** `PER_SERVER` | BP_D1=PER_SERVER |

**Recommendation**: 🟢 **`BP_D3_OPT_A` (ACCOUNT_WIDE_ONCE)** — coerente con BP_D1 raccomandato.

---

## 4. BP_D4 — Season scope

| Opzione | Pros | Cons |
|---|---|---|
| **BP_D4_OPT_A** `GLOBAL_SEASON` | Operazionalmente semplice; event hub globale; default | Server lanciato a metà non parte da S1 |
| **BP_D4_OPT_B** `PER_SERVER_SEASON` | Server nuovo parte da S1 | Cross-server BP_D2 ambiguity; catalog complexity |

**Recommendation**: 🟢 **`BP_D4_OPT_A` (GLOBAL_SEASON)** — strength **medium**.

---

## 5. Implementation consequences

### Se tutte le raccomandazioni accettate (A/A/A)

- Unlocks: **V4 BLOCK_A technical hardening** (4 LOC su `economy.py:158` → `$setOnInsert`)
- Index `(user_id, season)` su `battle_pass` → richiede ops pack DB-create-index dedicato
- **NESSUNA DB migration**

### Se BP_D1=PER_SERVER

- Introduce DB migration battle_pass split
- BP_D3 forzato PER_SERVER
- BP_D2 cross-server policy TBD

---

## 6. Verdict

🟢 **`BLOCK_A_BP_PRODUCT_DECISION_BOARD_READY`**

**Next action**: board signoff dei 3 recommendation; quando firmati, sbloccare V4 BLOCK_A hardening in pack dedicato.
