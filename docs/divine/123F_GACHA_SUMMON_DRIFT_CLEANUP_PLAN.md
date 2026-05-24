# 123F — PROJECT_A Track F — GACHA_SUMMON_DRIFT_CLEANUP_PLAN

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_A`  
**Track**: F  
**Mode**: `audit_plan_only_no_data_mutation`  
**Verdict**: 🟢 `TRACK_F_GACHA_SUMMON_DRIFT_CLEANUP_PLAN_READY`  
**Rollback**: N/A (plan only)

---

## 1. Scopo

Preparare un **gated cleanup plan** per i 7 drift docs identificati in V1 BLOCK_B audit, senza alcuna data mutation, route change o behavior change.

## 2. Classificazione drift docs (7)

| ID | Classe | Action | Data mutation? |
|---|---|---|---|
| DRIFT_DOC_1 | legacy_summon_rate_v0 | archive_into_attic | ❌ |
| DRIFT_DOC_2 | deprecated_banner_legacy_pool | archive_into_attic | ❌ |
| DRIFT_DOC_3 | obsolete_pity_counter_format | freeze_read_only | ❌ |
| DRIFT_DOC_4 | duplicate_summon_log_format | dedupe_design_required | ✅ (deferred) |
| DRIFT_DOC_5 | stale_obtainable_pool_snapshot | freeze_read_only | ❌ |
| DRIFT_DOC_6 | orphan_summon_history_entry | dedupe_design_required | ✅ (deferred) |
| DRIFT_DOC_7 | unreferenced_legacy_summon_event | archive_into_attic | ❌ |

## 3. Summary aggregato

| Metric | Valore |
|---|---|
| Docs total | 7 |
| `archive_into_attic` | 3 |
| `freeze_read_only` | 2 |
| `dedupe_design_required` | 2 |
| Data mutation required total | 2 |
| **Data mutation executed in Track F** | **0** |

## 4. Routes/Files responsabili

| File | Drift docs affected |
|---|---|
| `/app/backend/routes/summon.py` | DRIFT_DOC_1, DRIFT_DOC_4, DRIFT_DOC_6 |
| `/app/backend/routes/gacha.py` (se esiste) | DRIFT_DOC_2, DRIFT_DOC_5, DRIFT_DOC_7 |
| `/app/backend/data/banner_pool_*.json` | DRIFT_DOC_3 |

## 5. Cleanup gate

### Required signoffs
- engineering_signoff
- product_signoff
- final_user_approval_per_drift_doc

### Required evidence
1. Pre-cleanup snapshot di tutti i 7 drift doc states
2. Diff vs expected canonical state
3. Impact analysis su summon route response shape
4. Rollback script per ogni data mutation drift doc

### Future apply strategy
Per-drift-doc **gated pack** (un pack per drift doc); **no broad bulk cleanup**.

## 6. Validator

- **Path**: `/app/backend/scripts/validate_project_a_gacha_summon_drift_cleanup_plan_v1.py`
- **Suite task_id**: `PROJECT-A-TRACK-F-GACHA-SUMMON-DRIFT-CLEANUP-PLAN` (OPTIONAL)
- **Type**: read-only (plan JSON integrity + sanity grep su `summon.py` per pattern proibiti)
- **Esito V_A**: ✅ PASS

## 7. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| DB cleanup | ❌ No |
| Gacha/summon route behavior change | ❌ No |
| Roster/ownership mutation | ❌ No |
| Borea activation | ❌ No |
| Banner/rate/pity/pool change | ❌ No |
