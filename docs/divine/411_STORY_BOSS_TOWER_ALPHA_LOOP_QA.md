# 411 — Story / Boss / Tower Alpha Loop QA

**Pack:** `MEGA_RELEASE_ACCELERATION_17_STORY_PLAYABLE_ALPHA_AND_BOSS_TOWER_ALPHA_LOOP_SUPER_PACK_v68`

## QA Matrix
- File: `data/design/qa/story_boss_tower_alpha_loop_qa_matrix_v1.json`
- Severita': P0 / P1 / P2 / P3.
- 22 casi che coprono: prerequisiti v67, contratti Story/Boss/Tower, screen, mini-loop, boundaries result/reward/progress, isolamento (no backend, no story.tsx/combat.tsx, no battle_engine, no `/api/story/battle`, no `/api/battle/simulate`), reward grant, permanent progress, db writes, MD5, layout mobile, rotation, autoplay cleanup, reset, docs e validators.

## Progress Report v12
- File: `data/design/release_acceleration/alpha_loop_progress_report_v12.json`
- `story_first_playable_alpha_slice = preview_ready_v68`
- `boss_alpha_loop = preview_ready_v68`
- `tower_alpha_loop = preview_ready_v68`
- `reward_grant = false`
- `permanent_progress = false`
- `db_writes = 0`
- `battle_engine_runtime = false`
- Next recommended: `training_combat_onboarding_super_pack`, `event_arena_alpha_gate_super_pack`, `hero_asset_dryrun_manifest_super_pack`.
- Not approved: story permanent progress, boss/tower reward grant, battle_engine runtime, db writes, backend route enablement, ranking/leaderboard.
