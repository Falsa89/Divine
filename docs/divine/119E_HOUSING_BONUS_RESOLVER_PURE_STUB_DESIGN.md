# 119E — V5 BLOCK E — HOUSING BONUS RESOLVER PURE STUB DESIGN

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V5`  
**Block**: E — `HOUSING_BONUS_RESOLVER_PURE_STUB_DESIGN_PACK`  
**Verdict**: 🟢 `BLOCK_E_HOUSING_BONUS_RESOLVER_STUB_DESIGN_READY`  
**Modalità**: DESIGN/DOC ONLY

---

## 1. Pure-function contract

```
name:           HousingBonusResolver
type:           pure_function
purity:         no side effects, deterministic, thread-safe, version-stamped
```

---

## 2. Inputs

| Campo | Type | Note |
|---|---|---|
| `user_id` | str | required |
| `server_id` | str | required (housing è server-bound) |
| `rooms` | List[RoomState] | snapshot read-only |
| `residents` | List[ResidentAssignment] | resident assignments |
| `vip_level` | int | da `vip_data` (account-wide) |
| `bonus_catalog_version` | str | version pin |

## 3. Outputs

| Campo | Type | Descrizione |
|---|---|---|
| `bonus_set` | Dict[str, float] | es. `{'hp_pct': 0.05, 'atk_pct': 0.03}` |
| `applied_caps` | List[CapTrigger] | cap raggiunti durante calcolo |
| `catalog_version` | str | echo input version |

---

## 4. Caps canonical

| Cap | Valore |
|---|---|
| Max total housing bonus % of power | **15%** |
| Max resident bonus per hero | **5%** |
| Max residents per room | **1** |
| Max room slots per user (by VIP) | vip0:4, vip1:5, vip2:6, vip3:7, vip4:8, vip5:10 |
| Stacking con AF2-N gift bonuses | ❌ disallowed |
| Stacking con artifacts | ✅ allowed |

---

## 5. Guardrails

| Constraint | Status |
|---|---|
| No battle integration | ✅ |
| No DB write | ✅ |
| No stat application | ✅ |
| No UI | ✅ |
| No `/api/housing` endpoint | ✅ |
| No call in `battle_engine.py` | ✅ |
| No call in `battle_core.py` | ✅ |
| No call in `combat.tsx` | ✅ |
| Only callable via future stats_provider (with explicit pack approval) | ✅ |

---

## 6. Future implementation checklist

| Priorità | Step |
|---|---|
| **P0** | Design board signoff power curve + caps |
| **P0** | DB schema canonical (rooms, inventory, residents, claim_history) |
| **P0** | SLC-H live wiring (housing è server-bound → richiede `active_server_profile_id`) |
| **P1** | Implementazione pure stub in `/app/backend/services/housing_bonus_resolver.py` (file separato da routes) |
| **P1** | Unit tests deterministici con catalog_version pin |
| **P2** | stats_provider integration (channel separato da AF2-N) |
| **P2** | battle_engine integration via stats_provider (richiede Batch-4 + unfreeze battle_engine) |

---

## 7. Verdict

🟢 **`BLOCK_E_HOUSING_BONUS_RESOLVER_STUB_DESIGN_READY`**
