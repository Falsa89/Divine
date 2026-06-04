# 408 — Boss + Tower Alpha Loop Contracts

**Pack:** `MEGA_RELEASE_ACCELERATION_17_STORY_PLAYABLE_ALPHA_AND_BOSS_TOWER_ALPHA_LOOP_SUPER_PACK_v68`

## Contratti
- `data/design/modes/boss_tower_alpha_loop_contract_v1.json`
- `data/design/modes/boss_alpha_loop_preview_fixture_v1.json`
- `data/design/modes/tower_alpha_loop_preview_fixture_v1.json`
- `data/design/modes/boss_tower_alpha_loop_forbidden_scope_v1.json`

## Boss fixture
- `mode = boss`
- `boss_family_preview = family_alpha_titan_preview`
- `boss_phase_preview` con 3 fasi
- `enrage_hint_preview` non autoritativo
- `weakness_hint_preview` non autoritativo
- 7 step deterministici di timeline preview
- result preview senza reward

## Tower fixture
- `mode = tower`
- `tower_id = tower_alpha_preview`
- `floor_id = floor_alpha_001`
- `floor_number_preview = 1`
- `modifier_hint_preview` non autoritativo
- `enemy_family_preview = family_alpha_construct_preview`
- 6 step deterministici di timeline preview
- result preview senza reward

## Guardrail comuni
- `db_writes = 0`
- `backend_used = false`
- `battle_engine_runtime_used = false`
- `leaderboard_writes = false`
- `ranking_writes = false`
- `reward_grant_enabled = false`
- `permanent_progress_enabled = false`
- `inventory_mutation = false`
- `wallet_mutation = false`
