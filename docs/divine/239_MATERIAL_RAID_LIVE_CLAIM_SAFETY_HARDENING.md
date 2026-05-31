# 239 - PROJECT_MATERIAL_RAID_LIVE_CLAIM_SAFETY_HARDENING_PACK (v37 Track B)

**Mode**: ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_CLAIM  
**Flag**: `MATERIAL_RAID_CLAIM_SAFETY_PREVIEW_ENABLED` (default off -> 503)

## Endpoints
- `GET /api/material-raid-claim-safety-preview/config`
- `POST /api/material-raid-claim-safety-preview/validate-claim-request`
- `POST /api/material-raid-claim-safety-preview/grant-plan-preview`
- `POST /api/material-raid-claim-safety-preview/idempotency-preview`

## 15 guard checks (preview)
`ownership_verified`, `track_id_valid`, `stage_id_valid`, `raid_clear_instance_id_future_match`, `not_already_claimed_future`, `expected_reward_hash_match`, `expected_reward_table_version_match`, `idempotency_key_required`, `user_materials_future_target_acquired`, `atomic_increment_future`, `rollback_strategy_required_future`, `audit_log_required_future`, `no_stamina_consumed`, `no_tickets_consumed`, `no_paid_attempt_consumed`.

## Safety
`claim_enabled=false`, `materials_granted=false`, `user_materials_mutation_enabled=false`, `stamina_consumed=false`, `tickets_consumed=false`, `paid_attempt_consumed=false`, `db_writes=0`. Esistente `backend/routes/material_raid_preview.py` invariato.
