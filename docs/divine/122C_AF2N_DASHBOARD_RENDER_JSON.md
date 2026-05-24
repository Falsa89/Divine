# 122C — V8 BLOCK_C — AF2N_DASHBOARD_RENDER_JSON

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V8`  
**Block**: C  
**Mode**: `design_export_json_only`  
**Verdict**: 🟢 `BLOCK_C_AF2N_DASHBOARD_RENDER_JSON_READY`  
**Rollback**: N/A (export-only, nessuna runtime mutation)

---

## 1. Scopo

Renderizzare il **template V7 BLOCK_D** (`AF2N_V8_CANARY_HEALTH_DASHBOARD_V1`) in un **artefatto JSON concreto** compatibile con il subset Grafana schema, pronto per provisioning futuro.

**Nessuna** connessione runtime, **nessun** daemon, **nessun** external service.

## 2. Upstream

- V7 BLOCK_D template: `/app/data/design/system_safety/af2n_observability_dashboard_template_v1.json`

## 3. Dashboard rendered structure

| Campo | Valore |
|---|---|
| `uid` | `af2n_v8_canary_health` |
| `title` | AF2-N V8 Canary Health Dashboard |
| `refresh` | 30s |
| `time` | now-24h → now |
| `timezone` | utc |
| Panel count | **8** |
| Alert rules | **5** |
| V8 signoff gating panels | **4** (P1, P2, P5, P6) |
| Templating variables | 2 (`endpoint`, `reason`) |
| External connections | **0** |
| Datasource placeholders | 2 (`af2n_metrics_ds`, `suite_runs_ds`) |

## 4. Panels (8) + Alerts (5) mapping

| Panel | Title | Type | Metric | Gating | Alert |
|---|---|---|---|---|---|
| P1 | Canary Completion Ratio | stat | `af2n_canary_completion_ratio` | ✅ DBR_02 | A1 |
| P2 | Ledger Write Failures by Reason | barchart | `af2n_ledger_write_failures_total` | ✅ | A2 |
| P3 | Rate-Limit Throttle by Endpoint | timeseries | `af2n_rate_limit_throttle_total` | — | — |
| P4 | Redis Crash Events / Mitigation | stat dual | `af2n_redis_crash_events_total` + mitigations | — | A3 |
| P5 | Inventory Writes Blocked (FROZEN) | stat | `af2n_inventory_writes_blocked_frozen_total` | ✅ | A4 |
| P6 | Affinity Gain Delta vs Control | timeseries | `af2n_affinity_gain_delta_vs_control` | ✅ DBR_02 | A5 |
| P7 | Gift Spend Volume Distribution | heatmap | `af2n_gift_spend_volume_seconds_bucket` (p50/p95/p99) | — | — |
| P8 | V21..V24 Rollback Test Timeline | timeline | `suite_optional_validator_runs{task_id=~af2n_v2[1-4]_rollback_readiness.*}` | — | — |

## 5. Placeholders runtime

Due datasource placeholders intenzionalmente lasciati come `<placeholder:...>`:
- `<placeholder:af2n_metrics_ds>` → verra' valorizzato dal provisioning ops pack (Prometheus o equivalente)
- `<placeholder:suite_runs_ds>` → verra' valorizzato dall'export V6 BLOCK_B se elevato a metric source

## 6. Validator

- **Path**: `/app/backend/scripts/validate_af2n_dashboard_render_json_v1.py`
- **Suite task_id**: `V8-BLOCK-C-AF2N-DASHBOARD-RENDER-JSON` (OPTIONAL)
- **Type**: read-only (no HTTP, no DB, no external service)
- **Verifiche**: 8 panel canonici, 5 alert con panel_ref, 4 gating panel, 0 daemon, 0 external connections, upstream template presente

## 7. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| AF2-N runtime mutation | ❌ No |
| Dashboard daemon | ❌ No |
| External service connection | ❌ No |
| Public spend UI | ❌ No |
| STACK-G changes | ❌ No |

## 8. Cosa sblocca

- Gate `EV-OBSERVABILITY-DASHBOARDS` (in `af2n_broad_rollout_signoff_package_v7.json`) avanza da `PENDING` a `PROVIDED_RENDER_JSON_READY`.
- Provisioning ops pack futuro: traduzione 1-to-1 della render JSON in Grafana (via API o file di config).
