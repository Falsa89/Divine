# 315 — Battle Entrypoint Registry Design

Pack: `MEGA_RELEASE_ACCELERATION_MASTER_BATCH_EXECUTION_PLAN_PACK_v54`
Track: B
Tag: `PUBLIC_SYNC_TAG_v54_MEGA_RELEASE_ACCELERATION_MASTER_BATCH_EXECUTION_PLAN`

Design-only registry dei punti di ingresso battaglia.

## Material Raid (registrato in preview)
- frontend_entry_route = `/material-raid-alpha`
- visual_preview_route = `/material-raid-visual-preview`
- reward_preview_route = `/material-raid-reward-preview`
- visual_battle_required = true
- auto_resolve_allowed = false
- reward_claim_enabled = false
- db_writes = 0
- loop_closed = true

## Guild War (design deferito)
- auto_resolve_allowed = true
- replay_link_required = true
- runtime non implementato in v54

## Story / Boss
- runtime locked in v54 (nessun cambio a story.tsx / battle_engine.py / /api/story/battle)

## Vincoli
No `battle_engine.py` changes. No `combat.tsx` changes. No `story.tsx` changes. No `/api/battle/simulate`. No `/api/story/battle`. No runtime wire.
