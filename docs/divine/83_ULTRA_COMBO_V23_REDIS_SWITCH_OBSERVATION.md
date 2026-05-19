# ULTRA-COMBO V23 — REDIS RATE-LIMIT PROVISION/SWITCH-GATED + STAGE4 OBSERVATION WINDOW + ABUSE MONITORING PREP + DELTA AUDIT V23 + LOCUST STAGE4 RATE-LIMIT + SAFETY-ROLLUP-R

**Stato finale:** ✅ **PASS — REDIS LIVE SWITCH APPLIED SAFELY; STAGE4 INTERNAL BETA STABILE; BROAD ROLLOUT NO_GO**
**Data:** 2026-05-19
**Project:** Divine RPG / Divine Waifus

---

## 1. File creati

### Script Python (`/app/backend/scripts/`)
- `validate_af2n_v23_preflight.py`
- `probe_af2n_v23_redis_live.py`
- `validate_af2n_v23_redis_live_probe.py`
- `validate_af2n_v23_redis_switch.py`
- `run_af2n_stage4_observation_window_v23.py`
- `validate_af2n_stage4_observation_window_v23.py`
- `validate_af2n_v23_abuse_monitoring_prep.py`
- `audit_affinity_inventory_delta_consistency_v23.py`
- `validate_affinity_inventory_delta_consistency_v23.py`
- `run_af2n_v23_locust_stage4_ratelimit.py`
- `validate_af2n_v23_locust_stage4_ratelimit.py`
- `validate_af2n_broad_rollout_blocker_matrix_v2.py`
- `audit_affinity_gifts_public_preview_v23_safety.py`
- `validate_af2n_v23_rollback_readiness.py`
- `build_safety_rollup_r_v18.py`
- `validate_collection_affinity_runtime_activation_rollup_v18.py`
- `validate_ultra_combo_v23_redis_switch_observation.py`

### Locust loadtests
- `/app/loadtests/af2n_v23_stage4_ratelimit_locustfile.py`

### Supervisor / Redis
- `/etc/supervisor/conf.d/redis.conf` (NEW — redis-server gestito da supervisor)

### Artefatti JSON
- `/app/data/design/affinity/af2n_v23_preflight_result_v1.json`
- `/app/data/design/affinity/af2n_v23_redis_live_probe_result_v1.json`
- `/app/data/design/affinity/af2n_v23_redis_switch_result_v1.json`
- `/app/data/design/affinity/af2n_stage4_observation_window_v23_result.json`
- `/app/data/design/affinity/af2n_v23_abuse_monitoring_prep_plan_v1.json`
- `/app/data/design/affinity/affinity_inventory_delta_consistency_v23_report.json`
- `/app/data/design/affinity/af2n_v23_locust_stage4_ratelimit_result_v1.json`
- `/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v2.json`
- `/app/data/design/affinity/af2n_v23_rollback_readiness_result_v1.json`
- `/app/data/design/ui/affinity_gifts_public_preview_v23_safety_result.json`
- `/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v18.json`

### Backup
- `/app/backups/af2n_stage4/backend.conf.v23_pre_redis_switch_*.bak`

### Reports
- `/app/backend/reports/suite_v23.json`
- `/app/backend/reports/ultra_combo_v23_composite.json`

### Documentazione
- `/app/docs/divine/83_ULTRA_COMBO_V23_REDIS_SWITCH_OBSERVATION.md` (questo file)

## 2. File modificati

