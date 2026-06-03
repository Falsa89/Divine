# 376 — Dry-Run Request/Response Contract (target v64)

Pack: `MEGA_RELEASE_ACCELERATION_12_MATERIAL_RAID_CLAIM_SAFETY_AND_STAGING_BLUEPRINT_SUPER_PACK_v63`

## Request fields

`user_id`, `server_id`, `material_raid_run_id`, `idempotency_key`,
`reward_preview_payload`, `payload_hash`, `reward_hash`, `dry_run_nonce`.

## Response fields

`dry_run_status`, `would_create_ledger`, `would_grant_rewards`,
`duplicate_status`, `rollback_token_preview`, `observation_window_ref`, `errors`.

## Invarianti

- `dry_run_only=true`, `live_apply_allowed=false`
- `db_writes=0`, `future_v64_target=true`
- `would_grant_rewards` sempre `false` nel layer dry-run
