# AF2-N Stage 4 Support Runbook V25

**Task origin**: `AF2-N-V25-SUPPORT-RUNBOOK`  
**Audience**: Support Tier 1 / Tier 2, On-call backend, Economy ops  
**Replaces**: `84_SUPPORT_ECONOMY_PREP_V24.md` (V24 was triage-only; V25 adds incident response)

---

## 1. Incident severity matrix

| Severity | Definition | Response time | Owner |
|---|---|---|---|
| **P0** | Borea/hidden alias leak, unauthorized spend, 5xx wave, negative inventory | < 5 min | On-call backend |
| **P1** | Redis outage, rate-limit backend degraded, delta mismatch, ledger overflow | < 30 min | On-call backend + Economy |
| **P2** | 429 spike, single-user complaint, latency increase | < 4 hours | Tier 2 |
| **P3** | Cosmetic / FAQ / individual ticket | next business day | Tier 1 |

---

## 2. P0 — Borea leak emergency

**Symptom**: `/api/heroes` contains `borea`, `greek_borea`, or `primordial_gaia`, OR `/api/affinity/gift-spend` returns non-404 for these aliases.

```bash
# 1. CONFIRM
curl -s http://localhost:8001/api/heroes | python3 -c "import sys,json;ids={(h.get('id') or '').lower() for h in json.load(sys.stdin)};print(ids & {'borea','greek_borea','primordial_gaia'})"
for h in borea greek_borea primordial_gaia; do
  curl -s -o /dev/null -w "$h %{http_code}\n" -X POST http://localhost:8001/api/affinity/gift-spend \
    -H "Content-Type: application/json" -d "{\"gift_id\":\"x\",\"hero_id\":\"$h\",\"quantity\":1,\"idempotency_key\":\"oncall_check\",\"user_id\":\"stage4_qa_001\"}"
done
```

**Mitigation**:
1. Page on-call backend P0 IMMEDIATELY.
2. Set `AFFINITY_GIFT_RUNTIME_ENABLED=false` in `/etc/supervisor/conf.d/backend.conf` and restart backend.
3. Snapshot ledger: `python3 /app/backend/scripts/run_af2n_v24_clone_rollback_drill.py`.
4. Investigate root cause before re-enabling.

**Customer comms (draft)**:
> We've detected an internal QA-only data flag exposed during Stage 4 Internal Beta. No production accounts are affected. Stage 4 Beta is paused while we investigate. ETA: 2 hours.

---

## 3. P0 — Unauthorized spend emergency

**Symptom**: user_id outside `AFFINITY_GIFT_CANARY_ALLOWLIST` produced a successful (200/201) gift-spend.

```bash
# 1. Inspect last 10 ledger entries
mongosh divine_waifus --quiet --eval "db.gift_transaction_ledger.find({}).sort({_id:-1}).limit(10).forEach(d=>print(JSON.stringify({tx:d.tx_id,u:d.user_id,canary:d.canary,status:d.status})))"
```

**Mitigation**:
1. Page on-call P0.
2. Disable feature flag (see §2 step 2).
3. Mark suspect rows: `db.gift_transaction_ledger.updateMany({user_id: '<u>'}, {$set: {emergency_flag: 'v25_review'}})`.
4. Refund inventory: manual review.

---

## 4. P0 — Negative inventory emergency

**Symptom**: any `user_gift_inventory.balances.*` value < 0.

```bash
mongosh divine_waifus --quiet --eval "db.user_gift_inventory.find({\"balances\":{\$exists:true}}).forEach(d=>{for(k in (d.balances||{})){if(d.balances[k]<0)print(d.user_id+' '+k+'='+d.balances[k])}})"
```

**Mitigation**:
1. Freeze inventory writes: `AFFINITY_GIFT_INVENTORY_WRITES_ENABLED` set empty in backend.conf, restart.
2. Recompute from ledger (V22 delta audit script).
3. Patch user balance with admin-only one-off (not from this runbook).

---

## 5. P1 — Redis outage / backend degraded

