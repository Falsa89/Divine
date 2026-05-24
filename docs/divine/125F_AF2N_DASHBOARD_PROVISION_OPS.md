# 125F — PROJECT_C Track F — AF2-N DASHBOARD PROVISION OPS TEMPLATES

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_C`  
**Track**: F  
**Mode**: `local_templates_only_no_external_integration`  
**Verdict**: 🟢 `TRACK_F_AF2N_DASHBOARD_PROVISION_OPS_TEMPLATES_READY`  
**Rollback**: eliminare `/app/ops/grafana/templates/*.template` (zero impatto runtime)

---

## 1. Scopo

Emettere localmente i **template di provisioning Grafana** definiti in V_B Track F come **file locali inerti**, senza chiamate esterne né secret bakati. Nessun applicate a Grafana di produzione, nessun rollout AF2-N pubblico.

## 2. Template emessi

| File | Phase | Scopo |
|---|---|---|
| `af2n_datasource.yaml.template` | 1 | Datasource Prometheus-compatibile (placeholder URL + token) |
| `af2n_dashboard_provisioning.yaml.template` | 2 | Provider Grafana per la dashboard `af2n_v8_canary_health.json` |
| `af2n_alerts.yaml.template` | 3 | 5 regole A1..A5 con sink placeholder (pager/email/slack) |

## 3. Placeholder canonici (tutti `${...}`)

- `${AF2N_METRICS_DS_URL}`
- `${AF2N_METRICS_DS_TOKEN}`
- `${AF2N_PAGER_TOKEN}`
- `${AF2N_SMTP_PASSWORD}`
- `${AF2N_SLACK_WEBHOOK_URL}`
- `${GRAFANA_PROVISIONING_PATH}`

Nessun secret reale è committato; il validator esegue una verifica euristica contro pattern noti (`-----BEGIN`, `ghp_`, `glpat-`, `AKIA`, `xoxb-`).

## 4. Production apply status

`DESIGNED_NOT_AUTHORIZED` — l'applicazione live richiede signoff Ops + iniezione delle 6 env vars sul nodo Grafana.

## 5. Forbidden scope rispettato

AF2-N runtime mutation ❌, external service integration ❌, public spend UI ❌, STACK-G changes ❌, AF2-N public rollout ❌.

## 6. Validator

`/app/backend/scripts/validate_project_c_af2n_dashboard_provision_ops_v1.py` — controlla presenza dei 3 file, presenza dei 6 placeholder, assenza di pattern secret bakati.
