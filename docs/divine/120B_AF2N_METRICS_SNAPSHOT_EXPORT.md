# 120B — V6 BLOCK B — AF2-N METRICS SNAPSHOT EXPORT

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V6`  
**Block**: B — `AF2N_METRICS_SNAPSHOT_EXPORT_PACK`  
**Verdict**: 🟢 `BLOCK_B_AF2N_METRICS_SNAPSHOT_EXPORT_READY`  
**Modalità**: SUITE/DOC/EXPORT ONLY

---

## 1. Reference pipeline

Definita in V5 BLOCK_B (`af2n_observability_metrics_pipeline_v1.json`) — 5 family / 16 metrics: canary, ledger, rate_limit, inventory_writes, affinity_gain.

---

## 2. Export script

| Campo | Valore |
|---|---|
| Path | `/app/backend/scripts/export_af2n_metrics_snapshot_v1.py` |
| Mode | **non-runtime on-demand** |
| Output | `/app/data/design/system_safety/af2n_metrics_snapshot.jsonl` |
| Daemon | ❌ No |
| DB writes | **0** |
| Redis writes | **0** |
| Hits runtime endpoints | GET-only (read-only smoke) |
| Runs in suite | ❌ No (solo invocazione esplicita) |

---

## 3. Snapshot format (JSONL)

```json
{
  "timestamp_utc": "ISO8601",
  "metric_family": "canary",
  "metric_name": "af2n_canary_active_users_total",
  "value": 42,
  "labels": {"cohort": "v8_canary"},
  "source": "/api/affinity/gift-spend/canary-status"
}
```

---

## 4. Validator (in suite, OPTIONAL)

| Campo | Valore |
|---|---|
| Path | `/app/backend/scripts/validate_af2n_metrics_snapshot_export_v1.py` |
| Behavior | verifica script export presente; verifica JSONL parseable se presente |
| Esegue export | ❌ No |
| Safe in suite | ✅ Yes |

---

## 5. Non-runtime guarantees

- ❌ no metric emit verso collector esterno
- ❌ no daemon
- ❌ no continuous polling
- ❌ no write-back to runtime
- ✅ export idempotente
- ✅ solo GET API calls

---

## 6. Verdict

🟢 **`BLOCK_B_AF2N_METRICS_SNAPSHOT_EXPORT_READY`**
