# 255 — MEGA_ECONOMY_SAFETY_ACCELERATION_5 v41 · Track B

## Economy Safety Observability Foundation

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_5_OBSERVABILITY_SIGNOFF_AND_REQUEST_HASH_PACK_v41`  
**Track**: B  
**Modalità**: DESIGN_CONTRACT_AUDIT_ONLY  
**Runtime activation**: `false`  
**DB writes**: `0`

### Scopo

Fondazione di osservabilità per la safety economy (preview-only). Definisce:

1. **Audit schema** (`audit_schema_v1.json`): forma canonica del record di
   audit con campi required/optional/forbidden + tipi e enum.
2. **Privacy policy** (`privacy_policy_v1.json`): classificazione PII,
   redazione, retention, export, data-subject rights.
3. **Metrics** (`metrics_v1.json`): catalogo di counter / histogram / gauge
   con limiti di cardinalità e label proibite.
4. **Dashboard panels** (`dashboard_panels_v1.json`): definizioni dei
   pannelli per la dashboard `economy_safety_overview_v1`.
5. **Alert rules** (`alert_rules_v1.json`): regole critiche
   (DB-writes, live-commit, live-claim, reward-grants devono restare 0) +
   warning su idempotency conflicts, hash mismatches, validation errors.

### File creati

- `data/design/economy_safety/economy_safety_observability_audit_schema_v1.json`
- `data/design/economy_safety/economy_safety_observability_privacy_policy_v1.json`
- `data/design/economy_safety/economy_safety_observability_metrics_v1.json`
- `data/design/economy_safety/economy_safety_observability_dashboard_panels_v1.json`
- `data/design/economy_safety/economy_safety_observability_alert_rules_v1.json`
- `data/design/economy_safety/economy_safety_observability_foundation_proof_marker_v1.json`
- `backend/scripts/validate_economy_safety_observability_foundation_v1.py`

### Invarianti di sicurezza

L'audit record **non** può contenere PII. Devono restare a zero le 4
metriche-invariante:

- `economy_safety_db_writes_total`
- `economy_safety_live_commit_executions_total`
- `economy_safety_live_claim_executions_total`
- `economy_safety_reward_grants_total`

Qualsiasi valore non-zero attiva alert **critical** e congela il signoff.

### Cardinalità label

- `operation_family` max 8
- `operation` max 64
- `outcome` max 5
- `validation_error_code` max 64

### Retention

- audit records: 30 giorni default / 90 max
- metrics: 90 giorni default / 365 max
- dashboard screenshots: 30 giorni default / 90 max

### Non in questo pack

- Implementazione runtime dell'audit pipeline
- Implementazione runtime delle metriche (nessun client Prometheus attivato)
- Implementazione runtime degli alert (nessun Alertmanager configurato)
- Modifiche a `server.py` (intatto)
