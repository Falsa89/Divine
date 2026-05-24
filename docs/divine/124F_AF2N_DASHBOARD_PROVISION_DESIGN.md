# 124F — PROJECT_B Track F — AF2N_DASHBOARD_PROVISION_DESIGN

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_B`  
**Track**: F  
**Mode**: `design_doc_export_only_no_external_integration`  
**Verdict**: 🟢 `TRACK_F_AF2N_DASHBOARD_PROVISION_DESIGN_READY`

---

## 1. Scopo

Definire i **4 step di provisioning** del dashboard AF2-N a Grafana, basandosi sul render JSON V8 BLOCK_C, **senza** alcuna external service integration ne' deployment.

## 2. Provisioning phases (4)

### Phase 1 — DATASOURCE_REGISTRATION
- Registrare `af2n_metrics_ds` (Prometheus) + `suite_runs_ds` come Grafana provisioned datasources
- Secrets: `AF2N_METRICS_DS_URL`, `AF2N_METRICS_DS_TOKEN`
- Status: `DESIGNED_NOT_PROVISIONED`

### Phase 2 — DASHBOARD_FILE_PROVISIONING
- Convertire render JSON V8 BLOCK_C in Grafana provisioning YAML
- Target: `/etc/grafana/provisioning/dashboards/af2n_v8_canary_health.json`
- Status: `DESIGNED_NOT_PROVISIONED`

### Phase 3 — ALERT_RULES_PROVISIONING
- Deploy 5 alert rules (A1-A5) via Grafana alerting provisioning
- Target: `/etc/grafana/provisioning/alerting/af2n_alerts.yaml`
- Sinks required:
  - `sink_pager` (PagerDuty/Opsgenie) per A1, A4
  - `sink_email` (SMTP) per A2, A3
  - `sink_slack` (webhook) per A5
- Secrets: `AF2N_PAGER_TOKEN`, `AF2N_SMTP_PASSWORD`, `AF2N_SLACK_WEBHOOK_URL`
- Status: `DESIGNED_NOT_PROVISIONED`

### Phase 4 — PRODUCTION_TURN_ON
- Enable provisioning in production
- Canary panels P1/P2/P5/P6 visibili a SRE oncall
- Status: `DESIGNED_NOT_AUTHORIZED`

## 3. Env vars required (future)

```
AF2N_METRICS_DS_URL
AF2N_METRICS_DS_TOKEN
AF2N_PAGER_TOKEN
AF2N_SMTP_PASSWORD
AF2N_SLACK_WEBHOOK_URL
GRAFANA_PROVISIONING_PATH
```

## 4. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| AF2-N runtime mutation | ❌ No |
| External service integration | ❌ No |
| Public spend UI | ❌ No |
| STACK-G changes | ❌ No |

## 5. Cosa sblocca

- Gate AF2-N `EV-OBSERVABILITY-DASHBOARDS`: avanza da `PROVIDED_RENDER_JSON_READY` (V8 BLOCK_C) a `PROVIDED_RENDER_JSON_AND_PROVISIONING_DESIGN_READY` (V_B Track F).
- Provisioning ops pack futuro: traduzione 1-to-1 dei 4 phase in script di deployment.
