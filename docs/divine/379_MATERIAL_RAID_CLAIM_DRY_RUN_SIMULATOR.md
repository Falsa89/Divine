# 379 — Material Raid Claim Dry-Run Simulator

Pack: `MEGA_RELEASE_ACCELERATION_13_MATERIAL_RAID_STAGING_DRY_RUN_AND_CANARY_SIMULATION_PACK_v64`

Tag: `PUBLIC_SYNC_TAG_v64_MEGA_RELEASE_ACCELERATION_13_MATERIAL_RAID_STAGING_DRY_RUN_AND_CANARY_SIMULATION`

## Scopo

Simulazione in-memory delle 6 decisioni canoniche del futuro claim:

- `first_claim_would_stage`
- `duplicate_same_payload_would_return_existing`
- `duplicate_conflict_would_reject`
- `missing_idempotency_key_would_reject`
- `over_canary_cap_would_reject`
- `rollback_preview_required`

## Invarianti

- Python puro, **nessun** import pymongo/motor/redis/server/battle_engine.
- Nessuna lettura `MONGO_URL`.
- `db_writes=0`, `live_apply_allowed=false`.
- Evidence emessa in `data/design/economy/results/`.
