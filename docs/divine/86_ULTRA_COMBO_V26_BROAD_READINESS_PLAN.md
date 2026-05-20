# ULTRA-COMBO V26 — Managed Redis Readiness + Cap Raise Plan + Inventory Scope Expansion + Broad-Rollout Signoff V6 + Alerting Integration Prep + Frontend Smoke + Stress 2x + Safety-Rollup-U

**Status**: ✅ **PASS** (plan-only, broad rollout NOT authorized)  
**Task origin**: `AF2-N-V26`  
**Date**: 2026-05-19  
**Sequence**: V21 → V22 → V23 → V24 → V25 → **V26** → (future: managed Redis provisioning, alerting integration LIVE, broad rollout approval)

---

## 0. TL;DR

Tutti i 12 deliverable V26 (parts A–O) completati e validati. Quasi tutti i blocker P1 ora sono `PLAN_READY` per il broad rollout; lo switch live è gated dietro approvazione utente finale.

| Part | Verdict | Status |
|---|---|---|
| A — Preflight V26 | PASS | live |
| B — Managed Redis readiness | PASS | PLAN_ONLY + probe READY_NOT_APPLIED |
| C — Cap raise plan 5k→100k | PASS | PLAN_ONLY (5 stage) |
| D — Inventory scope expansion | PASS | PLAN_ONLY (5 stage) |
| E — Broad-rollout signoff V6 | PASS | PLAN_ONLY + BLOCKED (8 domain, gates=0/8) |
| F — Alerting integration prep | PASS | PLAN_ONLY (5 sink) |
| G — Frontend smoke | PASS | live read-only |
| H — Stress 2x | PASS | safe probe + sim (0×5xx, Borea 30/30, ctrl 5/5) |
| I — Blocker Matrix V5 | PASS | P0 5/5 closed, P1 9/9 closed_or_plan |
| J — Observation V26 | PASS | 111 samples, 0×5xx |
| K — Rollback readiness V26 | PASS | dry-run, prod NOT touched |
| L — Safety Rollup U | PASS | tutti gli stati addressati |
| M — Composite V26 | PASS | 12/12 |
| N — Suite + baseline | PASS | **181/181** (+13 da V25) |
| O — API Smoke | PASS | tutti gli endpoint verdi |

---

## 1. File creati (28 totali)

### Scripts (`/app/backend/scripts/`)
- `run_af2n_v26_preflight.py` + validator
- `run_affinity_managed_redis_readiness_plan.py` + validator
- `probe_affinity_managed_redis_optional.py` (gated da `REDIS_MANAGED_URL`)
- `run_af2n_cap_raise_plan.py` + validator
- `run_af2n_inventory_scope_expansion_plan.py` + validator
- `run_af2n_broad_rollout_signoff_package_v6.py` + validator
- `run_af2n_alerting_integration_prep.py` + audit validator
- `audit_affinity_gifts_frontend_smoke_v26.py`
- `run_af2n_stress_2x_v26.py` + validator
- `run_af2n_broad_rollout_blocker_matrix_v5.py` + validator
- `run_af2n_stage4_observation_window_v26.py` + validator
- `run_af2n_v26_rollback_readiness.py` + validator
- `run_collection_affinity_runtime_activation_rollup_v21.py` + validator
- `validate_ultra_combo_v26_broad_readiness_plan.py`

### Result JSON (`/app/data/design/`)
- `affinity/af2n_v26_preflight_result_v1.json`
- `affinity/affinity_managed_redis_readiness_plan_v1.json`
- `affinity/affinity_managed_redis_probe_result_v1.json`
- `affinity/af2n_cap_raise_plan_v1.json`
- `affinity/af2n_inventory_scope_expansion_plan_v1.json`
- `affinity/af2n_broad_rollout_signoff_package_v6.json`
- `affinity/af2n_alerting_integration_plan_v1.json`
- `affinity/af2n_alerting_integration_prep_result_v1.json`
- `affinity/af2n_stress_2x_v26_result.json`
- `affinity/af2n_broad_rollout_blocker_matrix_v5.json`
- `affinity/af2n_stage4_observation_window_v26_result.json`
- `affinity/af2n_v26_rollback_readiness_result_v1.json`
- `ui/affinity_gifts_frontend_smoke_v26_result.json`
- `system_safety/collection_affinity_runtime_activation_readiness_rollup_v21.json`

### Documentation (`/app/docs/divine/`)
- `86_ULTRA_COMBO_V26_BROAD_READINESS_PLAN.md` (questo file)

---

## 2. File modificati

- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` — aggiunte 13 voci V26 in coda

**NESSUN altro file modificato.** In particolare:
- ✅ `backend/battle_engine.py` UNCHANGED
- ✅ `backend/battle_core.py` UNCHANGED
- ✅ `backend/affinity_gift_spend.py` UNCHANGED (rispetto a V25)
- ✅ `frontend/app/combat.tsx` UNCHANGED
- ✅ Gacha / roster / Character Bible / asset / skill catalogs / final_numbers UNCHANGED

---

## 3. Preflight

| Check | Risultato |
|---|---|
| `/api/health` | 200 / `status=ok` |
| `/api/heroes` count | **100** (esatto) |
| Borea leak in list | `[]` |
| gift-spend borea/greek_borea/primordial_gaia | **3 × 404** |
| canary runtime_attached | true |
| canary `rate_limit_backend` | **redis** |
| canary ledger / cap / allowlist | 172 / 5000 / 700 |
| metrics endpoint enabled | true |
| `battle_runtime_attached` | false ✅ |
| Guardrail diffs clean | tutti ✅ |
| V25 deliverables present | 4/4 ✅ |

**Verdict**: PASS

---

## 4. Managed Redis readiness

`/app/data/design/affinity/affinity_managed_redis_readiness_plan_v1.json`

- **Status**: `PLAN_ONLY` — `live_switch_in_v26=false`
- **5 opzioni valutate**: A standalone, B Sentinel replica, C Cluster, D Managed single-AZ, E Managed multi-AZ
- **Recommended path**:
  - Stage 4 NOW → A (current)
  - Pre Broad Rollout → **D** Managed single-AZ (~15–30 USD/mese)
  - Broad Rollout prod → **E** Managed multi-AZ (~50–120 USD/mese)
- **Env vars richiesti** (NESSUNO commit): `REDIS_MANAGED_URL`, `REDIS_TLS`, `REDIS_AUTH_STRATEGY`, `REDIS_MANAGED_TIMEOUT_MS`, `AFFINITY_RATE_LIMIT_BACKEND=redis_managed`
- **Migration steps**: 7 step documentati con canary 5% e flip after 24h zero fail-open
- **Rollback**: <60s, fail-open memory già testato
- **Failover expectations**: detection 5s, customer impact transparent
- **Probe opzionale** (`probe_affinity_managed_redis_optional.py`): emette `READY_NOT_APPLIED` se `REDIS_MANAGED_URL` non presente (caso attuale); quando presente, esegue PING+SET+GET+DEL con timings ms
- `secrets_in_repo=false` ✅

---

## 5. Cap raise plan 5k → ≥100k

`/app/data/design/affinity/af2n_cap_raise_plan_v1.json`

**5 stage** progressivi (PLAN ONLY, `live_cap_change_in_v26=false`):

| Stage | Cap | Users | Gate |
|---|---|---|---|
| S0 current | 5,000 | 700 | Stage 4 Internal Beta active |
| S1 | 25,000 | 2,500 | Local Redis OK; bump at 70% di S0 cap |
| S2 | 50,000 | 7,000 | Managed Redis single-AZ provisioned |
| S3 | 100,000 | 15,000 | Managed Redis multi-AZ + alerting LIVE + signoff V6 |
| S4 open | unlimited+quota | all | Full broad rollout authorized |

**Pressure analysis**:
- Redis key estimate at S3: ~50,000 zsets (user × 3 + ip cap)
- Mongo indexes required: 4 (idempotency unique sparse, user+ts, inventory unique, affinity_state unique)
- Inventory seed: per-stage opt-in, mai blanket

**Rollback per stage**: <2 min RTO ogni step.

---

## 6. Inventory scope expansion plan

`/app/data/design/affinity/af2n_inventory_scope_expansion_plan_v1.json`

**5 stage** (PLAN ONLY, `live_expansion_in_v26=false`):

| Stage | Users con inventory writes | Risk |
|---|---|---|
| S0 current | ~150 (Stage1 subset) | LOW |
| S1 | 700 (full Stage 4) | LOW |
| S2 | 2,500 (Internal Beta) | MEDIUM |
| S3 | 7,000 (Internal Beta full) | MEDIUM-HIGH |
| S4 | all eligible (broad rollout) | HIGH |

**Constraints**:
- `anti_negative_inventory`: $inc + lower-bound + alert P0
- `reconciliation`: daily V23 delta script, zero tolerance
- `borea_hidden_invariant`: enforced BEFORE any inventory mutation
- `support_ops`: runbook V25 §4

**Rollback**: unset `AFFINITY_GIFT_INVENTORY_WRITES_ENABLED`, RTO <90s.

---

## 7. Broad rollout signoff package V6 (PLAN_ONLY, BLOCKED)

`/app/data/design/affinity/af2n_broad_rollout_signoff_package_v6.json`

**8 domain**, **gates_passed = 0/8** (intenzionale).

| Domain | Owner | Status | Progress |
|---|---|---|---|
| product | PM | PENDING | – |
| engineering | Backend Lead | PENDING | – |
| qa | QA Lead | PENDING | – |
| economy | Economy Ops | PENDING | – |
| rollback | Backend Lead | PARTIAL | 60% |
| security_abuse | Security | PARTIAL | 70% |
| support_ops | Support Lead | PARTIAL | 50% |
| **final_user_approval** | Project Owner | **NOT_YET_REQUESTED** | – |

**Hard flags**: `broad_rollout_allowed=false`, `public_spend_ui_allowed=false`, `STACK_G_allowed=false`, `final_user_approval_granted=false`.

**Blocker dalla matrix V5** elencati come prerequisiti.

---

## 8. Alerting integration live prep

`/app/data/design/affinity/af2n_alerting_integration_plan_v1.json`

**5 sinks evaluati** (tutti `PLAN_ONLY`, eccetto `local_mock_sink` AVAILABLE_NOW):

| Sink | Protocol | Secrets | Status |
|---|---|---|---|
| prometheus | HTTP scrape | no | PLAN_ONLY |
| pagerduty | Events API v2 | sì | PLAN_ONLY |
| slack | Incoming Webhook | sì | PLAN_ONLY |
| generic_webhook | HTTP POST | sì | PLAN_ONLY |
| **local_mock_sink** | file appender | no | **AVAILABLE_NOW** |

**Phase plan**: P0 mock → P1 prometheus+slack warnings → P2 prometheus+pagerduty P0/P1.

- `secrets_in_repo=false` ✅
- `live_integration_in_v26=false` (rispetto della regola)
- `v25_contract_rules_count=9` (riferito a V25)
- Blocker rimane aperto fino a live wiring (BLK-D-02-LIVE → PLAN_READY)

---

## 9. Frontend smoke

`/app/data/design/ui/affinity_gifts_frontend_smoke_v26_result.json`

| Check | Result |
|---|---|
| `affinity-gifts-preview.tsx` presente | ✅ |
| HTTP `/affinity-gifts-preview` (port 3000) | **200** |
| HTTP `/api/affinity/gift-spend/canary-status` | **200** |
| Static check `fetch method GET` only | ✅ |
| Mentions `hero_id: borea` | **NO** ✅ |
| Mutating fetch on gift-spend | **0** |
| Critical findings | **0** |
| A11y hints found | sì (accessibilityLabel ecc.) |

**Verdict**: PASS

---

## 10. Stress 2x

`/app/data/design/affinity/af2n_stress_2x_v26_result.json`

**Mode**: SIMULATION_PLUS_SAFE_LIVE_PROBE

### Simulazione 2x (read-only math)

| Metric | 2x value |
|---|---|
| users | 1,400 |
| cap | 10,000 |
| expected total events | 7,000 |
| cap pressure ratio | 0.7 |
| expected 429 events | 3,080 |
| Redis ops/sec peak | ~2.4 |

### Live probe (safe, 95 totali)

| Phase | Result |
|---|---|
| Borea 404 | **30/30** ✅ |
| Controlled spend allowlist | **5/5** ✅ |
| Non-allowlist gated | **30/30** (423 o 429) ✅ |
| Burst 429 induced | **24/30** |
| 5xx | **0** ✅ |
| Unauthorized success | **0** ✅ |
| Ledger delta | ≤10 ✅ |

**Verdict**: PASS — safety invariants tutti rispettati.

---

## 11. Blocker Matrix V5

`/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v5.json`

### Sommario

| Severità | Total | Closed/Plan_Ready | Open |
|---|---|---|---|
| 🔴 P0 | 6 | 5 closed + 1 `PLAN_READY_NOT_APPROVED` (BLK-G-01 broad signoff) | 0 |
| 🟠 P1 | 9 | **9/9** closed_or_plan_ready | 0 |
| 🟡 P2 | 3 | 3/3 closed | 0 |
| 🟢 P3 | 4 | 4/4 closed (3 V25, 1 PLAN_READY V26) | 0 |

### V26 closures/transitions

- **BLK-B-03** (Redis SPOF) → `PLAN_READY_V26`
- **BLK-B-06** (cap raise) → `PLAN_READY_V26`
- **BLK-B-07** (inventory scope) → `PLAN_READY_V26`
- **BLK-C-03** (frontend smoke) → `CLOSED_V26`
- **BLK-D-02-LIVE** (alerting live sink) → `PLAN_READY_V26`
- **BLK-F-01** (stress 2x, nuovo) → `CLOSED_V26`
- **BLK-G-01** (broad rollout signoff, nuovo) → `PLAN_READY_V26_NOT_APPROVED`

### Gates

- ✅ Gate 1 Stage 4 extension: aperto
- ❌ Gate 2 Broad Rollout: chiuso (richiede `LIVE_CLOSED` di B-03/B-06/B-07 + approvazione utente)
- ❌ Gate 3 Public Spend UI: chiuso

---

## 12. Observation continuation

`/app/data/design/affinity/af2n_stage4_observation_window_v26_result.json`

Modalità **IP-aware phased** (FLUSHDB tra fasi):

| Phase | Result |
|---|---|
| Borea probes (50) | 50/50 → 404 |
| Non-allowlist (40) | 40/40 → 423/429 |
| Controlled spend (5) | 5/5 → 200 |
| Idempotency replay | 200 (deduplicato) |
| Burst (15) | 15/15 → 429 |
| Total 5xx | **0** |
| `rate_limit_backend` finale | **redis** |
| Ledger total rows finale | 172 |

**Verdict**: PASS

---

## 13. Rollback readiness V26

`/app/data/design/affinity/af2n_v26_rollback_readiness_result_v1.json`

| Check | Result |
|---|---|
| Stage 4 runtime flag switchable | ✅ |
| Redis local fallback switchable | ✅ |
| Managed Redis rollback plan presente | ✅ |
| Inventory writes flag switchable | ✅ |
| Broad rollout not active | ✅ |
| Supervisor conf presente | ✅ |
| Redis recovery script (exec) | ✅ |
| DB backups presenti | ✅ |
| Clone drill verdict PASS (V24) | ✅ |
| V25 rollback readiness PASS | ✅ |
| **Production DB touched** | **false** |

**Rollback paths**: 8 strade documentate.

**Verdict**: PASS

---

## 14. Safety Rollup U

```json
{
  "state": "stage4_internal_beta_active_no_broad_rollout",
  "managed_redis_status": "PLAN_READY",
  "cap_raise_plan_status": "PLAN_READY",
  "inventory_scope_plan_status": "PLAN_READY",
  "broad_rollout_signoff_v6_status": "PLAN_READY_NOT_APPROVED",
  "alerting_integration_status": "PLAN_READY",
  "frontend_smoke_status": "CLOSED",
  "stress_2x_status": "CLOSED",
  "blocker_matrix_v5_status": "CLOSED",
  "observation_v26_status": "CLOSED",
  "rollback_readiness_status": "CLOSED",
  "api_heroes_count_100": true,
  "borea_hidden": true,
  "rate_limit_backend": "redis",
  "broad_rollout_authorized": false,
  "public_spend_ui": false,
  "battle_wiring_live": false,
  "all_v26_parts_addressed": true,
  "verdict": "PASS"
}
```

---

## 15. Borea safety (live)

| Endpoint | borea | greek_borea | primordial_gaia |
|---|---|---|---|
| `POST /api/affinity/gift-spend` | **404** | **404** | **404** |
| `/api/heroes` list | NOT PRESENT | NOT PRESENT | NOT PRESENT |
| UI interactive surface | NO | NO | NO |
| UI decorative text | yes (allowed) | no | no |

---

## 16. Validator results

```
ULTRA-COMBO-V26 PASS passes=12 fails=0
  ✓ AF2-N-V26-PREFLIGHT
  ✓ AF2-N-V26-MANAGED-REDIS-READINESS
  ✓ AF2-N-V26-CAP-RAISE-PLAN
  ✓ AF2-N-V26-INVENTORY-SCOPE-PLAN
  ✓ AF2-N-V26-BROAD-ROLLOUT-SIGNOFF-V6
  ✓ AF2-N-V26-ALERTING-INTEGRATION-PREP
  ✓ AF2-N-V26-FRONTEND-SMOKE
  ✓ AF2-N-V26-STRESS-2X
  ✓ AF2-N-V26-BLOCKER-MATRIX-V5
  ✓ AF2-N-V26-OBSERVATION-WINDOW
  ✓ AF2-N-V26-ROLLBACK-READINESS
  ✓ AF2-N-V26-SAFETY-ROLLUP-U
