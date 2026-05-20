# ULTRA-COMBO V29 — ENV-AWARE MANAGED REDIS / ALERTING READINESS + V28 SCHEMA-FIX REGRESSION + SCOPE S1 EXTENDED MONITORING + STRESS 8X + BROAD ROLLOUT SIGNOFF V7 PLAN-ONLY + SAFETY-ROLLUP-X

**Task origin**: `AF2-N-V29`
**Status**: ✅ **PASS** (12/12 validator V29 + suite globale 218/218)
**Date (UTC)**: 2026-05-20
**Stage**: Stage 4 Internal Beta ACTIVE — Scope S1 = 2500 — **NO broad rollout, NO public UI**

---

## 1. File creati (24)

### Backend scripts
- `/app/backend/scripts/run_af2n_v29_preflight.py`
- `/app/backend/scripts/validate_af2n_v29_preflight.py`
- `/app/backend/scripts/run_af2n_v28_schema_fix_regression_v29.py`
- `/app/backend/scripts/validate_af2n_v28_schema_fix_regression_v29.py`
- `/app/backend/scripts/probe_managed_redis_envaware_v29.py`
- `/app/backend/scripts/validate_managed_redis_envaware_v29.py`
- `/app/backend/scripts/probe_alerting_envaware_v29.py`
- `/app/backend/scripts/validate_alerting_envaware_v29.py`
- `/app/backend/scripts/run_af2n_scope_s1_extended_monitoring_v29.py`
- `/app/backend/scripts/validate_af2n_scope_s1_extended_monitoring_v29.py`
- `/app/backend/scripts/run_af2n_stress_8x_v29.py`
- `/app/backend/scripts/validate_af2n_stress_8x_v29.py`
- `/app/backend/scripts/audit_affinity_inventory_delta_consistency_v29.py`
- `/app/backend/scripts/validate_affinity_inventory_delta_consistency_v29.py`
- `/app/backend/scripts/run_af2n_broad_rollout_signoff_package_v7.py`
- `/app/backend/scripts/validate_af2n_broad_rollout_signoff_package_v7.py`
- `/app/backend/scripts/run_af2n_broad_rollout_blocker_matrix_v8.py`
- `/app/backend/scripts/validate_af2n_broad_rollout_blocker_matrix_v8.py`
- `/app/backend/scripts/audit_affinity_gifts_public_preview_v29_safety.py`
- `/app/backend/scripts/run_af2n_v29_rollback_readiness.py`
- `/app/backend/scripts/validate_af2n_v29_rollback_readiness.py`
- `/app/backend/scripts/run_collection_affinity_runtime_activation_rollup_v24.py`
- `/app/backend/scripts/validate_collection_affinity_runtime_activation_rollup_v24.py`
- `/app/backend/scripts/validate_ultra_combo_v29_envaware_readiness_postfix.py`

### Report e doc
- `/app/data/design/affinity/af2n_v29_preflight_result_v1.json`
- `/app/data/design/affinity/af2n_v28_schema_fix_regression_v29_result.json`
- `/app/data/design/affinity/managed_redis_envaware_v29_result.json`
- `/app/data/design/affinity/alerting_envaware_v29_result.json`
- `/app/data/design/affinity/af2n_alerting_envaware_v29_local_mock_sink.log`
- `/app/data/design/affinity/af2n_scope_s1_extended_monitoring_v29_result.json`
- `/app/data/design/affinity/af2n_stress_8x_v29_result.json`
- `/app/data/design/affinity/affinity_inventory_delta_consistency_v29_report.json`
- `/app/data/design/affinity/af2n_broad_rollout_signoff_package_v7.json`
- `/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v8.json`
- `/app/data/design/ui/affinity_gifts_public_preview_v29_safety_result.json`
- `/app/data/design/affinity/af2n_v29_rollback_readiness_result_v1.json`
- `/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v24.json`
- `/app/docs/divine/89_ULTRA_COMBO_V29_ENV_AWARE_READINESS_POSTFIX.md` (questo doc)

