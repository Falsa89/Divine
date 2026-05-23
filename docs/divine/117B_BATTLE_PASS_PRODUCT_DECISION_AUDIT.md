# 117B — V3 BLOCK B — BATTLE PASS PRODUCT DECISION AUDIT

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V3`  
**Block**: B — `BATTLE_PASS_PRODUCT_DECISION_AUDIT`  
**Verdict**: 🟢 `BLOCK_B_BATTLE_PASS_PRODUCT_DECISION_AUDIT_READY`  
**Modalità**: AUDIT/DOC ONLY

---

## 1. Battle Pass surfaces ispezionate (4)

| ID | Endpoint | Linea | Collection | Op |
|---|---|---|---|---|
| BP-S01 | `GET /api/battlepass` | 106 | battle_pass | insert (auto-init) |
| BP-S02 | `POST /api/battlepass/claim/{level}` | 146 | battle_pass + users | update |
| BP-S03 | `POST /api/battlepass/buy-premium` | 157 | users + battle_pass | update + upsert |
| BP-S04 | `POST /api/battlepass/add-exp` | 166 | battle_pass | insert + update |

---

## 2. Decision matrix (4 product decisions)

| ID | Question | Default | Recommendation |
|---|---|---|---|
| **BP_D1** | Progress account-wide o per-server? | ACCOUNT_WIDE | da decidere (impatta BP-S01, BP-S04) |
| **BP_D2** | Premium purchase account-wide o per-server? | ACCOUNT_WIDE_ONCE | 🟢 **ACCOUNT_WIDE_ONCE** (strong) — coerente con `VIP_PAID_ACCOUNT_WIDE_CANONICAL_V1` |
| **BP_D3** | Claim rewards account-wide o per-server? | ACCOUNT_WIDE_ONCE | Dipende da BP_D1 |
| **BP_D4** | Season globale o per-server? | GLOBAL_SEASON | da decidere |

---

## 3. Separazione technical vs product

### Technical-only (sicuri post-decision)
- L'upsert pattern di BP-S03 (linea 157) usa `$set` invece di `$setOnInsert` (già notato in V1 BLOCK_A)
- Mancanza di indici `(user_id, season)` su `battle_pass`
- `battle_pass.season` hardcoded a 1 nel default doc

### Product-decision-required
- BP_D1 (progress scope)
- BP_D2 (premium scope) — raccomandato `ACCOUNT_WIDE`
- BP_D3 (claim scope)
- BP_D4 (season scope)

---

## 4. Sequenza raccomandata post-decision

| Step | Nome | Rischio | DB migration se |
|---|---|---|---|
| 1 | `PRODUCT_DECISION_BOARD_REVIEW_BATTLE_PASS` | doc | — |
| 2 | `BATTLE_PASS_TECHNICAL_HARDENING_PACK` (upsert + index) | 🟢 low | no |
| 3 | `BATTLE_PASS_SCOPE_APPLY_PACK` | 🟡 medium | yes se BP_D1=PER_SERVER |

---

## 5. Verdict

🟢 **`BLOCK_B_BATTLE_PASS_PRODUCT_DECISION_AUDIT_READY`**
