# 123G — PROJECT_A Track G — PROJECT_COMPLETION_DOD_TRACKER

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_A`  
**Track**: G  
**Mode**: `project_management_dod_tracker_no_runtime`  
**Verdict**: 🟢 `TRACK_G_QA_RELEASE_DOD_TRACKER_READY`  
**Rollback**: N/A (project management doc)

---

## 1. Scopo

Definire il **technical Definition-of-Done tracker** per la completion del progetto **escludendo graphics/audio/art assets** (out of scope).

## 2. DoD rows (7)

### Row 1 — SLC/SLC-H
- **Current**: **73% → 78%** post-Project_A
- **Target GA**: 95%+
- **Closed**: schema canonical, 3 indices definition, collection LIVE INERT (NEW), legacy /server/select deprecation, dual-route design Phase 2/3/4
- **Pending**: dual-route Phase 2 endpoint impl, dual-write, legacy removal, users.server drop
- **Next**: `SERVER_PROFILES_DUAL_ROUTE_IMPLEMENTATION_PACK`

### Row 2 — AF2-N
- **Current**: stage4_internal_beta_canary_active
- **Target GA**: broad_rollout_v8+
- **Closed**: pipeline, snapshot export, dashboard template, render JSON, **runtime routing preflight (NEW)**
- **Pending**: managed Redis live, alerting live sink, legal+product signoff, final user approval, broad rollout V8
- **Next**: `AF2N_OBSERVABILITY_DASHBOARD_PROVISION_DESIGN_PACK`

### Row 3 — combat/skill/status
- **Current**: adapter_wiretest_only_no_live_combat
- **Target GA**: live_skill_status_in_combat
- **Closed**: catalog baseline v6, adapter wiretest, **runtime map (NEW)**
- **Pending**: catalog freeze, status effect baseline, MVP sandbox runner, no-diff guard
- **Next**: `HERO_SKILL_KIT_CATALOG_FREEZE_PACK`

### Row 4 — economy/battle pass/shop
- **Current**: 90%+
- **Target GA**: 100%
- **Closed**: BP D1/D3/D4 signoff, $setOnInsert hardening, **user_season unique index APPLIED (NEW)**, **V4 R4 CLOSED (NEW)**, /server/select deprecation
- **Pending**: shop carousel/limited offers audit, gem topup observability
- **Next**: `SHOP_LIMITED_OFFERS_CONTRACT_AUDIT_PACK`

### Row 5 — gacha/summon
- **Current**: behavior_stable_drift_cleanup_pending
- **Target GA**: drift_cleanup_complete
- **Closed**: V1 BLOCK_B audit, **drift cleanup plan READY (NEW)**
- **Pending**: per-drift-doc gated apply packs (7), obtainable pool stability validator
- **Next**: `DRIFT_DOC_1_LEGACY_SUMMON_RATE_ARCHIVE_PACK`

### Row 6 — housing MVP
- **Current**: design_only_no_runtime
- **Target GA**: MVP_inert_get_endpoints + claim_idempotent
- **Closed**: dimora audit, resolver stub design v5, **backend contract READY (NEW)**
- **Pending**: pure resolver stub creation, DB schemas, inert GETs, claim idempotent
- **Next**: `HOUSING_MVP_RESOLVER_STUB_CREATION_PACK`

### Row 7 — QA/mobile/release
- **Current**: suite_baseline_371+_extensions
- **Target GA**: suite_pass + mobile_smoke + release_checklist_signed
- **Closed**: suite 367→371→(post V_A), parallel audit, **DoD tracker READY (NEW)**
- **Pending**: parallel runner implementation, mobile smoke flow, release GA template
- **Next**: `SUITE_PARALLEL_RUNNER_IMPLEMENTATION_PACK`

## 3. Global progress estimate

| Indicatore | Pre-Project_A | Post-Project_A | Δ | Giustificazione |
|---|---|---|---|---|
| **Global project** | 86% | **88%** | **+2%** | 2 apply ops live (server_profiles collection+3 indexes; BP unique index chiude V4 R4) + 5 design/audit track + DoD tracker |
| **SLC-H readiness** | 73% | **78%** | **+5 pts** | Track A apply chiude Phase 1 collection preconditions; combinato con V8 BLOCK_D dual-route design abilita Phase 2 implementation pack |

## 4. Validator

- **Path**: `/app/backend/scripts/validate_project_completion_dod_tracker_v1.py`
- **Suite task_id**: `PROJECT-A-TRACK-G-QA-RELEASE-DOD-TRACKER` (OPTIONAL)
- **Type**: read-only (verifica 7 rows, struttura, justification fields)
- **Esito V_A**: ✅ PASS
