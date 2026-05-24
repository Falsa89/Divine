# 124C — PROJECT_B Track C — HERO_SKILL_KIT_CATALOG_FREEZE

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_B`  
**Track**: C  
**Mode**: `suite_data_doc_only_no_runtime`  
**Verdict**: 🟢 `TRACK_C_HERO_SKILL_KIT_CATALOG_FREEZE_READY`  
**Rollback**: N/A (audit/suite only)

---

## 1. Scopo

Freezare i 6 baseline catalog del hero skill kit come **canonical read-only**, registrando lo sha256 di ciascuno per future regression detection. Identifica `rm134b_axispatch_v6` come **CANONICAL_ACTIVE_BASELINE** e marca gli altri 5 come `HISTORICAL`.

## 2. Frozen catalogs (6)

| Version tag | Status | SHA256 (first 16) | Bytes |
|---|---|---|---|
| rm132pre_v1 | HISTORICAL | `f75d20aab42e023a` | 3382 |
| rm132preb2_v2 | HISTORICAL | `26770389876c9a6e` | 4003 |
| rm132apost_v3 | HISTORICAL | `76d530dac5081861` | 4927 |
| rm132b_v4 | HISTORICAL | `c851734004f0373c` | 5602 |
| rm132c2_v5 | HISTORICAL | `6bcb81ddcc78040c` | 3125 |
| **rm134b_axispatch_v6** | **CANONICAL_ACTIVE_BASELINE** | `fa974b5913a20ce3` | 4447 |

## 3. Invariants documentati

| Invariante | Stato |
|---|---|
| Slot progression rules 1⋆—6⋆ + Borea inert | deferred a slot-progression validator (futuro) |
| No final balance numbers live | ✅ True |
| Borea activation | ❌ False |
| 5⋆ no true ultimate | design constraint (non enforced live qui) |
| 6⋆ ha ultimate + divine_weapon_id | design constraint (non enforced live qui) |

## 4. Future unfreeze gate

Lo unfreeze richiede:
1. Esplicita user authorization
2. Pack marker dedicato `HERO_SKILL_KIT_CATALOG_UNFREEZE_PACK`
3. Rationale documentata

## 5. Validator

- **Path**: `/app/backend/scripts/validate_project_b_hero_skill_kit_catalog_freeze_v1.py`
- **Suite task_id**: `PROJECT-B-TRACK-C-HERO-SKILL-KIT-CATALOG-FREEZE` (OPTIONAL)
- **Type**: read-only sha256 check
- **Verifica chiave**: ogni catalog file deve match il sha256 dichiarato nel manifest (regression invariant)

## 6. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| Skill runtime activation | ❌ No |
| `battle_engine.py` changes | ❌ No |
| Catalog content rewrite | ❌ No |
| Final balance numbers introduction | ❌ No |
| Borea activation | ❌ No |
