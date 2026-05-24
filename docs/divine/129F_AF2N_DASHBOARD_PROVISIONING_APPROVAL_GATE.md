# 129F — AF2-N Dashboard Provisioning Approval Gate (Track F)

**Verdict:** `TRACK_F_AF2N_DASHBOARD_PROVISIONING_APPROVAL_GATE_READY`

## 5 Approval Gates (tutte PENDING)
1. `OPS_APPROVAL` (ops_lead) — finestra di provisioning + rollback approvati.
2. `ALERT_SINK_CONFIGURED` (ops_lead) — sink alert (slack/pagerduty/email)
   instradato e testato in dry-run.
3. `DASHBOARD_DATA_SOURCE_CONFIGURED` (ops_lead) — Grafana data source UID
   confermato, scrape healthy.
4. `NO_SECRET_LEAKAGE` (qa_lead) — audit conferma assenza di leak di
   `AF2N_GRAFANA_API_TOKEN` o secret correlati.
5. `ROLLBACK_NO_OP_PATH` (ops_lead) — rollback script testato localmente;
   no-op path verificato.

## Future env requirements
- `AF2N_GRAFANA_URL`
- `AF2N_GRAFANA_API_TOKEN`
- `AF2N_DASHBOARD_FOLDER_UID`
- `AF2N_ALERT_SINK_URL`

## Vincoli rispettati
- NO external service calls; NO AF2-N runtime mutation;
  NO public spend UI; NO STACK-G changes.
