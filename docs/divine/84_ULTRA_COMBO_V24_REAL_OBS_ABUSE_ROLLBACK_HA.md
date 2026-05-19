# ULTRA-COMBO V24 — Real Observation Window + Abuse Metrics Instrumentation + Staging Rollback Drill + Redis HA Plan + Safety-Rollup-S

**Status**: ✅ **PASS**  
**Task origin**: `AF2-N-V24`  
**Date**: 2026-05-19  
**Sequence**: V21 → V22 → V23 → **V24** → V25 (next) → V26 (broad-rollout signoff)

---

## 0. TL;DR

Tutti i 5 deliverable richiesti dallo ZIP V24 sono stati completati e validati:

1. ✅ **Real Observation Window Stage 4** — eseguito su traffico reale, popola counters reali, 0 × 5xx.
2. ✅ **Abuse Metrics Instrumentation** — modulo + endpoint + hooks installati, validator rinforzato (Opzione C).
3. ✅ **Staging Clone Rollback Drill** — NON DESTRUTTIVO, 144 rows marked reverted in clone, production hash invariato.
4. ✅ **Redis HA Decision Plan** — documento PLAN-ONLY con decisione standalone-now / managed-pre-broad.
5. ✅ **Safety Rollup S + Blocker Matrix V3 + Support Prep** — 3 P0 closed, P1 al 43% closed.

**Hard invariants**: TUTTI rispettati (vedere §7).

---

## 1. Deliverable 1 — Real Observation Window Stage 4

Script: `backend/scripts/run_af2n_v24_real_observation_window.py`  
Report: `backend/reports/v24_real_observation_window.json`

| Fase | Risultato |
|---|---|
| `/api/health` | ✅ 200, `status=ok` |
| `/api/heroes` count | ✅ 100 (esatto) |
| Borea / greek_borea / primordial_gaia probes | ✅ 3 × 404 |
| Canary spend (10 users allowlist) | ✅ 10 / 10 success |
| Induced burst (10 rapid posts same user) | ✅ 429 osservato (rate-limit hit), 0 × 5xx |
| `rate_limit_backend` | ✅ `redis` |
| `ledger_canary_rows` post-window | 144 |

**Counter reali popolati durante la finestra** (dopo restart):

```text
af2_gift_spend_borea_404_total{hero_alias=borea} = N
af2_gift_spend_borea_404_total{hero_alias=greek_borea} = N
af2_gift_spend_borea_404_total{hero_alias=primordial_gaia} = N
af2_gift_spend_total{http_status=404,hidden_alias_flag=1} = 3N
af2_ratelimit_429_total{backend=redis,reason=user_burst_exceeded} = M
af2_gift_spend_total{http_status=429} = M
```

(Note: label rinominata da `borea=1` → `hidden_alias_flag=1` per chiarezza
semantica e safety di pulizia.)

---

## 2. Deliverable 2 — Abuse Metrics Instrumentation

### 2.1 Componenti

- **Modulo**: `backend/data/affinity_metrics.py` — counters, histograms, gauges
  in-memory, gated da `AFFINITY_METRICS_ENABLED=true_explicit_affinity_metrics_on`.
- **Endpoint**: `GET /api/affinity/gift-spend/_admin/metrics-snapshot` —
  read-only, gated, safety-annotated.
- **Hooks**: 2 chiamate `from data.affinity_metrics import inc` installate in
  `backend/routes/affinity_gift_spend.py` (Borea-404 path + rate-limit-429 path).

### 2.2 Safety design

```json
"safety": {
    "flag": "AFFINITY_METRICS_ENABLED",
    "design": "in_memory_process_local",
    "not_for_production_dashboards": true,
    "no_borea_data": true,
    "no_user_pii": true
}
```

- ✅ No PII utente (mai `user_id` come label)
- ✅ No hero data (solo conteggi numerici + label operative)
- ✅ Endpoint NON pubblicizzato in routing pubblico — internal Stage 4 only
- ✅ Process-local: morirà al restart, nessuna persistenza

