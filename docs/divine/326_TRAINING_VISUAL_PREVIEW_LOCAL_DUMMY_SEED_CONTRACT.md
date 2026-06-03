# 326 — Training Visual Preview Local Dummy Seed Contract

Pack: `MEGA_RELEASE_ACCELERATION_5_TRAINING_VISUAL_PREVIEW_LOCAL_DUMMY_SEED_WIRING_PACK_v56`
Track: A
Tag: `PUBLIC_SYNC_TAG_v56_MEGA_RELEASE_ACCELERATION_5_TRAINING_VISUAL_PREVIEW_LOCAL_DUMMY_SEED`

Contratto del wiring locale (dummy seed) per Training Visual Preview.

## Transizione
- `previous_state = preview_shell_v55`
- `target_state = local_dummy_seed_wired_v56`
- `seed = training-alpha-v56`
- timeline_steps_min/max = 5..7
- `source_route = /training-visual-preview`
- `router_route = /visual-battle-preview-router`

## Vincoli (tutti enforced dal validator)
- `local_only = true`
- `backend_used = false`
- `battle_engine_runtime_used = false`
- `result_authoritative = false`
- `reward_claim_enabled = false`
- `reward_grant_enabled = false`
- `db_writes = 0`
- `no_inventory_mutation = true`
- `no_wallet_mutation = true`
- no `Reanimated`, no import di `combat.tsx`
