# ULTRA-COMBO V22 — STAGE4 EXTENDED MONITORING + REDIS RATE-LIMIT MIGRATION PREP + INVENTORY/AFFINITY DELTA AUDIT + LOCUST STAGE4 EXTENDED + BROAD-ROLLOUT BLOCKER MATRIX + SAFETY-ROLLUP-Q

**Stato finale:** ✅ **PASS — STAGE4 INTERNAL BETA STABILE; REDIS MIGRATION READY_NOT_APPLIED; BROAD ROLLOUT NO_GO**
**Data:** 2026-05-18
**Project:** Divine RPG / Divine Waifus

---

## 1. File creati

### Script Python (`/app/backend/scripts/`)
- `validate_af2n_v22_preflight.py`
- `run_af2n_stage4_extended_monitoring_v22.py`
- `validate_af2n_stage4_extended_monitoring_v22.py`
- `audit_affinity_rate_limit_redis_migration_plan.py`
- `probe_affinity_rate_limit_redis_backend.py`
- `validate_affinity_rate_limit_redis_probe.py`
- `audit_affinity_inventory_delta_consistency_v22.py`
- `validate_affinity_inventory_delta_consistency_v22.py`
- `run_af2n_v22_locust_stage4_extended.py`
- `validate_af2n_v22_locust_stage4_extended_result.py`
- `validate_af2n_broad_rollout_blocker_matrix.py`
- `audit_affinity_gifts_public_preview_v22_safety.py`
- `validate_af2n_v22_rollback_readiness.py`
- `build_safety_rollup_q_v17.py`
- `validate_collection_affinity_runtime_activation_rollup_v17.py`
- `validate_ultra_combo_v22_stage4_monitoring_redisprep.py`

### Adapter PREP (`/app/backend/data/`)
- `affinity_rate_limit_store.py` — abstraction per-process con backend `memory|redis`, default `memory`, fail-open su Redis init/runtime error.

### Locust loadtests
- `/app/loadtests/af2n_v22_stage4_extended_locustfile.py`

### Artefatti JSON
- `/app/data/design/affinity/af2n_v22_preflight_result_v1.json`
- `/app/data/design/affinity/af2n_stage4_extended_monitoring_v22_result.json`
- `/app/data/design/affinity/affinity_rate_limit_redis_migration_plan_v1.json`
- `/app/data/design/affinity/affinity_rate_limit_redis_probe_result_v1.json`
- `/app/data/design/affinity/affinity_inventory_delta_consistency_v22_report.json`
- `/app/data/design/affinity/af2n_v22_locust_stage4_extended_result_v1.json`
- `/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v1.json`
- `/app/data/design/affinity/af2n_v22_rollback_readiness_result_v1.json`
- `/app/data/design/ui/affinity_gifts_public_preview_v22_safety_result.json`
- `/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v17.json`

### Reports
- `/app/backend/reports/suite_v22.json`
- `/app/backend/reports/ultra_combo_v22_composite.json`

## 2. File modificati

- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` — aggiunti 11 validator V22.

**NON modificati (invarianti hard):** `battle_engine.py`, `battle_core.py`, `combat.tsx`, `synergy_system.py`, `game_systems.py`, gacha/roster/Character Bible/skill catalogs/final_numbers, `/etc/supervisor/conf.d/backend.conf` (nessun env change in V22), `affinity_gift_spend.py`.

## 3. Preflight V22

✅ PASS — gate critici verdi:
- `api_health_200`, `heroes_100`, `heroes_no_borea`, `canary_status_200`, `canary_flag_on`, `inv_writes_flag_on`, `stage4_allowlist_ge_700`, `cap_ge_5000`, `ledger_within_cap`, `rate_limit_active`, `battle_off`, `combat_off`, `buffs_off`, `borea_404` × 3 alias, `non_allowlist_423`, `battle_files_unchanged`, `db_connectivity`, `ugi_no_negative`, `no_borea_hero_rows`, `baseline_v6_diff_pass`, `suite_pass`, `ui_preview_present`, `ui_preview_no_spend_post`, `ui_preview_no_borea_in_code`, `locust_binary_present`, `locust_version_known`, `py_redis_pkg_present`.
- **Redis availability** (informational): `redis-server` ❌, `redis-cli` ❌, `REDIS_URL` ❌, `python-redis` ✅ → `overall_redis_available=false` → migration restera in PREP.

## 4. Stage4 Extended Monitoring

✅ PASS — **366 sample** (compressed observation window):
- 80 health/status polls, 30 Borea 404 probes × 3 alias, 80+80 non-allowlist (diversi user_id), 12 burst rate-limit, 10 fresh Stage4 + replay con delta inv/affinity check, 60 idem-sweep, 0 critical 5xx, 0 negative inventory, 0 Borea row in ledger, 0 duplicate idempotency.
- Status counts: `{200, 404, 423, 429}` — nessun 5xx, nessun unauthorized 200.

## 5. Redis Rate-Limit Migration PREP

✅ PASS (PREP only) — `affinity_rate_limit_redis_migration_plan_v1.json` documenta:
- limitazioni attuali (in-memory, no shared, no persistent)
- target Redis (sliding-window via ZADD+ZREMRANGEBYSCORE+ZCARD+EXPIRE, atomic pipeline)
- chiavi `af2:ratelimit:user:{id}`, `af2:ratelimit:ip:{ip}`, `af2:ratelimit:burst:{id}`
- TTL 15s/65s/3605s
- fallback FAIL_OPEN→memory (canary safety)
- piano rollout 4-fase (PREP→DRY_RUN_LOCAL→GATED_LIVE→BROAD_ROLLOUT_PREREQ)
- rollback runtime via toggle env + restart, RTO 30s
- metrics + alert plan
- `live_switch_allowed_this_task=false`

✅ Adapter skeleton `/app/backend/data/affinity_rate_limit_store.py` con `rate_limit_check()` API duale (memory/redis), default memory, gated.

Probe: `READY_NOT_APPLIED` (REDIS_URL non set) — validator accetta come safe.

## 6. Inventory/Affinity Delta Audit

✅ PASS — audit read-only su 3 collezioni:
- `negative_inventory_count=0`
- `borea_in_ledger=0`, `borea_in_affinity_state=0`
- `duplicate_tx_ids=0`, `duplicate_idempotency_groups=0`
- `inconsistent_canary_markers=0`
- `non_allowlist_success_count=0`
- `idempotency_distinct_tx_ids=0` (ogni (user_id, key) → unico tx_id)
- `delta_mismatch_users=0` su sample 60 utenti stage3/4 → `qty_mut == affinity_points == total_gifts_given` ✅
- `stage4_seed_inv_rows=500` (consistente con apply V21)

## 7. Locust Stage4 Extended

✅ PASS — 60s, 15 utenti virtuali, rampa 5/s:
- Mix: canary-status 25%, non-allowlist 35%, replay 25%, burst 10%, fresh-capped 5%, Borea 3%
- `locust_returncode=0`, `ledger_growth=1`, `cap_exceeded=false`, `negative_inventory_count=0`, `safe_ledger_growth=true`
- Tutti gli status code attesi (200/404/423/429) marcati esplicitamente come success.

## 8. Broad-Rollout Blocker Matrix

✅ PASS validator | ❌ **`go_no_go_global=NO_GO`** — 12 blocker:
| ID | Area | Severity | Stato | GO/NO_GO |
|---|---|---|---|---|
| BR-001 | rate_limit (Redis) | CRITICAL | OPEN | NO_GO |
| BR-002 | observation_window 24-72h | CRITICAL | IN_PROGRESS | NO_GO |
| BR-003 | public_spend_ui | CRITICAL | BLOCKED_BY_POLICY | NO_GO |
| BR-004 | borea_safety | CRITICAL | PASS_LIVE | GO_PER_THIS_BLOCKER |
| BR-005 | rollback_drills (live) | HIGH | OPEN | NO_GO |
| BR-006 | abuse_monitoring | HIGH | OPEN | NO_GO |
| BR-007 | support_ops_runbook | HIGH | OPEN | NO_GO |
| BR-008 | economy_caps_simulation | HIGH | OPEN | NO_GO |
| BR-009 | locust_extended | MEDIUM | COMPRESSED_PASS | NO_GO |
| BR-010 | db_backup_restore_rehearsal | HIGH | DRY_RUN_PASS_LIVE_OPEN | NO_GO |
| BR-011 | stack_g_battle_wiring | CRITICAL | BLOCKED_BY_POLICY | BLOCKED_BY_POLICY_OK |
| BR-012 | final_user_signoff_v6 | CRITICAL | NOT_GRANTED | NO_GO |

## 9. UI Safety Recheck

✅ PASS — `/app/frontend/app/affinity-gifts-preview.tsx`:
- No `method: 'POST'/'PUT'/'PATCH'/'DELETE'` in codice.
- Solo `GET /api/affinity/gift-spend/canary-status` (template literal validato).
- No Borea identifier in codice (solo nei commenti di sicurezza).
- No runtime toggle word, no broad_rollout term in codice.
- `accessibilityLabel`/`accessibilityRole` presenti.

## 10. Rollback Readiness V22

✅ PASS — 5 script di rollback presenti e sintatticamente validi, 4 doc di evidence presenti, backup pre-Stage4 V21 disponibile.
Opzioni di rollback documentate per: Stage4, rate-limit, redis-switch, inventory-flag, full AF2-N, DB backup restore.

## 11. Safety Rollup Q (v17)

✅ PASS:
- `stage4_state=stage4_internal_beta_active_no_broad_rollout`
- `redis_rate_limit_state=redis_ready_not_applied`
- `broad_rollout_authorized=false`, `public_spend_ui=false`, `battle_wiring_live=false`, `buffs_enabled=false`
- `borea_hidden=true`, `inventory_live_scope=stage4_internal_beta_only`, `rate_limit_active=true`
- `locust_extended_status=PASS`, `extended_monitoring_status=PASS`, `delta_audit_status=PASS`
- `blocker_matrix_status=NO_GO`, `blocker_matrix_total_open_critical=6`
- `rollback_ready=true`
- Recommended next: **`provision_redis_and_continue_stage4_observation`**.

## 12. Borea Safety

✅ Confermato in 3 layer:
- `/api/heroes` list → 100 esatti, no Borea alias.
- `POST /api/affinity/gift-spend` con hero_id ∈ {borea, greek_borea, primordial_gaia} → **404 × 3**.
- DB: `gift_transaction_ledger.borea_count=0`, `user_affinity_state.borea_count=0`.

## 13. Validator results

| Validator V22 | Esito |
|---|---|
| V22-PREFLIGHT | PASS |
| AF2-N-V22-STAGE4-EXTENDED-MONITORING | PASS |
| AF2-N-V22-REDIS-MIGRATION-PLAN-AUDIT | PASS |
| AF2-N-V22-REDIS-PROBE | PASS (READY_NOT_APPLIED, safe) |
| AF2-N-V22-DELTA-AUDIT | PASS |
| AF2-L-LOCUST-STAGE4-V22 | PASS |
| AF2-N-V22-BROAD-ROLLOUT-BLOCKER-MATRIX | PASS |
| AF2-N-PUBLIC-UI-V22-SAFETY | PASS |
| V22-ROLLBACK-READINESS | PASS |
| SAFETY-ROLLUP-Q | PASS |
| ULTRA-COMBO-V22 (composite) | **PASS** |

## 14. Suite / baseline

- `run_hero_skill_kit_validator_suite.py --include-baseline-diff` → **PASS (133/133)**.
- `validate_hero_skill_kit_catalog_baseline_diff.py` → PASS (baseline `rm134b_axispatch_v6` invariata).

## 15. API smoke

| Endpoint | Atteso | Risultato |
|---|---|---|
| GET `/api/health` | 200 | ✅ 200 |
| GET `/api/heroes` (count) | 100 | ✅ 100 |
| GET `/api/affinity/gift-spend/canary-status` | 200 | ✅ 200 |
| POST stage4_qa_350 fresh | 200 | ✅ 200 |
| POST stessa idempotency_key | 200 replay | ✅ 200 |
| POST non-allowlist | 423 | ✅ 423 |
| POST `borea`/`greek_borea`/`primordial_gaia` | 404 | ✅ 404 × 3 |
| POST burst 10× stesso user | primi 6 = 423, dopo = 429 | ✅ 6×423, 4×429 |

## 16. Runtime / DB / gacha / roster / catalog safety

- Runtime flags: `AFFINITY_GIFT_RUNTIME_ENABLED`, `AFFINITY_GIFT_INVENTORY_WRITES_ENABLED`, `AFFINITY_GIFT_RATE_LIMIT_ENABLED` tutti ON (V12/V16/V21).
- `AFFINITY_RATE_LIMIT_BACKEND` non settato → default `memory` (V22 PREP).
- `REDIS_URL` non settato → adapter Redis non inizializzato → nessun side effect.
- DB: solo affinity collections mutate; gacha/roster/Character Bible/skill catalogs/final_numbers **invariati**.
- `git diff` su file di combattimento: **vuoto**.

## 17. Warnings

- ⚠️ **Locust era stato disinstallato dal container** tra V21 e V22 (residuo di restart container). Reinstallato `locust==2.44.0` durante V22.
- ⚠️ Rate-limit ancora in-memory per processo (reset al restart, no shared across worker). Blocker BR-001 critico per broad rollout.
- ⚠️ `redis-server` non disponibile in ambiente → migration PREP-only.
- ⚠️ Compressed observation window (~3 min): non sostituisce 24-72h reale; usato come early indicator.

## 18. Final recommendation

**MANTENERE Stage4 stabile** + **provisionare Redis** prima di V23.
Eseguibili in parallelo:
1. Provisioning Redis locale (apt-get install redis-server + set REDIS_URL).
2. Real 24-72h Stage4 observation window con probe periodici.
3. Drafting support runbook + abuse dashboards.

**NON autorizzato** (immutato):
- Broad rollout (12 blocker aperti, 6 CRITICAL).
- Public Spend UI.
- STACK-G / battle wiring.
- Buff/combat effects.
- Mutazioni di `battle_engine.py`/`combat.tsx`/`battle_core.py`.

## 19. Suggested next tasks

1. **V23 — REDIS PROVISIONING + GATED SWITCH** (priorità P1):
   - Install redis-server, set REDIS_URL in supervisor.conf, run probe live, validate equivalence con memory backend, gated switch dopo signoff.
2. **V23+ — REAL 24-72h OBSERVATION WINDOW** (priorità P1):
   - Cron 5-min ping invariants + 30-min sample, alerting su 5xx, ledger growth, delta mismatch.
3. **V24 — LIVE STAGE4 ROLLBACK DRILL IN STAGING CLONE** (priorità P2).
4. **V24 — ABUSE DASHBOARDS + ALERT ROUTING IMPLEMENTATION** (priorità P2).
5. **V25 — ECONOMY STRESS SIMULATION 10× CAP** (priorità P3).
6. **V25 — SUPPORT RUNBOOK + ON-CALL ROTATION DRAFTING** (priorità P3).
7. **V26 — BROAD-ROLLOUT SIGNOFF PACKAGE V6** (gated, plan-only fino a chiusura tutti blocker CRITICAL/HIGH).
8. **DEFERRED** — STACK-G / battle wiring (separate plan track).
9. **DEFERRED** — Public Spend UI design (post broad-rollout signoff).
