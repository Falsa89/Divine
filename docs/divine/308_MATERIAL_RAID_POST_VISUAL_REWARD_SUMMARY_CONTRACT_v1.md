# 308 — Material Raid Post-Visual Reward Summary Contract v1

**Pack**: `MEGA_RELEASE_ACCELERATION_3_MATERIAL_RAID_POST_VISUAL_REWARD_SUMMARY_AND_ALPHA_LOOP_CLOSURE_PACK_v53`
**Track**: A
**Public Sync Tag**: `PUBLIC_SYNC_TAG_v53_MEGA_RELEASE_ACCELERATION_3_MATERIAL_RAID_ALPHA_LOOP_CLOSURE`
**Contract**: `material_raid_post_visual_reward_summary_contract_v1`

## Scopo
Definire il contratto deterministico tra `/material-raid-visual-preview` e
`/material-raid-reward-preview`, attraverso il backend
`POST /api/material-raid/alpha-reward-summary-preview`.

## Query params richiesti
`track_id`, `stage_id`, `battle_seed_preview`, `battle_result_preview`, `mvp_hero_id`.

## Required backend response fields
`status`, `track_id`, `stage_id`, `reward_preview`, `materials_granted`,
`inventory_mutation`, `claim_button_enabled`, `claim_flow_state`, `db_writes`,
`result_authoritative`, `reward_claim_enabled`, `reward_grant_enabled`,
`compatible_with_future_material_raid_claim_safety`, `next_allowed_action`,
`source_visual_preview_supported`.

## Garanzie hard
- `result_authoritative=false`, `reward_claim_enabled=false`, `reward_grant_enabled=false`
- `claim_button_enabled=false`, `materials_granted=false`, `inventory_mutation=false`
- `db_writes=0`, `real_db_writes=0`
- `battle_engine_runtime_used=false`, `battle_engine_py_changed=false`
- `compatible_with_future_material_raid_claim_safety=true`

## Aggiunte append-only nel payload backend
- `source_visual_preview_supported`, `result_authoritative`, `reward_claim_enabled`,
  `reward_grant_enabled`, `battle_engine_runtime_used`, `next_allowed_action`,
  `target_frontend_route`.

Path / flag / default 503 / status / reward table invariati.
