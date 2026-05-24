# 120D — V6 BLOCK D — LEGACY /server/select REMOVAL PLAN

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V6`  
**Block**: D — `LEGACY_SERVER_SELECT_REMOVAL_PLAN_PACK`  
**Verdict**: 🟢 `BLOCK_D_LEGACY_SERVER_SELECT_REMOVAL_PLAN_READY`  
**Modalità**: AUDIT/PLAN ONLY (nessuna rimozione)

---

## 1. Target

| Campo | Valore |
|---|---|
| File | `/app/backend/routes/economy.py` |
| Endpoint | `POST /api/server/select` |
| Linea | **195** |
| Behavior | Set `users.server = req.server_id` (legacy single-server) |
| Frontend usage | ✅ yes (legacy flow) |
| Classification V1 | LEGACY_SERVER_SELECT_FORBIDDEN (W08) |

---

## 2. Removal strategy (4 fasi)

| Phase | Pack futuro | Diff stimato |
|---|---|---|
| **0** audit only | V6 BLOCK_D (questo) | 0 LOC |
| **1** deprecation warning | `ECONOMY_SERVER_SELECT_DEPRECATION_NOTICE_PACK` | ~5 LOC |
| **2** dual-route support | `SLC_H_LIVE_WIRING_DUAL_WRITE_PACK` | TBD |
| **3** route removal | `ECONOMY_LEGACY_SERVER_SELECT_REMOVAL_APPLY_PACK` | rimozione |
| **4** users.server drop | `USERS_SERVER_FIELD_BACKFILL_DROP_PACK` | DB migration |

---

## 3. Prerequisiti per Phase 3 removal

| Priorità | Item |
|---|---|
| **P0** | V6 BLOCK_C `server_profiles` schema implementato |
| **P0** | SLC-H endpoints implementati (4) |
| **P0** | Frontend migrato ai nuovi SLC-H endpoints |
| **P1** | Grace period ≥ 1 release cycle con deprecation warning |
| **P1** | Telemetry conferma zero calls a `/api/server/select` |
| **P2** | AF2-N V8 broad rollout signoff (no SLC-H/AF2-N interaction risk) |

---

## 4. Rollback strategy per fase

| Phase | Rollback |
|---|---|
| 1 | Trivial: revert ~5 LOC; deprecation warning era passivo |
| 2 | Revert dual-write; nuovo field rimane ma non authoritative |
| 3 | Re-add route da git history |
| 4 | DB restore da backup; `users.server` re-introdotto |

---

## 5. Affected consumers inventory

| Consumer | Dependency | Migration richiesta |
|---|---|---|
| Frontend select-server screen | `POST /api/server/select` | ✅ |
| Backend `ensure_server_scope` | reads `users.server` | depends V6 BLOCK_C dual_read |
| `GET /api/servers` (legacy) | sibling endpoint | namespace migration |

---

## 6. Verdict

🟢 **`BLOCK_D_LEGACY_SERVER_SELECT_REMOVAL_PLAN_READY`**

**Next action**: Phase 1 → pack `ECONOMY_SERVER_SELECT_DEPRECATION_NOTICE_PACK` (~5 LOC, low-risk).