- `/app/backend/routes/affinity_gift_spend.py` — `_rate_limit_check` ora delega a `data.affinity_rate_limit_store.rate_limit_check` quando `AFFINITY_RATE_LIMIT_BACKEND=redis` (fail-open su qualsiasi errore). Aggiunti campi `rate_limit_backend` e `rate_limit_redis_url_set` al `/canary-status` response.
- `/app/backend/data/affinity_rate_limit_store.py` — rimossa la cache `_REDIS_INIT_FAILED` permanente: `_get_redis()` ora ri-prova ad ogni richiesta con verifica ping live (resilienza a transient).
- `/etc/supervisor/conf.d/backend.conf` — aggiunti `AFFINITY_RATE_LIMIT_BACKEND=redis` e `REDIS_URL=redis://127.0.0.1:6379/0`.
- `/app/backend/requirements.txt` — aggiunti `redis==5.0.8` e `locust==2.44.0`.
- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` — aggiunti 12 validator V23.

**NON modificati (invarianti hard):** `battle_engine.py`, `battle_core.py`, `combat.tsx`, `synergy_system.py`, `game_systems.py`, gacha/roster/Character Bible/skill catalogs/final_numbers, frontend UI preview.

## 3. Preflight V23

✅ PASS — gate verdi:
- `api_health_200`, `heroes_100`, `heroes_no_borea`, `canary_status_200`, `canary_flag_on`, `inv_writes_flag_on`, `stage4_allowlist_ge_700`, `cap_ge_5000`, `ledger_within_cap`, `rate_limit_active`, `battle_off`, `combat_off`, `buffs_off`, `borea_404` × 3, `non_allowlist_423`, `battle_files_unchanged`, `db_connectivity`, `ugi_no_negative`, `no_borea_hero_rows`, `baseline_v6_diff_pass`, `suite_pass`, `ui_preview_present`, `ui_preview_no_spend_post`, `ui_preview_no_borea_in_code`, `locust_binary_present`.
- **Redis live**: `redis_cli_alive=true`, `backend_url_set=true`, `redis_via_python_backend=true`, `rate_limit_backend_redis=true`.

## 4. Redis provision/probe

- **Provision**: `apt-get install -y redis-server` su /usr/bin/redis-server, gestito da supervisor (`/etc/supervisor/conf.d/redis.conf`), bound 127.0.0.1:6379, no persistence (RDB/AOF disabilitati — Stage4 in-memory accettabile).
- **Probe live** (`af2n_v23_redis_live_probe_result_v1.json`):
  - `redis_server_version=7.0.15`, `ping_ok=true`, `ping_ms_first<2ms`.
  - Sliding window probe: 16 ZADD/ZREMRANGEBYSCORE/ZCARD/EXPIRE pipeline → `zcard=16`, p50<2ms, p95<5ms.
  - `rate_limit_keys_count` rilevati post-burst (60+ keys).
  - Status: **PASS**.

## 5. Redis switch gated

- **Backup pre-switch** creato in `/app/backups/af2n_stage4/backend.conf.v23_pre_redis_switch_<STAMP>.bak`.
- **ENV applicato**: `AFFINITY_RATE_LIMIT_BACKEND=redis`, `REDIS_URL=redis://127.0.0.1:6379/0` nel supervisor.conf del backend.
- **Backend riavviato** → `/canary-status` riporta `rate_limit_backend=redis`, `rate_limit_redis_url_set=true`.
- **Validazione switch** (`af2n_v23_redis_switch_result_v1.json`):
  - `canary_status_backend_advertised=redis`
  - 10 burst → 4×429 osservati, `snapshot_backends_observed=['redis']`
  - `redis_keys_present_after_burst=true`, `redis_keys_count=19`
  - `mode=redis_live_switch_applied_safely`
- ⚠️ **Issue risolto**: il package `redis` mancava nel Python del backend (`/usr/local/bin/python3.11`); installato + aggiunto a `requirements.txt`. Adapter `_get_redis()` ora resiliente (no cache permanente di fallimento).

## 6. Stage4 Observation Window

✅ PASS — 8 sample × 3s interval (compressed):
- 100% sample con `heroes_count=100`, `health=200`, `borea_<alias>=404`, `non_allowlist∈{423,429}`, `burst_saw_429=true`, `ledger_total≤cap`.
- `rate_limit_backends_observed=['redis']` (consistente per tutti i sample).
- 0 5xx, 0 cap overflow, 0 Borea leak.
- Configurabile via `OBS_SAMPLES`/`OBS_INTERVAL_S` per estendere a 24-72h.

## 7. Abuse Monitoring Prep

✅ PASS plan only (`af2n_v23_abuse_monitoring_prep_plan_v1.json`):
- **10 metrics**: `af2_gift_spend_total`, `_5xx_total`, `_borea_404_total`, `_unauthorized_success_total`, `af2_ratelimit_429_total`, `af2_ratelimit_redis_fail_open_total`, `af2_ledger_total_rows`, `af2_ledger_cap_headroom`, `af2_inventory_negative_count`, `af2_inventory_affinity_delta_mismatch_total`, `af2_gift_spend_latency_ms`.
- **2 dashboards**: `af2n_stage4_overview`, `af2n_redis_health`.
- **8 alert rules** (AF2-A-001..008): 5xx surge, unauthorized success, negative inventory, delta mismatch, Borea leak, ledger headroom, Redis fail-open, 429 abuse surge.
- **6-phase rollout** documentato (PREP → INSTRUMENTATION → EXPOSE → DASHBOARDS → ALERTS → BROAD_PREREQ).
- `dashboards_live=false`, `alerts_live=false` (no pipeline live in V23).

