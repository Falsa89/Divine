# 373 — Material Raid Idempotency + Replay Policy

Pack: `MEGA_RELEASE_ACCELERATION_12_MATERIAL_RAID_CLAIM_SAFETY_AND_STAGING_BLUEPRINT_SUPER_PACK_v63`

## Key components (idempotency key)

`user_id : server_id : material_raid_run_id : mode_id : reward_table_version :
preview_session_id : claim_attempt_nonce`

Hashing: sha256 sulla forma normalizzata.

## Statuses

`preview_only`, `staged_pending`, `staged_committed`,
`duplicate_same_payload`, `duplicate_conflict`, `rollback_required`, `rejected`.

## Replay decision table

| Segnale | Decisione |
|---|---|
| same key, same payload | duplicate_same_payload |
| same key, diff payload | duplicate_conflict |
| diff key, same payload (short window) | duplicate_conflict |
| nonce reuse | rejected |

Nessun DB write nel layer preview.
