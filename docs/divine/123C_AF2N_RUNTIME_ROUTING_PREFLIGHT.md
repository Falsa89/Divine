# 123C — PROJECT_A Track C — AF2N_RUNTIME_ROUTING_PREFLIGHT

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_A`  
**Track**: C  
**Mode**: `audit_preflight_no_runtime_mutation`  
**Verdict**: 🟢 `TRACK_C_AF2N_RUNTIME_ROUTING_PREFLIGHT_READY`  
**Rollback**: N/A (audit/preflight only)

---

## 1. Scopo

Preparare il **preflight runtime routing AF2-N Batch-3** senza modificare il runtime. Identifica route/file coinvolti, mappa lo state corrente canary, definisce l'apply gate per future runtime routing.

## 2. Upstream chain

- V5 BLOCK_B: AF2-N observability metrics pipeline
- V6 BLOCK_B: snapshot export
- V7 BLOCK_D: dashboard template
- V8 BLOCK_C: dashboard render JSON

## 3. Current AF2-N runtime state

| Aspetto | Valore |
|---|---|
| Stage | `stage4_internal_beta_active_no_broad_rollout` |
| Canary active | ✅ true |
| Canary allowlist size | 3 |
| Ledger cap | 20 |
| Feature flag | `true_explicit_affinity_gift_runtime_on` |
| Broad rollout authorized | ❌ false |
| Public spend UI | ❌ false |
| Battle runtime attached | ❌ false |
| Inventory mutation | ❌ false |
| Affinity points mutation | ❌ false |
| Buffs enabled | ❌ false |

## 4. Routes inventory per Batch-3 (NO RUNTIME CHANGE in Track C)

| Route | File | State corrente | Change in Track C | Future Batch-3 proposed |
|---|---|---|---|---|
| `POST /api/affinity/gift-spend` | `affinity.py` | canary allowlist active | NONE | increase cap 3 → 25 ONLY after signoff |
| `GET /api/affinity/gift-spend/canary-status` | `affinity.py` | read-only status | NONE | add optional metric fields per P3/P7 |
| `GET /api/affinity/*-axis` | `affinity.py` | AXIS-G combined 200/404/405 | NONE | none (axis layer GO) |

## 5. Apply gate per future Batch-3

### Required signoffs (7)
engineering, qa, product, legal, sre, security, final_user_approval.

### Required evidence

| Evidence | Status |
|---|---|
| EV-V28-SCHEMA-FIX-REG | PROVIDED |
| EV-V29-EXT-MONITORING | PROVIDED |
| EV-V29-STRESS-8X | PROVIDED |
| EV-V29-DELTA-AUDIT | PROVIDED |
| EV-INFRA-MANAGED-REDIS-LIVE | PENDING |
| EV-INFRA-ALERTING-LIVE | PENDING |
| **EV-OBSERVABILITY-DASHBOARDS** | **PROVIDED_RENDER_JSON_READY (via V8 BLOCK_C)** ✅ |
| EV-LEGAL-PRODUCT-SIGNOFF | PENDING |
| EV-USER-FINAL-APPROVAL | PENDING |

### Blocking gates
- `BLK-G-01_BROAD_ROLLOUT_V6_APPROVAL` (PLAN_READY_NOT_APPROVED)
- `BLK-G-02_NO_GO_V29` (P0 open)

## 6. Validator

- **Path**: `/app/backend/scripts/validate_project_a_af2n_runtime_routing_preflight_v1.py`
- **Suite task_id**: `PROJECT-A-TRACK-C-AF2N-RUNTIME-ROUTING-PREFLIGHT` (OPTIONAL)
- **Type**: read-only (JSON + source grep)
- **Verifiche**: nessuna AF2-N runtime mutation, broad_rollout false, no public_spend_ui enable in affinity.py

## 7. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| AF2-N runtime mutation | ❌ No |
| Public spend UI | ❌ No |
| Gift spend/inventory/ledger behavior change | ❌ No |
| STACK-G changes | ❌ No |
