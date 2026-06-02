# 294 — Live Ledger (DESIGN-ONLY)

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_14_EPHEMERAL_SIMULATION_INVARIANT_REPORT_AND_STAGING_DB_BLUEPRINT_PACK_v50`
**Track**: C
**Public Sync Tag**: `PUBLIC_SYNC_TAG_v50_MEGA_ECONOMY_SAFETY_ACCELERATION_14`
**Contract version**: `live_ledger_design_only_v1`

## Scopo
Fissare a livello di **design** gli schemi del futuro ledger live (idempotency,
audit, rollback, operator decision) senza alcuna implementazione runtime, senza
creare collezioni reali e senza scrivere su DB.

## File design
- `data/design/economy_safety/live_ledger_design_only_v1.json`
- `data/design/economy_safety/live_ledger_design_only_marker_v1.json`

## Schemi (4)
1. **`idempotency_ledger_entry`** — required fields: `ledger_key`, `operation_family`,
   `user_id`, `payload_hash`, `table_version`, `status`, `created_at_design`,
   `ttl_design_seconds`. Unique by `ledger_key`. TTL default 86400.
2. **`audit_event`** — required fields: `event_id_preview`, `operation_family`,
   `user_id`, `event_type`, `scenario`, `created_at_design`. PII-safe,
   `raw_payload_captured = false`.
3. **`rollback_record`** — required fields: `rollback_id_preview`,
   `operation_family`, `user_id`, `reason`, `original_ledger_key_ref`,
   `created_at_design`. `actual_reversal_performed = false`.
4. **`operator_decision`** — required fields: `decision_id_preview`,
   `operation_family`, `approver`, `decision`, `rationale`,
   `approval_phrase_recorded`, `checksum_sha256_ref`, `created_at_design`.
   Approver enum: `system_dry_run`, `owner_pending`, `qa_pending`,
   `game_director_pending`.

Ogni schema: `design_only=true`, `runtime_created=false`.

## 8 Famiglie di operazione
Ogni famiglia: `runtime_ledger_created=false`, `live_apply_allowed=false`,
`live_implementation_deferred=true`, `db_writes=0`.
`battle_pass_reward_claim` → `no_bp_delta_runtime=true`.
`mail_reward_claim` → `no_mail_state_mutation=true`.

## Forbidden
no_runtime_ledger_creation · no_real_db_connection · no_mongo_url · no_pymongo ·
no_motor · no_env_read · no_filesystem_writes · no_live_apply ·
no_production_mutation · no_reward_grant · no_endpoint_path_change ·
no_feature_flag_change · no_default_503_change · no_server_py_change ·
no_frontend_change · no_battle_engine_change
