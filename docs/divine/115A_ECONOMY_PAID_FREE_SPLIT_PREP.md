# 115A — BLOCK A — ECONOMY REFACTOR PAID/FREE SPLIT PREP

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V1`  
**Block**: A — `ECONOMY_REFACTOR_PAID_FREE_SPLIT_PREP`  
**Verdict**: 🟢 `BLOCK_A_ECONOMY_REFACTOR_PREP_READY`  
**Modalità**: AUDIT/PREP ONLY (nessun patch runtime, nessuna DB migration)  
**Timestamp**: 20260523T210000Z

---

## 1. Marker autorizzativi

| Marker | Valore | Status |
|---|---|---|
| `MEGA_COMBO_SLC_ACCELERATION_V1_APPROVAL` | `true` | ✅ presente |
| `SLC_ACCELERATION_MODE` | `MULTI_BLOCK_PARTIAL_SUCCESS` | ✅ presente |
| `BLOCK_A_ECONOMY_REFACTOR_PREP_APPROVAL` | `true` | ✅ presente |

---

## 2. Scope audit

File target: `/app/backend/routes/economy.py` (276 LOC).  
Sottosistemi: **SHOP / DAILY_FREE / MAIL / BATTLE_PASS / MULTI_SERVER_LEGACY / VIP**.

---

## 3. Classificazione write surfaces (11 trovate)

| ID | Endpoint | Linea | Collection | Op | Classificazione |
|---|---|---|---|---|---|
| W01 | `POST /api/shop/buy` | 55 | `shop_purchases` | insert | 🟡 AMBIGUOUS_DEFER |
| W02 | `POST /api/shop/claim-daily/{id}` | 73 | `daily_claims` | insert | 🟢 FREE_SERVER_BOUND |
| W03 | `POST /api/mail/claim/{id}` | 97 | `user_mail` | update | ⚪ UPDATE_ONLY_NO_SCOPE |
| W04 | `GET /api/battlepass (init)` | 106 | `battle_pass` | insert | 🟠 VIP_ACCOUNT_OR_MIXED |
| W05 | `POST /api/battlepass/claim/{lvl}` | 146 | `battle_pass` | update | ⚪ UPDATE_ONLY_NO_SCOPE |
| W06 | `POST /api/battlepass/buy-premium` | 157 | `battle_pass` | upsert $set | 🟡 AMBIGUOUS_DEFER |
| W07 | `POST /api/battlepass/add-exp (init)` | 166 | `battle_pass` | insert | 🟠 VIP_ACCOUNT_OR_MIXED |
| W08 | `POST /api/server/select` | 195 | `users.server` | update | 🔴 LEGACY_SERVER_SELECT_FORBIDDEN |
| W09 | `GET /api/vip (init)` | 214 | `vip_data` | insert | 🔵 PAID_ACCOUNT_WIDE |
| W10 | `POST /api/vip/claim-daily` | 262 | `vip_data` | upsert | 🔵 PAID_ACCOUNT_WIDE |
| W11 | `POST /api/vip/add-spend` | 269 | `vip_data` | upsert | 🔵 PAID_ACCOUNT_WIDE |

### Bucket sintetici

- 🔵 **PAID_ACCOUNT_WIDE**: W09, W10, W11 (VIP — canonical `NO_SERVER_SCOPE_BY_DESIGN`)
- 🟢 **FREE_SERVER_BOUND**: W02 (daily_claims — candidato sicuro per micro-batch)
- 🟠 **VIP_ACCOUNT_OR_MIXED**: W04, W07 (battle pass — richiede product decision)
- 🔴 **LEGACY_SERVER_SELECT_FORBIDDEN**: W08 (deferred a SLC-H + economy refactor signoff)
- 🟡 **AMBIGUOUS_DEFER**: W01 (shop_purchases), W06 (battle_pass buy-premium upsert pattern)
- ⚪ **UPDATE_ONLY_NO_SCOPE_REQUIRED**: W03, W05

---

## 4. Sequenza raccomandata di micro-batch futuri

| Step | Nome | Surfaces | Rischio | DB Migration |
|---|---|---|---|---|
| 1 | `ECONOMY_DAILY_CLAIMS_SCOPE_MICRO_BATCH` | W02 | 🟢 low | No |
| 2 | `ECONOMY_SHOP_PURCHASES_CLASSIFICATION_TASK` | W01 | 🟢 low (audit only) | No |
| 3 | `ECONOMY_BATTLE_PASS_REFACTOR_PRODUCT_DECISION` | W04, W06, W07 | 🟠 medium-high | Yes |
| 4 | `ECONOMY_VIP_PAID_ACCOUNT_WIDE_CANONICAL` | W09, W10, W11 | 🟢 low (marker) | No |
| 5 | `ECONOMY_LEGACY_SERVER_SELECT_REMOVAL` | W08 | 🔴 high | No (gated da SLC-H) |

---

## 5. Guardrail rispettati

- ❌ No pricing/currency change
- ❌ No paid/free behavior change
- ❌ No VIP behavior change
- ❌ No `/server/select` runtime wiring/removal
- ❌ No DB migration/backfill
- ❌ No route behavior change
- ❌ No file runtime modificati (0 LOC)

---

## 6. Artefatti creati

- `/app/data/design/server_lifecycle/economy_paid_free_split_plan_v1.json`
- `/app/docs/divine/115A_ECONOMY_PAID_FREE_SPLIT_PREP.md` (questo file)
- `/app/backend/scripts/audit_economy_paid_free_split_prep_v1.py`

---

## 7. Verdict

🟢 **`BLOCK_A_ECONOMY_REFACTOR_PREP_READY`**

Prossimo step low-risk consigliato: **ZIP gated `ECONOMY_DAILY_CLAIMS_SCOPE_MICRO_BATCH`** (singolo step di 2 righe su W02 con `ensure_server_scope`).