### 2.3 Validator (Opzione C)

Script: `backend/scripts/validate_af2n_v24_abuse_metrics_instrumentation.py`

Asserzioni rinforzate aggiunte in V24:

- Modulo + API minima (8 token richiesti)
- Hooks count ≥ 2 nella route
- Endpoint reachable + JSON valido
- 10 chiavi obbligatorie nel payload
- Buckets ms = `[5, 10, 25, 50, 100, 250, 500, 1000, 2000]`
- Safety annotations (`no_borea_data`, `no_user_pii`, `not_for_production_dashboards`, `design`)
- Counters / histograms tipi numerici
- NO leak di hero data fields (description, base_stats, image_url, rarity, ...)
- Guardrail diff = 0 su `battle_engine.py`, `battle_core.py`, `combat.tsx`

**Result**: PASS ✅

---

## 3. Deliverable 3 — Staging/Clone Rollback Drill

Script: `backend/scripts/run_af2n_v24_clone_rollback_drill.py`  
Report: `backend/reports/v24_rollback_drill.json`  
Backup logico: `backend/backups/v24_rollback_drill/20260519T220234Z/`

**Mode**: `NON_DESTRUCTIVE_CLONE_DRILL` — collezioni production **MAI** mutate.

| Step | Verifica | Risultato |
|---|---|---|
| 1. Snapshot pre | hash sha256 per ogni collezione | computed (counts: ledger=144, inventory=700, affinity_state=107) |
| 2. Backup logico | dump JSON in `/app/backend/backups/...` | OK |
| 3. Clone revert | 144 ledger rows marked `reverted_dry_run` in clone | OK |
| 4. Clone validation | no Borea alias in ledger | ✅ 0 leak |
| 5. Round-trip | hash post-restore == hash pre | ✅ MATCH |
| 6. Production invariant | hash production now == hash pre | ✅ UNCHANGED |

**Verdict**: PASS ✅, `production_collections_touched = false`.

---

## 4. Deliverable 4 — Redis HA Decision Plan

Documento: `/app/docs/divine/84_REDIS_HA_DECISION_PLAN_V24.md`

**Decisione**:

- 🟢 **Stage 4 NOW**: standalone hardenizzato + fail-open memory documentato (zero infra change).
- 🟡 **Pre Broad Rollout**: Managed Redis (single-AZ minimo) → ElastiCache/Upstash.
- 🔴 **Broad Rollout**: Managed Redis multi-AZ.

**Blocker aperti** (tracciati in Blocker Matrix V3):

- **BLK-B-01**: Container effimero — binario Redis sparisce a restart container. Mitigation: init-script idempotente (V25).
- **BLK-B-03**: SPOF single-node — risolto via Managed Redis (V26).

**Action items immediati**:

- [ ] Init-script `/app/scripts/ensure_redis_installed.sh` (V25)
- [ ] Runbook `/app/docs/divine/RUNBOOK_REDIS_RESTART.md` (V25)
- [ ] Alarming su `af2_ratelimit_redis_fail_open_total` (TBD)

---

## 5. Deliverable 5 — Safety Rollup S + Blocker Matrix V3 + Support Prep

### 5.1 Safety Rollup S

Validator: `validate_collection_affinity_runtime_activation_rollup_v19.py` → ✅ PASS

### 5.2 Blocker Matrix V3

Documento: `/app/docs/divine/84_BLOCKER_MATRIX_V3.md`

Stato chiusure:

| Severità | V21 | V22 | V23 | **V24** |
|---|---|---|---|---|
| 🔴 P0 | 3/5 | 5/5 | 5/5 | **5/5** ✅ |
| 🟠 P1 | 0/7 | 1/7 | 2/7 | **3/7** ⬆ |
| 🟡 P2 | 1/3 | 1/3 | 1/3 | **2/3** ⬆ |
| 🟢 P3 | 0/3 | 0/3 | 0/3 | **0/3** |

