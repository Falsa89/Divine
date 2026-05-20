# ULTRA-COMBO V28 — INVENTORY SCOPE S1 EXPANSION + ALLOWLIST 700→2500 GATED + STRESS 5X + OPTIONAL MANAGED REDIS / ALERTING PROBE + SAFETY-ROLLUP-W

**Task origin**: `AF2-N-V28`
**Status**: ✅ **PASS** (11/11 validator V28 + suite globale 205/205)
**Date (UTC)**: 2026-05-20
**Stage**: Stage 4 Internal Beta ACTIVE — **NO broad rollout, NO public UI**

---

## 1. Executive Summary

V28 espande lo scope dell'inventory-live in modo strettamente gated:

| Dimensione | Pre-V28 | Post-V28 | Cap hardcoded |
|------------|---------|----------|---------------|
| Allowlist canary | 700 utenti (`stage1..4_qa_*`) | **2500 utenti** (`+ 1800 stage5_qa_*`) | (env) |
| Cap ledger | 25 000 | **25 000** (invariato) | 25 000 (code) |
| Inventory writes | live (stage1) | live (stage1, marker `V28_SCOPE_S1`) | n/a |
| Rate-limit backend | redis | redis | redis |
| Heroes pubblici | 100 | **100** (invariato) | 100 |

**Invarianti P0 confermati**:
- ✅ `/api/heroes` = 100 (no leak Borea)
- ✅ `borea` / `greek_borea` / `primordial_gaia` → HTTP 404 (50/50 probe)
- ✅ Cap = 25 000 (immutato)
- ✅ Allowlist ≤ 2 500 (esattamente)
- ✅ Broad rollout = **OFF**
- ✅ Public spend/give UI = **OFF**
- ✅ STACK-G battle wiring = **OFF**
- ✅ `battle_engine.py` / `battle_core.py` / `combat.tsx` → **no-diff** (git stat vuoto)
- ✅ Nessun unauthorized spend, nessun 5xx in tutta la finestra V28

---

## 2. Parts & Verdicts

| # | Part | Script | Verdict | Note |
|---|------|--------|---------|------|
| A | Preflight V28 | `validate_af2n_v28_preflight.py` | ✅ PASS | gate generale |
| B | Inventory Scope S1 APPLY (700→2500) | `validate_af2n_inventory_scope_s1_v28.py` | ✅ PASS | status=`APPLIED`, marker `V28_SCOPE_S1` |
| B.1 | Schema-fix idempotente seed V28 | `fix_af2n_v28_scope_s1_inventory_schema.py` | ✅ PASS | migrati 1800 doc da nested→flat |
| C | Post-apply Observation (phased, IP-aware) | `validate_af2n_scope_s1_observation_v28.py` | ✅ PASS | borea 50/50→404, new_ctrl 10/10→200, burst 14/20→429, 5xx=0 |
| D | Stress 5x (sim 17 500 ev/day + safe live probe) | `validate_af2n_stress_5x_v28.py` | ✅ PASS | ctrl 10/10, na 60/60 blocked, burst 44/50→429, replay 5/5, 5xx=0 |
| E | Inventory Delta Audit (read-only) | `validate_affinity_inventory_delta_consistency_v28.py` | ✅ PASS | neg=0, borea_ledger=0, unauth=0, dup=0, marker 1800/1800 |
| F | Managed Redis Probe (gated) | `validate_managed_redis_v28_probe.py` | ✅ PASS | `READY_NOT_APPLIED` (env `REDIS_MANAGED_URL` non fornito) |
| G | Alerting Live Probe (gated) | `validate_alerting_live_v28_probe.py` | ✅ PASS | `LOCAL_MOCK` (env `ALERT_WEBHOOK_URL` non fornito) |
| H | **Blocker Matrix V7** | `validate_af2n_broad_rollout_blocker_matrix_v7.py` | ✅ PASS | P0 open=0, transitions V28 registrate |
| I | UI Safety (no public mutation surface) | `audit_affinity_gifts_public_preview_v28_safety.py` | ✅ PASS | 125 file scansionati, critical=0 |
| J | Rollback Readiness V28 | `validate_af2n_v28_rollback_readiness.py` | ✅ PASS | tutti 14 check OK |
| K | **Safety Rollup W** | `validate_collection_affinity_runtime_activation_rollup_v23.py` | ✅ PASS | guardrails clean, invarianti tutti rispettati |
| L | Composite ULTRA-COMBO V28 | `validate_ultra_combo_v28_inventory_scope_stress5x.py` | ✅ PASS | 11/11 |
| ✓ | Suite globale + baseline diff | `run_hero_skill_kit_validator_suite.py` | ✅ PASS | **205/205** (pass=205, fail=0, miss=0) |

---

## 3. Blocker Matrix V7 — sintesi transizioni V28

| ID | Severity | Title | Pre-V28 | Post-V28 |
|----|----------|-------|---------|----------|
| BLK-B-07 | P1 | Inventory scope S1 expansion | OPEN | **LIVE_CLOSED_V28** (`APPLIED`) |
| BLK-F-03 | P1 | Stress 5x | OPEN | **CLOSED_V28** (PASS) |
| BLK-B-03 | P1 | Redis SPOF (Managed Redis switch) | READY_NOT_APPLIED_V27 | **READY_NOT_APPLIED_V28** (env mancante, atteso) |
| BLK-D-02-LIVE | P3 | Alerting live sink | MOCK_CLOSED_V27 | **MOCK_CLOSED_V28** (LOCAL_MOCK, env mancante, atteso) |
| BLK-G-01 | P0 | Broad rollout signoff V6 final | PLAN_READY_NOT_APPROVED | **PLAN_READY_NOT_APPROVED** (immutato — non autorizzato) |