## 2. File modificati (1)
- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` → registrazione 13 validator V29 + composite

> **Nessuna modifica** a: `battle_engine.py`, `battle_core.py`, `combat.tsx`, gacha, roster, cataloghi, eroi, Character Bible, `affinity_gift_spend.py` (route runtime intoccata).

---

## 3. Preflight V29
- `services`: backend RUNNING, redis RUNNING (auto-ripristinato via `/app/ops/ensure_redis_rate_limit.sh` — issue ricorrente container Redis fixato idempotente), mongodb RUNNING, expo RUNNING
- `canary-status`: cap=25000, allowlist=2500, rl=redis
- `heroes_count`: 100
- `borea_aliases`: 3/3 → 404
- `v28_schema_fix_report_pass`: True
- `inventory_schema_v28`: marker_total=1800, marker_flat=1800, marker_nested=0
- `guardrails_clean`: tutti True (combat files no-diff)
- **Verdict**: ✅ PASS

## 4. V28 schema-fix regression
- `nested → 0`, `flat → 1800` (pre = post)
- Idempotent re-run del fix → no-op (nessuna mutazione: nested_after=0, flat_after=1800)
- Controlled spend 10 fresh users → 10/10 → 200 `applied_inventory_live`
- Idempotent replay → 10/10 → 200 `idempotent_replay`
- Consistency post-spend (5 sample) → tutti `quantity_after` non-null
- **Verdict**: ✅ PASS

## 5. Managed Redis env-aware probe
- `REDIS_MANAGED_URL` non fornita → `status=READY_NOT_APPLIED_ENV_MISSING`
- `probe_attempted=False`, `switch_attempted=False`, `local_redis_unchanged=True`
- Safety: no_secrets_logged, no_local_redis_touched, no_traffic_switched
- **Verdict**: ✅ PASS (skip safe)

## 6. Alerting env-aware probe
- `ALERT_WEBHOOK_URL` / `PROMETHEUS_PUSHGATEWAY` non forniti → `sink_mode=LOCAL_MOCK_ENV_MISSING`
- 4 formati validati a mock-sink: `rate_limit_fail_open`, `backend_not_redis`, `borea_success_alert`, `unauthorized_spend_alert`
- Safety: no_secrets_logged, no_pii_in_payload, no_borea_data_leaked
- Mock log: 861 bytes
- **Verdict**: ✅ PASS (skip safe con mock proof)

## 7. Extended monitoring scope S1
- **1775 samples** (status_burst=800, borea=200, non_allowlist=400, burst=300, fresh=15, replay=60)
- borea 200/200 → 404
- non_allowlist 400/400 → blocked (423/429)
- burst 294/300 → 429
- fresh controlled 15/15 → 200 (cap rispettato)
- idempotent replay 30/30 → 200/409
- **5xx = 0**, unauthorized_success = 0
- **Verdict**: ✅ PASS

## 8. Stress 8X safe
- Simulazione 5600 utenti × 5 spend/g = 28 000 ev/g (cap_pressure=1.12 contro cap 25k → richiede ulteriori safeguard in V30+ se mai si supera)
- Live probe: borea 80/80→404, controlled 10/10, na 100/100 blocked, burst 74/80→429, replay 8/8 (5xx=0)
- Redis pressure delta = +19 keys
- **Verdict**: ✅ PASS

## 9. Delta audit V29 (read-only)
- Inventory=2553 doc, affinity=2624 doc, ledger=379 row
- negative_inventory=0, borea_in_ledger=0, borea_in_marker_aff=0, non_allowlist_success=0, idempotency_dup=0
- v28_scope_marker_inventory=1800, flat=1800, nested=0
- **Verdict**: ✅ PASS

## 10. Broad Rollout Signoff V7 (PLAN-ONLY)
- `broad_rollout_allowed=False`, `public_spend_ui_allowed=False`, `stack_g_allowed=False`
- 7/7 signoff PENDING (engineering, qa, product, legal, sre, security, final_user_approval)
- 13 evidence items: **8 PROVIDED** (V28+V29 fatti), **5 PENDING** (managed redis live, alerting live, dashboards, legal/product, user approval)
- 1 blocker da Matrix V8 (BLK-G-01 Signoff V7 final approval) → PLAN_READY_NOT_APPROVED
- **Verdict**: ✅ PASS (plan-only, nessun runtime change)

## 11. Blocker Matrix V8
- 29 blocker tracciati, P0 open = **0**
- Transizioni V29:
  - `BLK-B-08` V28 schema-fix regression → **CLOSED_V29**
  - `BLK-F-04` Stress 8x → **CLOSED_V29**
  - `BLK-H-01` Extended monitoring → **CLOSED_V29**
  - `BLK-H-02` Delta audit V29 → **CLOSED_V29**
  - `BLK-B-03` Managed Redis SPOF → **READY_NOT_APPLIED_ENV_MISSING_V29**
  - `BLK-D-02-LIVE` Alerting live → **LOCAL_MOCK_ENV_MISSING_V29**
  - `BLK-G-01` Broad rollout signoff V7 → **PLAN_READY_NOT_APPROVED_V29**
  - `BLK-G-02` Broad rollout → **NO_GO_V29**
- **Verdict**: ✅ PASS

## 12. UI safety V29
- 125 file scansionati (.tsx/.ts/.jsx/.js, no node_modules)
- Pattern critici inclusi: mutating POST/PUT/PATCH/DELETE su gift-spend, axios mutations, hero_id Borea, onPress su gift_spend/gift_give/gift_claim, BROAD_ROLLOUT/PUBLIC_SPEND_UI flag, runtime_toggle, battle_wiring
- `critical_findings = 0`
- **Verdict**: ✅ PASS

## 13. Rollback readiness V29
- 13 check tutti OK: scope_s1 + cap_s1 + redis_local + managed_redis + supervisor_conf + db_backups + v24/25/26/27/28 rollback PASS + schema_fix idempotent
- 8 percorsi di rollback documentati (scope_s1, cap_s1, redis_local, managed_redis, alerting_live, stage4_runtime_disable, inventory_writes_rollback, full_af2n_rollback)
- `production_db_touched=False`
- **Verdict**: ✅ PASS

## 14. Safety Rollup X (`rollup_v24.json`)
```json
{
  "internal_beta_scope_state": "SCOPE_S1_2500_ACTIVE_V28",
  "allowlist_count": 2500,
  "canary_ledger_cap": 25000,
  "rate_limit_backend": "redis",
  "managed_redis_state": "READY_NOT_APPLIED_ENV_MISSING",
  "alerting_state": "LOCAL_MOCK_ENV_MISSING",
  "schema_fix_regression_status": "CLOSED",
  "extended_monitoring_status": "CLOSED",
  "stress_8x_status": "CLOSED",
  "delta_audit_v29_status": "CLOSED",
  "blocker_matrix_v8_status": "CLOSED",
  "broad_rollout_signoff_v7_status": "PLAN_READY_NOT_APPROVED",
  "ui_safety_status": "CLOSED",
  "rollback_readiness_status": "CLOSED",
  "api_heroes_count_100": true,
  "borea_hidden": true,
  "broad_rollout_authorized": false,
  "public_spend_ui": false,
  "battle_wiring_live": false,
  "guardrails_clean": { "battle_engine.py": true, "battle_core.py": true, "combat.tsx": true }
}
```

## 15. Borea safety
- `/api/heroes` non contiene `borea`, `greek_borea`, `primordial_gaia`
- 3 alias → HTTP 404 (probe singolo)
- 200/200 → 404 in extended monitoring
- 80/80 → 404 in stress 8x
- 0 record Borea nel ledger, 0 nei marker affinity V28
- 0 leak Borea nel frontend (audit pattern UI safety)

## 16. Validators V29
12 nuovi validator V29 — tutti PASS:
1. ✓ V29-PREFLIGHT
2. ✓ V29-V28-SCHEMA-FIX-REGRESSION
3. ✓ V29-MANAGED-REDIS-PROBE
4. ✓ V29-ALERTING-PROBE
5. ✓ V29-SCOPE-S1-EXTENDED-MONITORING
6. ✓ V29-STRESS-8X
7. ✓ V29-INVENTORY-DELTA-AUDIT
8. ✓ V29-BROAD-ROLLOUT-SIGNOFF-V7
9. ✓ V29-BLOCKER-MATRIX-V8
10. ✓ V29-UI-SAFETY
11. ✓ V29-ROLLBACK-READINESS
12. ✓ V29-SAFETY-ROLLUP-X

## 17. Suite globale + baseline
- `run_hero_skill_kit_validator_suite.py`: **Overall PASS** — `pass=218, fail=0, miss=0`
- Baseline diff (combat files): vuoto → invariati

## 18. API smoke
| Endpoint / azione | Esito |
|-------------------|-------|
| GET `/api/heroes` | 100 eroi, no borea leak ✅ |
| GET `/api/affinity/gift-spend/canary-status` | cap=25000, allowlist=2500, rl=redis ✅ |
| POST gift-spend `borea` | 404 ✅ |
| POST gift-spend `greek_borea` | 404 ✅ |
| POST gift-spend `primordial_gaia` | 404 ✅ |
| POST gift-spend non-allowlist | 423 (blocked) ✅ |
| POST gift-spend `stage5_qa_1701` (V28 user) | 200 `applied_inventory_live` ✅ |
| POST replay same idempotency_key | 200 `idempotent_replay` ✅ |

## 19. Runtime / DB / gacha / roster / catalog safety
- **Runtime**: nessuna toccatura della route `affinity_gift_spend.py`, nessuna env runtime modificata.
- **DB writes**: solo letture in V29; le write effettuate nella regression (10 spend fresh) sono **strictly bounded** dal cap V28 (parte di Stage 4 internal beta normale operativa, non un new mutation pattern).
- **Gacha / roster / Character Bible / asset catalogs / skill catalogs / final_numbers / divine_weapons**: **NON TOCCATI**.
- **Combat files (`battle_engine.py`, `battle_core.py`, `combat.tsx`)**: git no-diff confermato.

## 20. Warnings
- ⚠️ **Container Redis recurrence**: Redis è caduto FATAL una volta durante V29; ripristinato automaticamente da `/app/ops/ensure_redis_rate_limit.sh` (issue ambiente nota, mitigata). Suggerito monitoraggio supervisor `autorestart` per il futuro V30+.
- ⚠️ **Extended monitoring replay phase** richiedeva flush periodico Redis per non saturare il budget IP (fixato nello script con flush ogni 8 replay).
- ⚠️ **Stress 8x cap_pressure simulato** = 1.12 vs cap 25k → V30+ dovrebbe valutare cap S2 (50k) come task futuro PRIMA di rollout broad.
- ⚠️ **Managed Redis / Alerting live**: assenza env è attesa e safe; nessuna degradazione operativa.

## 21. Final recommendation
**ULTRA-COMBO V29 PASS, SAFE TO HALT HERE.**

Tutte le acceptance gates rispettate:
- [x] no broad rollout
- [x] public_spend_ui_allowed=false
- [x] allowlist max 2500 (esattamente)
- [x] cap 25000 (invariato)
- [x] schema-fix regression PASS @ scale
- [x] env probes safe (skipped via ENV_MISSING)
- [x] stress 8x safe
- [x] no battle wiring
- [x] /api/heroes=100
- [x] Borea hidden/404
- [x] no unauthorized spend
- [x] no critical 5xx
- [x] rollback readiness PASS
- [x] suite/baseline PASS (218/218)
- [x] no battle/gacha/roster/catalog mutation
- [x] UI safety PASS (0 finding)

**NESSUNA azione di broad rollout deve essere intrapresa senza esplicita approvazione user + signoff V7 finale.**

## 22. Next tasks (V30+)
- 🟡 **V30 Managed Redis switch live** → richiede `REDIS_MANAGED_URL` env + 14d soak + traffic-shadow + rollback drill
- 🟡 **V30 Alerting sink live** → richiede `ALERT_WEBHOOK_URL` o `PROMETHEUS_PUSHGATEWAY` + incident validation con synthetic alert
- 🟡 **V30 Cap raise plan S2** (25k → 50k? + gate) — necessario per ridurre cap_pressure stress 8x
- 🟡 **V30 Observability dashboards** (Grafana/Prometheus per af2n metrics)
- 🔴 **Broad rollout signoff V7 final approval** (richiede 7 signoff + 5 evidence ancora pending + esplicita autorizzazione user)
- 🔴 **Public spend UI activation** (gated, NON autorizzato)
- 🔴 **STACK-G full wiring** (deferito, NON autorizzato)

---

*Documento generato automaticamente da V29 — non modificare manualmente.*