**Symptom**: `redis-cli ping` not PONG, OR `canary-status.rate_limit_backend != redis`, OR alert `redis_fail_open` firing.

```bash
bash /app/ops/ensure_redis_rate_limit.sh    # idempotent recovery
redis-cli ping
curl -s http://localhost:8001/api/affinity/gift-spend/canary-status | python3 -c "import sys,json;print(json.load(sys.stdin).get('rate_limit_backend'))"
```

**Mitigation**:
1. Run `/app/ops/ensure_redis_rate_limit.sh` (returns 0 = healthy).
2. If it fails with rc=1 (apt unavailable) → manual reinstall:
   ```bash
   apt-get update && apt-get install -y redis-server
   supervisorctl start redis
   ```
3. If it fails with rc=3 (Redis won't start) → fail-open is ACTIVE; backend is using in-memory fallback. **No customer impact** but reduced abuse protection.
4. Page on-call after 15 min if not resolved.

**Customer comms**: Not required — fail-open is transparent.

---

## 6. P1 — Delta mismatch (inventory vs ledger)

**Symptom**: `af2_inventory_delta_mismatch_total > 0` in metrics-snapshot.

```bash
python3 /app/backend/scripts/validate_affinity_inventory_delta_consistency_v23.py
```

**Mitigation**: Investigate before next deploy. Do NOT rollback DB.

---

## 7. P2 — Individual user 429 complaint

User sees 429 errors when attempting spend.

**Diagnose**:
```bash
curl -s http://localhost:8001/api/affinity/gift-spend/canary-status | python3 -m json.tool | grep rate_limit
# Limits: 30/min/user, 240/h/user, 60/min/ip, burst 6/10s
```

**Response**: "Stage 4 Internal Beta has rate limits to protect the live testing environment: max 30 spends/minute, 240/hour, burst 6 in 10 seconds. Please wait a few seconds between attempts."

---

## 8. Rollback commands quick reference

| Goal | Command |
|---|---|
| Disable runtime entirely | edit `backend.conf`, unset `AFFINITY_GIFT_RUNTIME_ENABLED`, `supervisorctl restart backend` |
| Disable inventory writes only | unset `AFFINITY_GIFT_INVENTORY_WRITES_ENABLED`, restart backend |
| Disable rate-limit (NOT recommended) | unset `AFFINITY_GIFT_RATE_LIMIT_ENABLED`, restart backend |
| Switch backend Redis → memory | set `AFFINITY_RATE_LIMIT_BACKEND=memory`, restart backend |
| Restore Redis supervisor | `bash /app/ops/restore_redis_supervisor_service.sh` |
| Full Stage 4 freeze (DRY-RUN sim only) | `python3 /app/backend/scripts/run_af2n_v24_clone_rollback_drill.py` |

**ABSOLUTE**: Never do `db.dropDatabase()` on production. Never restore DB from backup without economy ops approval.

---

## 9. Escalation owners

| Domain | Primary | Secondary |
|---|---|---|
| Backend / Redis ops | on-call backend | platform team |
| Economy / ledger | economy ops | game design |
| Frontend / UI safety | frontend lead | QA |
| Hero data / Borea | content lead | game design |
| Database | DBA on-call | backend lead |

---

## 10. Drill cadence

- Redis restart drill: monthly (`/app/backend/scripts/run_redis_rate_limit_restart_drill_v25.py`)
- Clone rollback drill: monthly (`/app/backend/scripts/run_af2n_v24_clone_rollback_drill.py`)
- Borea safety smoke: every release (`/app/backend/scripts/run_af2n_v25_preflight.py`)

---

## 11. Status checklist (one-liner)

```bash
bash /app/ops/ensure_redis_rate_limit.sh && \
  python3 /app/backend/scripts/run_af2n_v25_preflight.py && \
  echo "✅ Stage 4 healthy"
```

---

**Approved by**: Backend + Economy + Support leads (V25)  
**Next review**: V26 (broad-rollout signoff)
