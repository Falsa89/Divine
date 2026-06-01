# 256 — MEGA_ECONOMY_SAFETY_ACCELERATION_5 v41 · Track C

## Pre-Signoff & Rollback Bundle

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_5_OBSERVABILITY_SIGNOFF_AND_REQUEST_HASH_PACK_v41`  
**Track**: C  
**Modalità**: DESIGN_CONTRACT_AUDIT_ONLY  
**Runtime activation**: `false`  
**DB writes**: `0`

### Scopo

Bundle di pre-signoff e rollback per le 8 famiglie operation:

1. **Readiness matrix** (`readiness_matrix_v1.json`): copertura per famiglia
   (preview, validator, proof marker, server registration, request hash
   contract, observability metrics, alert rules, rollback template).
2. **Signoff register** (`signoff_register_v1.json`): stato signoff per
   famiglia (tutte `pending`) + state machine.
3. **Canary/Live state** (`canary_live_state_v1.json`): stato canary/live
   (tutti disabled, pct=0) + canary policy.
4. **Rollback templates** (`rollback_templates_v1.json`): 8 template di
   rollback (uno per famiglia), tutti idempotent e dry-run only.

### File creati

- `data/design/economy_safety/economy_safety_pre_signoff_readiness_matrix_v1.json`
- `data/design/economy_safety/economy_safety_pre_signoff_signoff_register_v1.json`
- `data/design/economy_safety/economy_safety_pre_signoff_canary_live_state_v1.json`
- `data/design/economy_safety/economy_safety_pre_signoff_rollback_templates_v1.json`
- `data/design/economy_safety/economy_safety_pre_signoff_rollback_bundle_proof_marker_v1.json`
- `backend/scripts/validate_economy_safety_pre_signoff_bundle_v1.py`

### Invarianti di stato

In questo pack, per **tutte** le 8 famiglie:

- `signoff_state = "pending"`
- `canary_enabled = false`
- `live_enabled = false`
- `canary_pct = 0`
- `db_writes = 0`

### Signoff state machine

```
pending  --(v42 signed zip)-->         approved
pending  --(safety breach alert)-->    blocked
approved --(safety breach alert)-->    blocked
approved --(rollback signed zip)-->    rolled_back
blocked  --(remediation signed zip)--> pending
```

### Rollback policy

Ogni template definisce:

- `trigger_conditions`: alert critici o manual override
- `steps_dry_run_only`: disable flag, freeze signoff, audit transition,
  notify on-call, snapshot 60m metrics
- `rollback_idempotent = true`
- `db_writes = 0`

Il rollback **non** viene mai eseguito in questo pack: solo template di
design. La live execution arriverà come zip firmato separato.

### Non in questo pack

- Esecuzione live del rollback
- Flip di signoff verso `approved` (riservato a v42 signed zip)
- Flip di canary/live (riservato a v42 signed zip)
