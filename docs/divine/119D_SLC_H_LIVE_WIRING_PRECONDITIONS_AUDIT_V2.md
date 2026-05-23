# 119D — V5 BLOCK D — SLC-H LIVE WIRING PRECONDITIONS AUDIT V2

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V5`  
**Block**: D — `SLC_H_LIVE_WIRING_PRECONDITIONS_AUDIT_V2`  
**Verdict**: 🟢 `BLOCK_D_SLC_H_PRECONDITIONS_AUDIT_V2_READY`  
**Modalità**: AUDIT/DOC ONLY

---

## 1. V1 baseline reference

- **V1 audit**: `/app/data/design/server_lifecycle/slc_h_live_wiring_readiness_v1.json`
- **V1 readiness %**: 45%

---

## 2. Cambiamenti significativi V1 → V5

| Pack | Cambiamento | Impact |
|---|---|---|
| V2 BLOCK_A | daily_claims server_scope APPLIED | +1% readiness |
| V2 BLOCK_B | gvg user_mail server_scope APPLIED | +1% readiness |
| V2 BLOCK_C | VIP_PAID_ACCOUNT_WIDE_CANONICAL_V1 | closes 3 surfaces |
| V3 BLOCK_A | shop purchases REQUIRES_PRODUCT_DECISION_MIXED | clarifies blocker |
| V3 BLOCK_B | BP product decision matrix | BP_D2 closed in V4 |
| V4 BLOCK_B | BATTLE_PASS_PREMIUM_ACCOUNT_WIDE_CANONICAL_V1 | closes BP-S03 |
| V5 BLOCK_A | BP_D1/D3/D4 board prep | surface decisions, pending signoff |

---

## 3. SLC-H endpoints — status refresh

| Endpoint | V1 → V5 |
|---|---|
| `GET /api/servers` | PARTIAL (legacy unchanged) |
| `GET /api/account/server-profiles` | NOT_IMPLEMENTED |
| `POST /api/account/server-profiles/select` | NOT_IMPLEMENTED |
| `GET /api/account/active-server` | NOT_IMPLEMENTED |
| `POST /api/account/server-profiles/create` | NOT_IMPLEMENTED |

---

## 4. Readiness score V2

| Categoria | Conteggio |
|---|---|
| ✅ Completed | 4 |
| 💪 Strengthened (vs V1) | 5 |
| 🟡 Audit-only done | 4 |
| 🟡 Pending signoff | 1 |
| 🔴 Not implemented | 4 |
| 🔴 Blocked by design | 2 |
| **Readiness %** | **55%** |
| **Δ vs V1** | **+10 punti percentuali** |

---

## 5. Hard blockers per implementation

| Priorità | Blocker |
|---|---|
| **P0** | server_profiles collection canonical schema |
| **P0** | DB migration `users.active_server_profile_id` |
| **P0** | AF2-N V8 broad rollout signoff (canary + 3 FROZEN audits) |
| **P1** | Legacy `/server/select` removal (economy.py:195) |
| **P1** | Cosmetics schema split applied |
| **P1** | Battle pass BP_D1/D3/D4 board signoff (V5 BLOCK_A ready) |
| **P2** | `second_server_opening_enabled` flag + Phase 11 timeline |

---

## 6. Verdict

🟢 **`BLOCK_D_SLC_H_PRECONDITIONS_AUDIT_V2_READY`**