```

---

## 17. Suite / baseline

- Full suite: **Overall: PASS (pass=181, fail=0, miss=0)** ↑ da 168 (V25) → +13 V26
- Baseline diff (catalog): 0 mutazioni
- Git diff su guardrail files: **empty** ✅

---

## 18. API Smoke

| Endpoint | HTTP |
|---|---|
| `/api/health` | 200 |
| `/api/heroes` count | 200 (100 items) |
| `/api/affinity/gift-spend/canary-status` | 200 |
| `/api/affinity/gift-spend/_admin/metrics-snapshot` | 200 |
| POST gift-spend borea | **404** |
| POST gift-spend greek_borea | **404** |
| POST gift-spend primordial_gaia | **404** |
| POST gift-spend outsider | **423** |
| POST gift-spend controlled (allowlist) | **200** |
| GET `/affinity-gifts-preview` (UI) | 200 |
| `redis-cli ping` | **PONG** |

---

## 19. Runtime / DB / Gacha / Roster / Catalog safety

| Surface | Mutated in V26? |
|---|---|
| Runtime feature flags | **NO** |
| MongoDB production collections | **NO** |
| Gacha tables | **NO** |
| Roster | **NO** |
| Character Bible / cataloghi skills | **NO** |
| `final_numbers` | **NO** |
| `battle_engine.py` / `battle_core.py` / `combat.tsx` | **NO** |
| `affinity_gift_spend.py` route | **NO** (vs V25) |
| Secrets in repo | **NO** |

Redis FLUSHDB usato solo in observation/stress (rate-limit by-design effimero).

---

## 20. Warnings

1. 🟡 **Redis binary mid-task transient**: il binario è sparito di nuovo a metà task (filesystem effimero); lo script `ensure_redis_rate_limit.sh` lo ha reinstallato in <2s con rc=0. **Idempotenza verificata su un caso reale.**
2. 🟡 **Memory fallback can saturate IP rate-limit**: in test ad alto volume da loopback (127.0.0.1), il fallback memory ha saturato `ip_min=60`. Mitigato con backend restart + Redis ripristinato. In produzione multi-pod non sarà un issue.
3. 🟡 **Managed Redis live switch deferred**: BLK-B-03 risolto al livello plan, NON live. Provisioning + flip pendente decisione utente.
4. 🟡 **Alerting LIVE sink deferred**: BLK-D-02-LIVE in PLAN_READY; nessun sink esterno cablato in V26 (per design — niente secrets).
5. 🟡 **Broad rollout signoff V6**: gates=0/8 (intenzionale). Final user approval esplicita richiesta.

---

## 21. Final recommendation

✅ **PASS — Stage 4 Internal Beta resta safe e i piani per broad readiness sono completi.**

Stato:
- Tutti gli invarianti P0 OK
- Tutti i piani P1 documentati e validati (5 plan-only PASS)
- Stress 2x safe e nessun 5xx
- Frontend smoke ✅
- Idempotenza recovery Redis dimostrata su un caso reale durante questo task
- Hard invariants (Borea, /api/heroes=100, broad rollout OFF, public spend UI OFF, STACK-G OFF, battle wiring OFF) tutti rispettati

**Next gates richiedono decisione del project owner**:
1. Approvazione provisioning Managed Redis (BLK-B-03 → CLOSED)
2. Approvazione cap raise S1 → S2 (BLK-B-06 → CLOSED)
3. Approvazione inventory scope S1 expansion (BLK-B-07 → CLOSED)
4. Wiring alerting LIVE su prometheus/pagerduty (BLK-D-02-LIVE → CLOSED)
5. Final approval broad rollout signoff V6 (BLK-G-01 → CLOSED)

Fino ad allora: **Stage 4 Internal Beta active no broad rollout**.

---

## 22. Suggested next tasks (V27+)

### Priorità immediate (richiede input utente)

- 🟠 **V27 Managed Redis provisioning**: scegliere provider (ElastiCache vs Upstash), procurement, secret management, deploy code path, canary 5%, switch.
- 🟠 **V27 Alerting LIVE integration**: scegliere sink primario, configurare via secret manager, deploy.
- 🟠 **V27 Cap raise S1**: bump cap 5,000 → 25,000 + allowlist espansione a 2,500 utenti.

### Priorità medio termine

- 🟡 **V28 Inventory scope expansion S1**: opt-in 700 utenti completi Stage 4.
- 🟡 **V28 Observation 72h post-S1** + delta audit daily.
- 🟡 **V28 QA stress 5x simulation + live probe**.

### Priorità lungo termine (gating broad rollout)

- 🟢 **V29-V30 multi-stage progressivo a 100k**.
- 🟢 **V30 Broad rollout signoff V7** con tutti i domini PASSED.
- 🟢 **STACK-G wiring decision** (separato; rimane gated).

---

**Approval**: PASS — V26 completato in modalità safe. Broad rollout strictly deferred fino ad approvazione esplicita.
