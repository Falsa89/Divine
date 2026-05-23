# 117D — V3 BLOCK D — HOUSING RUNTIME SAFETY AUDIT V3

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V3`  
**Block**: D — `HOUSING_RUNTIME_SAFETY_AUDIT_V3`  
**Verdict**: 🟢 `BLOCK_D_HOUSING_RUNTIME_SAFETY_AUDIT_V3_READY`  
**Modalità**: AUDIT/DOC ONLY

---

## 1. Current housing runtime state

| Indicatore | Valore |
|---|---|
| `/api/housing` endpoints implementati | **0** |
| HousingBonusResolver | NOT_IMPLEMENTED |
| File routes housing | NONE |
| Frontend Expo housing screen | NOT_IMPLEMENTED |
| DB collections housing attive | none |
| Status runtime | 🟢 `DESIGN_ONLY_FROZEN` (sicuro) |

---

## 2. Safety architecture matrix (5 componenti)

| Componente | Status | Blocker |
|---|---|---|
| HousingBonusResolver | NOT_IMPLEMENTED | Design board signoff power curve |
| housing_inventory (rooms+furniture) | NOT_IMPLEMENTED | DB schema design |
| residents (hero assignment) | NOT_IMPLEMENTED | Resident bonus policy v1 da consolidare |
| claim_all (resource collection) | NOT_IMPLEMENTED | Anti-power-creep cap signoff |
| battle_power integration | DESIGN_ONLY | `battle_engine.py` FROZEN |

---

## 3. Anti-power-creep caps (canonical)

| Cap | Valore |
|---|---|
| Max total housing bonus % of power | **15%** |
| Max resident bonus per hero | **5%** |
| Max room slots per user | vedi `room_cap_policy v1` |
| VIP vault bonus capped | ✅ true |
| Stacking con AF2-N gift bonuses | ❌ disallowed (mutually exclusive bucket) |

---

## 4. Implementation blockers (6 totali)

| Priorità | Blocker |
|---|---|
| **P0** | `battle_engine.py` FROZEN → impossibile integrare stats_provider housing channel |
| **P0** | Design board signoff power curve + anti-power-creep caps |
| **P1** | DB schema canonical (rooms, inventory, residents, claim_history) |
| **P1** | SLC-H live wiring (housing è server-bound → richiede `active_server_profile_id`) |
| **P2** | Frontend Expo housing screen |
| **P2** | VIP vault cross-server policy (gated by `VIP_PAID_ACCOUNT_WIDE_CANONICAL_V1`) |

---

## 5. Required safe architecture per HousingBonusResolver

- Resolver puro stateless: `input(user_id) -> bonus_set`
- Caps anti-power-creep hardcoded da `room_cap_policy v1`
- Output deterministico (testabile)
- **NESSUNA** chiamata diretta in combat path → passa via `stats_provider`
- Versioning del bonus catalog

---

## 6. Verdict

🟢 **`BLOCK_D_HOUSING_RUNTIME_SAFETY_AUDIT_V3_READY`**

**Next action**: design board review per power curve + anti-power-creep caps. Solo dopo si può considerare un pack `HousingBonusResolver_PURE_STUB` (no runtime wire) come step zero.
