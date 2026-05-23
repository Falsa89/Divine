# 117A — V3 BLOCK A — ECONOMY SHOP PURCHASES CLASSIFICATION AUDIT

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V3`  
**Block**: A — `ECONOMY_SHOP_PURCHASES_CLASSIFICATION_AUDIT`  
**Verdict**: 🟢 `BLOCK_A_ECONOMY_SHOP_PURCHASES_AUDIT_READY`  
**Modalità**: AUDIT/DOC ONLY (nessun runtime patch)

---

## 1. Surface target

| Campo | Valore |
|---|---|
| ID | **ECONOMY-W01** |
| File | `/app/backend/routes/economy.py` |
| Endpoint | `POST /api/shop/buy` |
| Linea | **56** |
| Collection | `shop_purchases` |
| Op | `insert_one` |
| Stato precedente (V1) | `AMBIGUOUS_DEFER` |

---

## 2. Inventory shop items (10)

| Currency di acquisto | # | Item IDs | Classificazione |
|---|---|---|---|
| `gold` (free server-bound) | 3 | gems_small, gems_medium, gems_large | FREE_TO_PAID_CONVERSION_PURCHASE |
| `gems` (paid account-wide) | 7 | stamina_50, stamina_full, gold_pack, gold_chest, exp_boost, gacha_ticket, gacha_ticket_10 | PAID_TO_MIXED_REWARD_PURCHASE |

---

## 3. Verdict canonical

🟡 **`REQUIRES_PRODUCT_DECISION_MIXED`**

`shop_purchases` è intrinsecamente MIXED. Nessun micro-batch metadata-only è sicuro senza prima una product decision esplicita.

---

## 4. Product decisions richieste

| ID | Question | Default attuale |
|---|---|---|
| **DECISION_1** | Daily purchase caps account-wide o server-bound? | implicito ACCOUNT_WIDE |
| **DECISION_2** | Shop rotation/promo globale o per-server? | implicito GLOBAL |

### DECISION_1 — opzioni

| Opzione | Impatto |
|---|---|
| ALL_ACCOUNT_WIDE | Lo shop resta globale; più semplice, riduce competitività per-server |
| ALL_SERVER_BOUND | Stesso item shop in N server; più grind ma più paid-friendly |
| SPLIT_BY_PRICE_TYPE | gold-priced server-bound + gems-priced account-wide |

---

## 5. Micro-batch futuri sicuri

| Condizione | Pack |
|---|---|
| DECISION_1=ALL_SERVER_BOUND | `ECONOMY_SHOP_PURCHASES_SERVER_BOUND_MICRO_BATCH` (2 LOC) |
| DECISION_1=SPLIT_BY_PRICE_TYPE | `ECONOMY_SHOP_PURCHASES_CONDITIONAL_SCOPE_MICRO_BATCH` (5-8 LOC) |
| DECISION_1=ALL_ACCOUNT_WIDE | Solo marker canonical (zero LOC runtime) |

Nessuno è sicuro prima della decision.

---

## 6. Verdict

🟢 **`BLOCK_A_ECONOMY_SHOP_PURCHASES_AUDIT_READY`**
