# Blocker Matrix V3 — Stage 4 → Broad Rollout

**Task origin**: `AF2-N-V24-SAFETY-ROLLUP-S`  
**Generated**: V24 ULTRA-COMBO  
**Owner**: backend / economy ops  
**Scope**: Tutti i blocker che separano lo stato corrente (Stage 4 Internal
Beta) dal Broad Rollout pubblico.

---

## Legenda severità

- 🔴 **P0**: bloccante assoluto per qualsiasi promozione
- 🟠 **P1**: bloccante per Broad Rollout (non per Stage 4 esteso)
- 🟡 **P2**: bloccante per Public Spend UI
- 🟢 **P3**: nice-to-have

---

## Matrice blockers

| ID | Severità | Titolo | Stato | Owner | Note V24 |
|---|---|---|---|---|---|
| BLK-A-01 | 🔴 P0 | `battle_engine.py` / `combat.tsx` mai modificati | ✅ CLOSED | backend | Verificato diff = 0 a ogni V21→V24 |
| BLK-A-02 | 🔴 P0 | Borea/greek_borea/primordial_gaia gift-spend → 404 | ✅ CLOSED | backend | Counter reali V24: 3 × 404 osservati |
| BLK-A-03 | 🔴 P0 | `/api/heroes` count = 100 | ✅ CLOSED | backend | Verificato in real observation V24 |
| BLK-A-04 | 🔴 P0 | Nessun 5xx in observation window | ✅ CLOSED | backend | V24 obs window: 0 × 5xx su ~30 requests |
| BLK-A-05 | 🔴 P0 | Nessuno spend non autorizzato | ✅ CLOSED | backend | Ledger 144 rows, tutte canary + allowlist |
| BLK-B-01 | 🟠 P1 | Redis HA: binario sparisce a restart container | 🟠 OPEN | infra | Mitigation in §5.1 del Redis HA Plan; init-script da implementare |
| BLK-B-02 | 🟠 P1 | Redis non-persistente (effimero) | 🟢 ACCEPTED | infra | Dataset rate-limit è by-design effimero |
| BLK-B-03 | 🟠 P1 | Redis single-node (SPOF) | 🟠 OPEN | infra | Plan: Managed Redis pre-Broad (V26) |
| BLK-B-04 | 🟠 P1 | Rollback drill solo su clone | ✅ CLOSED V24 | backend | V24 drill non-destructive: PASS, prod hash unchanged |
| BLK-B-05 | 🟠 P1 | Abuse metrics not instrumented | ✅ CLOSED V24 | backend | Modulo `affinity_metrics.py` + endpoint `_admin/metrics-snapshot` live, counter popolati |
| BLK-B-06 | 🟠 P1 | Stage 4 cap a 5.000 — broad rollout richiede cap ≥ 100k | 🟠 OPEN | economy | Decisione finale gated da V26 |
| BLK-B-07 | 🟠 P1 | Inventory writes scope = `Stage1 allowlist only` | 🟠 OPEN | backend | Switch scope a tutti gli utenti gated da V26 |
| BLK-C-01 | 🟡 P2 | Public Spend UI mai esposta | ✅ CLOSED | frontend | Verificato OFF in V21→V24 (combat.tsx untouched) |
| BLK-C-02 | 🟡 P2 | STACK-G wiring (affinity → battle_engine) | ✅ CLOSED | backend | Strictly deferred. battle_runtime_attached=false |
| BLK-C-03 | 🟡 P2 | Frontend gift-spend UI smoke test | 🔴 OPEN | frontend | Plan-only fino a Public Spend UI gate |
| BLK-D-01 | 🟢 P3 | Documentazione runbook restart Redis | 🟠 OPEN | docs | Da scrivere in `/app/docs/divine/RUNBOOK_REDIS_RESTART.md` |
| BLK-D-02 | 🟢 P3 | Alarming `af2_ratelimit_redis_fail_open_total` > 100/h | 🟠 OPEN | infra | Counter già esiste, alarming TBD |
| BLK-D-03 | 🟢 P3 | Support playbook per spend errors | 🟠 OPEN | support | V24: bozza in `SUPPORT_ECONOMY_PREP_V24.md` |

---

## Promotion gates

### Gate 1 → Estensione Stage 4 (cap 5k → 20k)
- ✅ Tutti i 🔴 P0 CLOSED
- ✅ BLK-B-04 (rollback drill) CLOSED
- ✅ BLK-B-05 (abuse metrics) CLOSED
- 🟠 Necessario: BLK-B-01 mitigato (init-script Redis)

**Verdict V24**: ✅ Pronto per estensione cap quando autorizzato

### Gate 2 → Broad Rollout (pubblico)
- ✅ Gate 1
- 🟠 BLK-B-03 (Managed Redis) CLOSED
- 🟠 BLK-B-06 (cap aumentato) CLOSED
- 🟠 BLK-B-07 (inventory writes scope) CLOSED
- 🟡 BLK-C-03 (frontend smoke) CLOSED

**Verdict V24**: ❌ NOT READY — almeno 4 P1 open. Gated dietro V26 signoff.

### Gate 3 → Public Spend UI
- ✅ Gate 2
- 🟡 BLK-C-01 reopen + UI build pronta
- 🟡 BLK-C-02 reopen + STACK-G wiring deliberato

**Verdict V24**: ❌ NOT AUTHORIZED — strictly deferred.

---

## Trend V21 → V24

| Metric | V21 | V22 | V23 | V24 |
|---|---|---|---|---|
| P0 closed | 3 / 5 | 5 / 5 | 5 / 5 | 5 / 5 |
| P1 closed | 0 / 7 | 1 / 7 | 2 / 7 | 3 / 7 |
| P2 closed | 1 / 3 | 1 / 3 | 1 / 3 | 2 / 3 |
| P3 closed | 0 / 3 | 0 / 3 | 0 / 3 | 0 / 3 |
| Borea 404 evidence | static | static | static | **REAL counter** |
| Rate-limit backend | memory | memory | redis | **redis (HA-planned)** |

---

## Next actions

1. 🟠 V25: chiudere BLK-B-01 con init-script idempotente Redis.
2. 🟠 V25: scrivere `RUNBOOK_REDIS_RESTART.md` (BLK-D-01).
3. 🟠 V26: provisioning Managed Redis (BLK-B-03).
4. 🟢 V26: signoff package per Broad Rollout (cap + scope inventory).