P0 open = **0** ✅ — broad rollout authorized = **false** (gated).

---

## 4. Bug fix in-flight (V28 B.1)

Lo script `apply_af2n_inventory_scope_s1_v28.py` aveva seedato gli 1800 nuovi
`stage5_qa_*` con schema annidato `{user_id, balances: {gift_test_001: 50}}`
mentre la route runtime legge lo schema flat
`{user_id, gift_id, quantity}`. Risultato pre-fix: nuovi utenti ricevevano
HTTP 412 (`inventory_insufficient`).

**Fix idempotente**: `fix_af2n_v28_scope_s1_inventory_schema.py` ha migrato
1800 doc nested → flat preservando il marker `V28_SCOPE_S1` per il rollback.

**Verifica post-fix**:
- `stage5_qa_0001` con `gift_test_001`=50 → smoke spend → HTTP 200, `applied_inventory_live`
- Observation 10/10 controlled fresh → HTTP 200
- Delta Audit: marker_inv = 1800, no nested residui

**Ambito DB-write**: esclusivamente record con marker `meta.v28_scope_s1=true`.
Nessun dato di catalogo, gacha, roster, eroi, combat è stato toccato.

---

## 5. Managed Redis & Alerting — task futuri V29+

Le probe sono gated su variabili ambiente del container:

| Probe | Env var richiesta | Stato attuale V28 | Verdict |
|-------|-------------------|-------------------|---------|
| Managed Redis | `REDIS_MANAGED_URL` | non fornita | `READY_NOT_APPLIED` → PASS |
| Alerting live | `ALERT_WEBHOOK_URL` o `PROMETHEUS_PUSHGATEWAY` | non fornita | `LOCAL_MOCK` (sink-log) → PASS |

Nessun comportamento runtime cambia finché le env non vengono forniti.
Il client locale Redis (`redis://127.0.0.1:6379/0`) rimane il backend
rate-limit ufficiale, supervisionato + auto-recuperato da
`/app/ops/ensure_redis_rate_limit.sh`.

---

## 6. Safety Rollup W (snapshot live)

```json
{
  "internal_beta_scope_state": "EXPANDED_TO_2500_V28",
  "allowlist_count": 2500,
  "canary_ledger_cap": 25000,
  "api_heroes_count_100": true,
  "borea_hidden": true,
  "rate_limit_backend": "redis",
  "broad_rollout_authorized": false,
  "public_spend_ui": false,
  "battle_wiring_live": false,
  "guardrails_clean": {
    "backend/battle_engine.py": true,
    "backend/battle_core.py": true,
    "frontend/app/combat.tsx": true
  }
}
```

---

## 7. Rollback paths (drill-ready)

1. **Scope S1 (utenti+conf)** → `python3 /app/backend/scripts/rollback_af2n_inventory_scope_s1_v28.py`
2. **Cap S1 (5k→25k)** → `python3 /app/backend/scripts/rollback_af2n_cap_raise_s1_v27.py`
3. **Local Redis recovery** → `bash /app/ops/ensure_redis_rate_limit.sh`
4. **Managed Redis switch** → `python3 /app/backend/scripts/rollback_managed_redis_switch_v27.py`
5. **Stage4 runtime disable** → unset `AFFINITY_GIFT_RUNTIME_ENABLED` + restart
6. **Inventory writes disable** → unset `AFFINITY_GIFT_INVENTORY_WRITES_ENABLED` + restart
7. **Full AF2-N rollback** → unset tutte le env AF2-N* + restart

Backup `backend.conf` con timestamp UTC:
`/app/backend/backups/v28_scope_s1/backend.conf.20260520T201358Z.bak`.

---

## 8. Acceptance Gates V28

- [x] Tutti i validator V28 PASS (11/11)
- [x] Suite globale PASS (205/205, baseline diff incluso)
- [x] Invarianti P0 rispettati
- [x] Rollback readiness PASS
- [x] UI safety PASS (no public mutation surface)
- [x] Nessun unauthorized spend
- [x] Nessun 5xx in finestra V28
- [x] Broad rollout NON autorizzato
- [x] Public spend UI NON attivata
- [x] STACK-G / battle wiring NON collegati
- [x] `battle_engine.py` / `battle_core.py` / `combat.tsx` invariati (git no-diff)

**Verdict finale**: **ULTRA-COMBO V28 = PASS**.

---

## 9. Pending future tasks (V29+)

- 🟡 V29 Managed Redis switch live (in attesa di `REDIS_MANAGED_URL`)
- 🟡 V29 Alerting sink live (in attesa di `ALERT_WEBHOOK_URL` o `PROMETHEUS_PUSHGATEWAY`)
- 🔴 Broad rollout final signoff V6 → richiede approvazione esplicita
- 🔴 Public spend UI activation → gated, NON autorizzato
- 🔴 STACK-G full wiring (battle_engine ↔ affinity stats) → deferito per safety

---

*Documento generato automaticamente da V28 — non modificare manualmente.*
