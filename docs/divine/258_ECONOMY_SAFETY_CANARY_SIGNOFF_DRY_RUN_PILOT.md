# 258 — Economy Safety Canary/Signoff Dry-Run Pilot

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_6_DRY_RUN_RUNTIME_INSTRUMENTATION_PACK_v42` · Track C  
**Modalità**: DESIGN_CONTRACT_AUDIT_ONLY  
**Runtime activation**: `false`  
**DB writes**: `0`

### Scopo

Pilot **design-only** di canary/signoff per **una sola** famiglia operation:
`material_raid_claim`. Scelta motivata da:

- è un flusso di reward claim ad alto valore
- centrale nel gameplay loop
- ha già safety preview attiva da v37
- ha copertura request hash + observability dry-run da v41/v42

### Stato del pilot in questo pack

- `operation_family = "material_raid_claim"`
- `signoff_state = "pending"`
- `approved_by = null`
- `canary_enabled = false`
- `canary_percentage = 0`
- `live_enabled = false`
- `live_claim_enabled = false`
- `reward_grant_enabled = false`
- `material_grant_enabled = false`
- `premium_currency_use_enabled = false`
- `bp_delta_runtime_enabled = false`
- `db_writes = 0`

### Kill switch

- env var: `MATERIAL_RAID_CLAIM_CANARY_KILL_SWITCH`
- default state: `engaged_kill`

### Alert richiesti (sempre armati)

- `ALERT_DB_WRITES_NONZERO`
- `ALERT_LIVE_CLAIM_NONZERO`
- `ALERT_REWARD_GRANTS_NONZERO`
- `ALERT_IDEMPOTENCY_CONFLICT_SPIKE`
- `ALERT_REQUEST_HASH_MISMATCH_SPIKE`

### Dashboard

- `economy_safety_overview_v1` (definita in v41)

### Approver richiesti per `signoff approved`

- `game_director`
- `technical_producer`
- `qa_owner`
- `rollback_owner`

### Rollback link

Utilizza il template `material_raid_claim` da
`economy_safety_pre_signoff_rollback_templates_v1.json` (v41).

### Non in questo pack

- Flip di signoff verso `approved`
- Flip di canary (`canary_enabled`/`canary_percentage`)
- Flip di live
- Reward/material grant
- DB writes
