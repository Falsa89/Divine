# 116C — V2 BLOCK C — ECONOMY VIP PAID ACCOUNT-WIDE CANONICAL MARKER

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V2`  
**Block**: C — `ECONOMY_VIP_PAID_ACCOUNT_WIDE_CANONICAL_MARKER`  
**Verdict**: 🟢 `BLOCK_C_ECONOMY_VIP_PAID_MARKER_READY`  
**Modalità**: AUDIT/DOC ONLY (nessun runtime patch)

---

## 1. Marker autorizzativi

| Marker | Status |
|---|---|
| `MEGA_COMBO_SLC_ACCELERATION_V2_APPROVAL=true` | ✅ |
| `BLOCK_C_ECONOMY_VIP_PAID_MARKER_APPROVAL=true` | ✅ |

---

## 2. Regola canonical introdotta

**Rule ID**: `ECONOMY_VIP_PAID_ACCOUNT_WIDE_CANONICAL_V1`

> Le superfici VIP e tutte le scritture su collection `vip_data` sono **ACCOUNT_WIDE_BY_DESIGN**. NON devono ricevere `ensure_server_scope`. Lo scope server-bound è esplicitamente NON applicabile (paid currency progression).

---

## 3. Superfici classificate canonical

| ID | Endpoint | Linea | Collection | Op | Decisione |
|---|---|---|---|---|---|
| ECONOMY-W09 | `GET /api/vip` (auto-init) | 214 | `vip_data` | insert_one | 🔵 `NO_SERVER_SCOPE_BY_DESIGN` |
| ECONOMY-W10 | `POST /api/vip/claim-daily` | 262 | `vip_data` | upsert | 🔵 `NO_SERVER_SCOPE_BY_DESIGN` |
| ECONOMY-W11 | `POST /api/vip/add-spend` | 269 | `vip_data` | upsert | 🔵 `NO_SERVER_SCOPE_BY_DESIGN` |

---

## 4. Classificazione paid currency

| Currency | Categoria | Note future |
|---|---|---|
| `gems` | 🔵 PAID_ACCOUNT_WIDE | Eventuale paid-vs-free split richiede product decision |
| `gold` | 🟢 FREE_SERVER_BOUND_CANDIDATE | Più corretto come server-bound; richiede DB migration |
| `stamina` | 🟢 FREE_SERVER_BOUND_CANDIDATE | Tipicamente server-bound (UX) |

---

## 5. Prerequisiti per futuro economy refactor

| Priorità | Item |
|---|---|
| **P0** | Product decision su paid (gems) vs free (gold/stamina) split tra server |
| **P0** | Battle pass progress per-server vs account-wide |
| **P1** | Rimozione legacy `/server/select` post SLC-H live wiring |
| **P1** | Migration plan `users.server` → `users.active_server_profile_id` |
| **P2** | Split `users` document in `(account_profile, server_profile)` |

---

## 6. Validator strategy

Nessuno script standalone richiesto: il **rollup V2 (Block E)** verifica presenza del file canonical e consistenza delle 3 superfici W09/W10/W11.

---

## 7. Verdict

🟢 **`BLOCK_C_ECONOMY_VIP_PAID_MARKER_READY`**