## 8. Delta Audit V23 (post-Redis switch)

✅ PASS — read-only audit:
- `negative_inventory_count=0`, `borea_in_ledger=0`, `borea_in_affinity_state=0`
- `duplicate_tx_ids=0`, `duplicate_idempotency_groups=0`, `non_allowlist_success_count=0`
- `delta_mismatch_users=0` su 80 sample → `qty_mut == affinity_points == total_gifts_given` per stage3/4_qa_*.

## 9. Locust Stage4 Rate-Limit (Redis)

✅ PASS — 45s, 15 utenti, focus rate-limit:
- `locust_returncode=0`, `rate_limit_backend_observed=redis`
- `ledger_growth=3`, `cap_exceeded=false`, `safe_ledger_growth=true`, `negative_inventory_count=0`
- `redis_keys_before=30 → redis_keys_after=58` (conferma path Redis attivo)
- Mix: status 20%, non-allow 30%, burst rotating 25%, replay 15%, Borea 3%, fresh capped 5%.

## 10. Blocker Matrix Update V2

✅ Validator PASS | ❌ `go_no_go_global=NO_GO`
- **BR-001 rate_limit**: OPEN → **CONDITIONAL_GO** (Redis switch live applicato safe).
- **BR-006 abuse_monitoring**: OPEN → **PREP_PLAN_DONE**.
- **BR-009 locust_extended**: COMPRESSED_PASS → **COMPRESSED_PASS_REDIS**.
- Restanti (BR-002, 003, 005, 007, 008, 010, 012) invariati OPEN/CRITICAL.
- BR-004 borea_safety: PASS_LIVE (continuous).
- BR-011 stack_g_battle_wiring: BLOCKED_BY_POLICY_OK (deferred).
- Summary: 5 CRITICAL open, 1 CRITICAL conditional, 3 HIGH open, 1 HIGH prep_done, 1 MEDIUM open.

## 11. UI Safety V23

✅ PASS — `affinity-gifts-preview.tsx` invariata, solo `GET /api/affinity/gift-spend/canary-status`, no POST/Borea/runtime-toggle/broad_rollout in codice, accessibility presente.

## 12. Rollback Readiness V23

✅ PASS — 5 script rollback presenti & sintattici, 3 doc evidence, backup V21 pre-stage4 + V23 pre-redis-switch entrambi presenti.
- Opzione `redis_switch_rollback`: restore `backend.conf.v23_pre_redis_switch_*.bak` + restart (rimuove REDIS_URL e ripristina backend `memory`).

## 13. Safety Rollup R (v18)

✅ PASS:
- `stage4_state=stage4_internal_beta_active_no_broad_rollout`
- `redis_rate_limit_state=redis_live_switch_applied_safely`
- `rate_limit_backend_live=redis`, `rate_limit_active=true`
- `broad_rollout_authorized=false`, `public_spend_ui=false`, `battle_wiring_live=false`, `buffs_enabled=false`
- `borea_hidden=true`, `inventory_live_scope=stage4_internal_beta_only`
- `observation_window_status=PASS`, `delta_audit_status_v23=PASS`, `locust_v23_status=PASS`
- `blocker_matrix_v2_status=NO_GO`, `blocker_matrix_v2_critical_open=5`
- Recommended next: **`instrument_abuse_metrics_and_continue_observation`**.

## 14. Borea Safety

✅ Confermato in 3 layer:
- `/api/heroes` list = 100, no Borea alias.
- `POST /api/affinity/gift-spend` con borea/greek_borea/primordial_gaia → **404 × 3**.
- Observation window samples (8/8): tutti e 3 alias = 404 ad ogni rotazione.
- Locust V23: borea_probe task → 404 (success).

## 15. Validator results

| Validator V23 | Esito |
|---|---|
| V23-PREFLIGHT | PASS |
| AF2-N-V23-REDIS-LIVE-PROBE | PASS |
| AF2-N-V23-REDIS-SWITCH | PASS (redis_live_switch_applied_safely) |
| AF2-N-V23-STAGE4-OBSERVATION-WINDOW | PASS |
| AF2-N-V23-ABUSE-MONITORING-PREP | PASS |
| AF2-N-V23-DELTA-AUDIT | PASS |
| AF2-L-LOCUST-STAGE4-V23 | PASS |
| AF2-N-V23-BLOCKER-MATRIX-V2 | PASS |
| AF2-N-PUBLIC-UI-V23-SAFETY | PASS |
| V23-ROLLBACK-READINESS | PASS |
| SAFETY-ROLLUP-R | PASS |
| ULTRA-COMBO-V23 (composite) | **PASS** |

