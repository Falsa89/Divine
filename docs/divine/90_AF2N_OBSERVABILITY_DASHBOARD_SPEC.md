# AF2-N Observability Dashboard Spec V1

**Task origin**: `AF2-N-V30-OBSERVABILITY-DASHBOARD-SPEC`
**Mode**: PLAN_ONLY (nessuna integrazione runtime in V30)
**Datasource**: Prometheus + Loki + Grafana; pushgateway opzionale per off-cluster bursts

## Panels (12)
| # | ID | Titolo | Tipo | Metric | Severity |
|---|----|--------|------|--------|----------|
| 1 | success_rate | Gift-spend success rate (5m) | graph | `af2n_gift_spend_success_count` | INFO |
| 2 | http_423 | HTTP 423 (disabled/non-allowlist) | graph | `af2n_gift_spend_http_423` | INFO |
| 3 | http_429 | HTTP 429 (rate limit) | graph | `af2n_gift_spend_http_429` | WARN |
| 4 | borea_attempts | Borea alias attempts (must be 0 success) | stat | `af2n_borea_attempt_total` | CRITICAL |
| 5 | redis_fail_open | Rate-limit Redis fail-open | stat | `af2n_rate_limit_fail_open_total` | CRITICAL |
| 6 | backend_not_redis | Backend != redis | singlestat | `af2n_rate_limit_backend` | CRITICAL |
| 7 | negative_inventory | Negative inventory rows | singlestat | `af2n_negative_inventory_rows` | CRITICAL |
| 8 | delta_mismatch | Delta audit mismatches | stat | `af2n_delta_mismatch_total` | HIGH |
| 9 | cap_pressure | Ledger cap pressure (rows / cap) | gauge | `af2n_ledger_cap_pressure` | WARN |
| 10 | p95_p99_latency | Spend p95/p99 latency | graph | `af2n_gift_spend_latency_ms` | INFO |
| 11 | http_5xx | HTTP 5xx | graph | `af2n_gift_spend_http_5xx` | CRITICAL |
| 12 | idempotent_replay | Idempotent replay hits | graph | `af2n_idempotent_replay_total` | INFO |

## Alert Rules (7)
| Rule ID | Condition | Severity | Action |
|---------|-----------|----------|--------|
| borea_success_alert | `borea_attempts.success > 0` | CRITICAL | rollback_runtime |
| unauthorized_spend_alert | `non_allowlist.applied > 0` | CRITICAL | rollback_runtime |
| backend_not_redis | `backend != "redis"` | HIGH | restore_local_redis |
| rate_limit_fail_open | `fail_open_count > 0` | HIGH | restore_local_redis |
| negative_inventory | `negative_inventory_rows > 0` | CRITICAL | pause_writes |
| cap_pressure_high | `ledger_rows / cap > 0.8` | MEDIUM | consider_cap_raise_plan |
| http_5xx_critical | `5xx_per_5m > 10` | CRITICAL | page_oncall |

## Deployment (futuro, V31+)
1. Esporre metriche Prometheus dal backend (es. `/metrics` endpoint con `prometheus_client`)
2. Deploy Grafana via Helm chart con datasource Prometheus
3. Importare il JSON dei panel come dashboard
4. Configurare Alertmanager con i 7 rule
5. Validare con incident sintetici prima di abilitare paging on-call

## Safety
- ✅ Plan-only, nessun runtime change in V30
- ✅ Nessun secret nei panel/alert payload
- ✅ Nessun PII
- ✅ Borea alias non comparirà nei dashboard se non come `borea_attempt_total` (counter aggregato, no per-user)
