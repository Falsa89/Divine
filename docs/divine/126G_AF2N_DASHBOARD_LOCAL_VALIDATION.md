# 126G — PROJECT_D Track G — AF2-N DASHBOARD LOCAL VALIDATION

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_D`  
**Verdict**: 🟢 `TRACK_G_AF2N_DASHBOARD_LOCAL_VALIDATION_READY`  
**Rollback**: N/A (validator only)

## Scopo

Validare **localmente** i 3 template Grafana emessi in V_C Track F. Nessun call esterno; nessuna provisioning verso Grafana di produzione.

## Check eseguiti

| File | Top key | Min entries | Required fields |
|---|---|---|---|
| `af2n_datasource.yaml.template` | `datasources:` | 1 | `name`, `type`, `url` |
| `af2n_dashboard_provisioning.yaml.template` | `providers:` | 1 | `name`, `type`, `options` |
| `af2n_alerts.yaml.template` | `groups:` | 1 + min 5 rules | `uid`, `title`, `labels` |

## Alert metric family coverage

Richiesti 5 UID canonici:

- `af2n_a1_canary_error_rate`
- `af2n_a2_latency_p99`
- `af2n_a3_ratelimit_block_rate`
- `af2n_a4_ledger_idempotency_collision`
- `af2n_a5_canary_traffic_share_drift`

Richieste 3 severity coperte: `pager`, `email`, `slack`.

## Forbidden scope rispettato

External calls ❌, AF2-N runtime mutation ❌, public spend UI ❌.