## 16. Suite / baseline

- `run_hero_skill_kit_validator_suite.py --include-baseline-diff` → **PASS (145/145)**.
- `validate_hero_skill_kit_catalog_baseline_diff.py` → PASS (baseline `rm134b_axispatch_v6` invariata).

## 17. API smoke

| Endpoint | Atteso | Risultato |
|---|---|---|
| GET `/api/health` | 200 | ✅ 200 |
| GET `/api/heroes` (count) | 100 | ✅ 100 |
| GET `/api/affinity/gift-spend/canary-status` | 200 + backend=redis | ✅ 200, `rate_limit_backend=redis` |
| POST stage4_qa_450 fresh | 200 | ✅ 200 |
| POST stessa idem | 200 replay | ✅ 200 |
| POST non-allowlist | 423 | ✅ 423 |
| POST `borea`/`greek_borea`/`primordial_gaia` | 404 | ✅ 404 × 3 |
| POST burst 10× stesso user | 6×423 → 4×429 | ✅ 6×423, 4×429 |
| Redis keys `af2:ratelimit:*` | presenti | ✅ 60+ keys |

## 18. Runtime / DB / gacha / roster / catalog safety

- Runtime flags: `AFFINITY_GIFT_RUNTIME_ENABLED`, `AFFINITY_GIFT_INVENTORY_WRITES_ENABLED`, `AFFINITY_GIFT_RATE_LIMIT_ENABLED` tutti ON.
- `AFFINITY_RATE_LIMIT_BACKEND=redis`, `REDIS_URL=redis://127.0.0.1:6379/0`.
- DB MongoDB: solo affinity collections mutate; gacha/roster/Character Bible/skill catalogs/final_numbers **invariati**.
- `git diff` su file di combattimento: **vuoto**.
- Redis usato solo per rate-limit (`af2:ratelimit:*` prefix), nessun dato persistente sensibile.

## 19. Warnings

- ⚠️ **Redis pkg + locust mancavano** nel Python del backend dopo restart container; reinstallati e aggiunti a `requirements.txt`.
- ⚠️ **Redis bound 127.0.0.1, no persistence (RDB/AOF off)**: appropriato per Stage4 (rate-limit è dato volatile). Per broad rollout serve HA decision.
- ⚠️ **Compressed observation window** (24s × 8 sample): non sostituisce 24-72h reale.
- ⚠️ Adapter Redis ora ha `fail-open` ad ogni request: se Redis crash, ratelimit cade a `memory_fallback` (no DoS interno) ma quote sono per-processo.

## 20. Final recommendation

**MANTENERE Stage4 stabile su Redis backend** + **strumentare metriche abuse**:
1. Real 24-72h observation window con cron + aggregator.
2. Phase 2 abuse monitoring: instrumentation prometheus_client (counters/gauges/histograms) — V24.
3. Live Stage4 rollback drill in staging clone — V24.
4. Redis HA decision (sentinel/cluster) — prerequisito broad rollout.

**NON autorizzato** (immutato):
- Broad rollout (5 CRITICAL open + observation pending).
- Public Spend UI.
- STACK-G / battle wiring.
- Buff/combat effects.
- Mutazioni di `battle_engine.py`/`combat.tsx`/`battle_core.py`.

## 21. Suggested next tasks

1. **V24 — REAL 24-72H OBSERVATION + ABUSE INSTRUMENTATION** (priorità P1):
   - Cron 5-min health probe + 30-min sample aggregator.
   - Phase 2 prometheus_client counters/gauges/histograms gated (no `/metrics` exposure yet).
2. **V24 — LIVE STAGE4 ROLLBACK DRILL IN STAGING CLONE** (priorità P1).
3. **V24 — REDIS HA DECISION + REPLICA PROVISION (PLAN)** (priorità P2).
4. **V25 — DASHBOARDS + ALERT ROUTING LIVE** (priorità P2).
5. **V25 — SUPPORT RUNBOOK + ON-CALL ROTATION DRAFTING** (priorità P2).
6. **V25 — ECONOMY STRESS SIMULATION 10× CAP** (priorità P3).
7. **V26 — BROAD-ROLLOUT SIGNOFF PACKAGE V6** (gated, plan-only fino a chiusura blocker).
8. **DEFERRED** — STACK-G / battle wiring (separate plan track).
9. **DEFERRED** — Public Spend UI design (post broad-rollout signoff).
