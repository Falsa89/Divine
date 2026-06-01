# 260 — Economy Observability Runtime Dry-Run

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_6_DRY_RUN_RUNTIME_INSTRUMENTATION_PACK_v42` · Track B  
**Modalità**: DRY_RUN_RUNTIME_INSTRUMENTATION_NO_LIVE_APPLY  
**Runtime activation**: `false`  
**DB writes**: `0`

### Scopo

Introdurre runtime dry-run della observability foundation v41 nelle 8 safety
preview route. Aggiunge `audit_event_preview` (mai persistito) e
`metric_sample_preview` (mai shippato) al response. Nessun sink esterno,
nessuna dashboard runtime, nessun client Prometheus attivato.

### Utility modulo

`backend/utils/economy_observability_dry_run.py`

Funzioni:

- `build_audit_event_preview(operation_family, operation_type, outcome, request_hash, ...)` → dict
- `build_metric_sample_preview(operation_family, route, status)` → dict
- `build_observability_dry_run_envelope(...)` → dict
- `build_config_block()` → dict per `/config`

### Comportamento

- audit event matcha lo schema `economy_safety_observability_audit_schema_v1`
- user_id sempre hashed (sha256 con salt server, truncato 32 char) o omesso
- audit_event_id è un UUID v4 generato ad-hoc
- counters in metric_sample includono counters-invariante = 0
- nessuna persistenza, nessun sink, nessun shipping esterno
- **no DB writes**, **no PII**

### Invariant counters (devono restare a 0)

- `economy_safety_db_writes_total`
- `economy_safety_live_commit_executions_total`
- `economy_safety_live_claim_executions_total`
- `economy_safety_reward_grants_total`
- `economy_safety_premium_currency_mutations_total`
- `economy_safety_bp_delta_triggers_total`

### Wire-up

8 safety preview route con flag ON ritornano:

```json
{
  "observability_dry_run": {
    "enabled": true,
    "audit_event_preview_created": true,
    "metric_sample_preview_created": true,
    "persistent_audit_write_enabled": false,
    "alert_sink_live_enabled": false,
    "dashboard_runtime_deployed": false,
    "external_sink_shipping_enabled": false,
    "raw_pii_in_payload": false,
    "db_writes": 0
  }
}
```

### Vincoli rispettati

- nessun cambio di endpoint path
- nessun cambio di feature flag
- nessun cambio del default 503
- nessun import di librerie esterne
- nessun DB write
- nessuna PII nel response
