# 118E — V4 BLOCK E — REDIS RATE-LIMIT HARDENING OPS

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V4`  
**Block**: E — `REDIS_RATE_LIMIT_HARDENING_OPS_PACK`  
**Verdict**: 🟢 `BLOCK_E_REDIS_RATE_LIMIT_HARDENING_OPS_READY`  
**Modalità**: OPS/DOC ONLY (nessun cambio runtime permanente)

---

## 1. Existing ops helper

| Campo | Valore |
|---|---|
| Script | `/app/ops/ensure_redis_rate_limit.sh` |
| Behavior | verify redis-server running; if down, restart + re-enable rate-limit |
| Invocation | manual or on V23/V24 preflight failure |
| Impact runtime | restart only when crashed; **idempotent** |

---

## 2. Known failure modes

| ID | Description | Symptom | Mitigation |
|---|---|---|---|
| FM1 | Redis binary drop in container (5+ recurrences) | Suite V23/V24 fail; AF2-N rate-limit bypassed | `bash /app/ops/ensure_redis_rate_limit.sh` |
| FM2 | Connection refused on `redis://localhost:6379` | AF2-N gift spend HTTP 503 | Restart redis-server, re-attempt; check container resource limits |

---

## 3. Runbook step-by-step

| # | Nome | Comando |
|---|---|---|
| 1 | Detect | `redis-cli ping` (expect `PONG`) |
| 2 | Suite check | `python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py \| tail -5` |
| 3 | Mitigate | `bash /app/ops/ensure_redis_rate_limit.sh` |
| 4 | Re-verify | `redis-cli ping && python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py \| tail -3` |

---

## 4. Non-invasive health check

**Script**: `/app/backend/scripts/audit_redis_rate_limit_ops_v1.py`

- Verifica presenza `/app/ops/ensure_redis_rate_limit.sh`
- Verifica presenza marker V4 BLOCK_E
- Verifica disponibilità binario `redis-cli`
- **NON** esegue `PING` per evitare effetti collaterali in CI/suite
- **NON** modifica config Redis

---

## 5. Forbidden scope verification

| Constraint | Violato? |
|---|---|
| Redis config permanent change | ❌ No |
| Rate-limit policy change | ❌ No |
| Production runtime env change | ❌ No |
| Rate limits disabled | ❌ No |
| AF2-N behavior change | ❌ No |

---

## 6. Verdict

🟢 **`BLOCK_E_REDIS_RATE_LIMIT_HARDENING_OPS_READY`**
