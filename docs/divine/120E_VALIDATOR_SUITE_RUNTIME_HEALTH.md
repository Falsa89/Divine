# 120E — V6 BLOCK E — VALIDATOR SUITE RUNTIME HEALTH

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V6`  
**Block**: E — `VALIDATOR_SUITE_RUNTIME_HEALTH_PACK`  
**Verdict**: 🟢 `BLOCK_E_VALIDATOR_SUITE_RUNTIME_HEALTH_READY`  
**Modalità**: SUITE EXTENSION ONLY

---

## 1. Health checks (5)

| ID | Check | Contract | Fail action |
|---|---|---|---|
| **H1** | backend uvicorn responding 200 su `/api/heroes` | HTTP 200 | block |
| **H2** | heroes count == 100 | count == 100 | block |
| **H3** | redis binary running (supervisorctl status) | RUNNING | hint: `bash /app/ops/ensure_redis_rate_limit.sh` |
| **H4** | MongoDB reachable (best-effort, optional) | connect within 2s | warn |
| **H5** | observability rollup last-modified < 7 days | file mtime fresh | warn |

---

## 2. Validator

| Campo | Valore |
|---|---|
| Path | `/app/backend/scripts/validate_suite_runtime_health_v1.py` |
| Behavior | read-only HTTP smoke + supervisorctl status + file mtime |
| Non-invasive | ✅ |
| DB writes | **0** |

---

## 3. Suite registration

- **Task ID**: `V6-BLOCK-E-SUITE-RUNTIME-HEALTH`
- **Section**: OPTIONAL
- **Behavior**: non-blocking; warns ma non FAIL su transitori H3/H4 se H1/H2 ancora PASS

---

## 4. Forbidden scope verification

| Constraint | Violato? |
|---|---|
| Runtime route change | ❌ No |
| Weakening existing validators | ❌ No |
| Masking failures | ❌ No |
| Runtime health endpoint added | ❌ No (puramente client-side check) |

---

## 5. Verdict

🟢 **`BLOCK_E_VALIDATOR_SUITE_RUNTIME_HEALTH_READY`**
