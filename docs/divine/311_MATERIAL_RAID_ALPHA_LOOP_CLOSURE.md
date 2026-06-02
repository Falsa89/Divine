# 311 — Material Raid Alpha Loop Closure

**Pack**: `MEGA_RELEASE_ACCELERATION_3_MATERIAL_RAID_POST_VISUAL_REWARD_SUMMARY_AND_ALPHA_LOOP_CLOSURE_PACK_v53`
**Tracks**: E + F
**Public Sync Tag**: `PUBLIC_SYNC_TAG_v53_MEGA_RELEASE_ACCELERATION_3_MATERIAL_RAID_ALPHA_LOOP_CLOSURE`

## Loop chiuso (5 step)
1. `/material-raid-alpha`
2. `POST /api/material-raid/alpha-battle-preview`
3. `/material-raid-visual-preview`
4. `/material-raid-reward-preview`
5. ritorno a `/material-raid-alpha`

## Garanzie per ciascun step
- `preview_only=true`, `db_writes=0`, `reward_grant_enabled=false`.
- Step backend: `result_authoritative=false`, `battle_engine_runtime_used=false`.
- Nessun home menu mandatory: tutti deeplink-only.

## QA Smoke Matrix (13 flussi)
P0/P1/P2/P3: alpha_open, prepare_battle, open_visual_preview, visual_preview_missing,
open_reward_preview, reward_preview_backend_off, reward_preview_backend_on,
no_claim_button, return_to_alpha, locked_track_no_loop, underpowered_no_loop,
mobile_rotation_layout, no_db_write_no_grant.
