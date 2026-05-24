# 121D — V7 BLOCK_D — AF2N_OBSERVABILITY_DASHBOARD_TEMPLATE

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V7`  
**Block**: D  
**Mode**: `design_doc_only`  
**Verdict**: 🟢 `BLOCK_D_AF2N_OBSERVABILITY_DASHBOARD_TEMPLATE_READY`  
**Timestamp**: 20260524T134500Z  
**Rollback**: N/A (doc-only, nessun runtime/daemon/endpoint/DB write)

---

## 1. Scopo

Formalizzare il **template del dashboard di observability AF2-N** (`AF2N_V8_CANARY_HEALTH_DASHBOARD_V1`) come **design doc**, pronto per essere renderizzato in JSON/YAML (Prometheus + Grafana) da un futuro implementation pack senza modifiche runtime in V7.

Upstream:
- V5 BLOCK_B pipeline metrics (`af2n_observability_metrics_pipeline_v1.json`)
- V6 BLOCK_B snapshot export (`af2n_metrics_snapshot_export_v1.json` + `af2n_metrics_snapshot.jsonl`)

## 2. Dashboard: 8 pannelli canonici

| Panel | Titolo | Metric / Viz | Threshold / Alert | V8 signoff gating |
|---|---|---|---|---|
| **P1** | Canary Completion Ratio | `af2n_canary_completion_ratio` — single_stat + sparkline | 🟢 ≥0.95 / 🟡 0.80–0.95 / 🔴 <0.80 | ✅ DBR_02 |
| **P2** | Ledger Write Failures by Reason | `af2n_ledger_write_failures_total` — stacked bar (label: reason) | failures > 5/hour | ✅ |
| **P3** | Rate-Limit Throttle by Endpoint | `af2n_rate_limit_throttle_total` — line chart (label: endpoint) | — | — |
| **P4** | Redis Crash Events / Mitigation Invocations | `af2n_redis_crash_events_total` + `af2n_redis_mitigation_invocations_total` — counter dual | crashes_today > 0 → runbook V4 BLOCK_E | — |
| **P5** | Inventory Writes Blocked (FROZEN) | `af2n_inventory_writes_blocked_frozen_total` — counter | should == attempted while FROZEN | ✅ |
| **P6** | Affinity Gain Delta vs Control | `af2n_affinity_gain_delta_vs_control` — line chart | 🟢 -0.05 / +0.10 — 🔴 >+0.25 o <-0.10 | ✅ DBR_02 |
| **P7** | Gift Spend Volume Distribution (P50/P95/P99) | `af2n_gift_spend_volume_seconds` — histogram | — | — |
| **P8** | V21/V22/V23/V24 Rollback Test Execution Timestamps | timeline | — | — |

## 3. Alert rules (5)

| ID | Condition | Severity | Action |
|---|---|---|---|
| A1 | completion_ratio < 0.80 for 1h | high | page on-call |
| A2 | ledger_write_failures > 5/hour | medium | investigate Redis health + ledger collection state |
| A3 | redis_crash_events > 0/day | medium | apply `/app/ops/ensure_redis_rate_limit.sh` (V4 BLOCK_E runbook) |
| A4 | inventory_writes_blocked != attempted | critical | halt canary; investigate FROZEN bypass |
| A5 | affinity_gain_delta > 0.25 | high | halt canary; investigate AF2-N gift catalog |

## 4. V8 signoff gating

Pannelli **P1, P2, P5, P6** sono pre-requisiti per il signoff broad-rollout V8 (DBR_02). Devono essere live e popolati di metriche reali per ≥14 giorni prima di abilitare `stage1_1pct_allowlist`.

## 5. Export to implement

- **In V7**: ❌ nessun export (design-only)
- **Future**: implementation pack rendera' JSON/YAML compatibile con Prometheus + Grafana, recuperando metriche dal pipeline V5 BLOCK_B + snapshot V6 BLOCK_B.

## 6. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| Daemon aggiunto | ❌ No |
| Runtime endpoint nuovo | ❌ No |
| AF2-N runtime mutation | ❌ No |
| DB write | ❌ No |
| Polling / background loop | ❌ No |

## 7. Cosa sblocca

- Roadmap V8: panel set canonico riferito da `AF2-N-V29-BROAD-ROLLOUT-SIGNOFF` (gate `EV-OBSERVABILITY-DASHBOARDS` → da `PENDING` a `PROVIDED` quando implementato).
- Pack implementazione dashboard (futuro): traduzione 1-to-1 di questo template.
