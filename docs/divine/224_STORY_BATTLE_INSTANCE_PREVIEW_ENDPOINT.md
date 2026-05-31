# 224 — STORY BATTLE INSTANCE PREVIEW ENDPOINT (MEGA_BATCH_ACCELERATION_1 TRACK A)

PHASE_2 endpoint preview-only/gated per la creazione di payload `battle_instance_id` Story.

## Flag

`STORY_BATTLE_INSTANCE_PREVIEW_ENABLED` (default off → 503 inert envelope).

## Endpoints

- `GET /api/story/battle-instance-preview/config`
- `POST /api/story/battle-instance-preview/create-preview`
- `POST /api/story/battle-instance-preview/validate-payload`
- `GET /api/story/battle-instance-preview/sample`

## Garanzie

- DB writes = 0
- reward_grant_enabled = false
- exp_grant_enabled = false
- story_progress_enabled = false
- visual_runtime_enabled = false
- story.tsx UNCHANGED, combat.tsx UNCHANGED, battle_engine UNCHANGED
- /api/story/battle UNCHANGED, /api/battle/simulate UNCHANGED