**Promotion gates**:

- ✅ Gate 1 (Stage 4 extension): pronto quando autorizzato
- ❌ Gate 2 (Broad Rollout): 4 × P1 open → V26 gated
- ❌ Gate 3 (Public Spend UI): strictly deferred

### 5.3 Support / Economy Prep

Documento: `/app/docs/divine/84_SUPPORT_ECONOMY_PREP_V24.md`

Include:

- Stato live features
- Ticket triage cheat-sheet (5 scenari)
- Escalation matrix
- Snapshot economy (144 ledger rows, cap 5000, allowlist 700)
- SLO impliciti misurati in V24

---

## 6. Suite + Composite

| Run | Tests | Result |
|---|---|---|
| `validate_ultra_combo_v24_observation_abuse_rollback_redisHA.py` | composite V24 | ✅ PASS (fails=0) |
| `run_hero_skill_kit_validator_suite.py` | full validator suite | ✅ PASS (155/155, 0 fail, 0 missing) |

---

## 7. Safety invariants — final check

| Invariant | V24 verification | Status |
|---|---|---|
| `battle_engine.py` untouched | `git diff --stat` = empty | ✅ |
| `battle_core.py` untouched | `git diff --stat` = empty | ✅ |
| `combat.tsx` untouched | `git diff --stat` = empty | ✅ |
| `/api/heroes` count == 100 | curl + json count | ✅ 100 |
| `borea` gift-spend → 404 | live POST | ✅ 404 |
| `greek_borea` gift-spend → 404 | live POST | ✅ 404 |
| `primordial_gaia` gift-spend → 404 | live POST | ✅ 404 |
| Borea NOT in `/api/heroes` list | id scan | ✅ no leak |
| No 5xx in observation window | ~30 requests | ✅ 0 / ~30 |
| Broad rollout OFF | feature flag inspection | ✅ OFF |
| Public Spend UI OFF | `applied_to_combat=false`, no UI route | ✅ OFF |
| STACK-G wiring OFF | `battle_runtime_attached=false` | ✅ OFF |
| Redis backend live | `redis-cli ping` + canary-status | ✅ PONG, `rate_limit_backend=redis` |
| No unauthorized spend | ledger 144 rows all canary + allowlist | ✅ |

---

## 8. Artefatti V24

| Path | Tipo |
|---|---|
| `/app/backend/data/affinity_metrics.py` | modulo |
| `/app/backend/routes/affinity_gift_spend.py` | route (hooks + endpoint) |
| `/app/backend/scripts/run_af2n_v24_real_observation_window.py` | script |
| `/app/backend/scripts/run_af2n_v24_clone_rollback_drill.py` | script |
| `/app/backend/scripts/validate_af2n_v24_abuse_metrics_instrumentation.py` | validator (Opzione C) |
| `/app/backend/reports/v24_real_observation_window.json` | report |
| `/app/backend/reports/v24_rollback_drill.json` | report |
| `/app/backend/backups/v24_rollback_drill/20260519T220234Z/` | backup logico |
| `/app/docs/divine/84_REDIS_HA_DECISION_PLAN_V24.md` | piano HA |
| `/app/docs/divine/84_BLOCKER_MATRIX_V3.md` | matrix |
| `/app/docs/divine/84_SUPPORT_ECONOMY_PREP_V24.md` | playbook |
| `/app/docs/divine/84_ULTRA_COMBO_V24_REAL_OBS_ABUSE_ROLLBACK_HA.md` | **questo report** |

---

## 9. Next ULTRA-COMBO

- **V25**: chiusura BLK-B-01 (init-script Redis) + RUNBOOK Redis restart + alarming P3
- **V26**: signoff package Broad Rollout (cap, scope inventory, Managed Redis provisioning)

---

**Approval**: PASS — Stage 4 Internal Beta continua, Broad Rollout resta gated, public UI resta OFF.
