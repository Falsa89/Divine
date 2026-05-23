# 119B — V5 BLOCK B — AF2-N OBSERVABILITY METRICS PIPELINE

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V5`  
**Block**: B — `AF2N_OBSERVABILITY_METRICS_PIPELINE_PACK`  
**Verdict**: 🟢 `BLOCK_B_AF2N_OBSERVABILITY_PIPELINE_READY`  
**Modalità**: OBSERVABILITY/DOC/SUITE ONLY (no runtime mutation)

---

## 1. Metrics schema (5 family, 16 metrics)

| Family | # metrics | Esempi |
|---|---|---|
| `canary` | 3 | `af2n_canary_active_users_total`, `af2n_canary_completion_ratio`, `af2n_canary_error_rate_5xx` |
| `ledger` | 3 | `af2n_ledger_writes_total`, `af2n_ledger_write_latency_seconds`, `af2n_ledger_write_failures_total` |
| `rate_limit` | 3 | `af2n_rate_limit_throttle_total`, `af2n_redis_crash_events_total`, `af2n_redis_mitigation_invocations_total` |
| `inventory_writes` | 2 | `af2n_inventory_writes_attempted_total`, `af2n_inventory_writes_blocked_frozen_total` |
| `affinity_gain` | 2 | `af2n_affinity_gain_delta_vs_control`, `af2n_gift_spend_volume_seconds` |

---

## 2. Validator mapping (V12-V30)

| Range | Mapping |
|---|---|
| V12-V14 | preflight design iterations |
| V18 | preflight validator |
| V19 | preflight validator |
| V21 | preflight + rollback validators |
| V22 | preflight + rollback validators |
| V23 | preflight + redis_switch + rollback (3 validators) |
| V24 | preflight + rollback validators |
| V25-V30 | reserved for future signoff |
| V8 signoff | NOT_ACHIEVED (target) |
| V4 canary report | consolidated reference |

---

## 3. Dashboard spec

| Campo | Valore |
|---|---|
| Target platform | Prometheus scrape OR JSONL file |
| Collector mode | **NON-RUNTIME** (read-only export su richiesta in `/app/data/design/system_safety/af2n_metrics_snapshot.jsonl`) |
| Refresh cadence | Manuale (no daemon) |
| Panels raccomandati | Canary completion, Ledger failures by reason, Rate-limit throttle, Redis crash/mitigation, Inventory writes blocked, Affinity gain delta |

---

## 4. Non-runtime audit validator

- **Script**: `/app/backend/scripts/validate_af2n_observability_pipeline_v1.py`
- **Behavior**: verifica presenza schema JSON + correct metric_families count + presenza V4 canary report
- **Writes**: nessuno
- **DB writes**: 0

---

## 5. Verdict

🟢 **`BLOCK_B_AF2N_OBSERVABILITY_PIPELINE_READY`**
