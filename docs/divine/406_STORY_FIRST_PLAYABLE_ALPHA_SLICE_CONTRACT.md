# 406 — Story First Playable Alpha Slice Contract

**Pack:** `MEGA_RELEASE_ACCELERATION_17_STORY_PLAYABLE_ALPHA_AND_BOSS_TOWER_ALPHA_LOOP_SUPER_PACK_v68`

## Scopo
Definisce il contratto per la prima alpha slice giocabile di Story, ottenuta concatenando i 3 nodi alpha (001/002/003) gia' previsti dal runtime adapter v67 in un mini-loop lato client.

## Pattern di sicurezza
- `alpha_slice_preview = true`
- `authoritative_runtime = false`
- `backend_used = false`
- `battle_engine_runtime_used = false`
- `api_story_battle_changed = false`
- `api_battle_simulate_changed = false`
- `story_tsx_changed = false`
- `combat_tsx_changed = false`
- `db_writes = 0`
- `reward_grant_enabled = false`
- `permanent_progress_enabled = false`
- `result_authoritative = false`
- `local_preview_adapter = true`

## Sequenza nodi
- `chapter_id = chapter_alpha`
- `story_alpha_node_001` -> `story_alpha_node_002` -> `story_alpha_node_003`
- `clear_sequence_preview_only = true`
- `chapter_complete_preview_only = true`

## Reward / Progress
- `reward_preview_not_granted = true`
- `progress_preview_not_persisted = true`
- Nessun mail reward.
- Nessun avanzamento Battle Pass.
- Nessun avanzamento achievement.
- Nessun avanzamento daily quest.

## File
- `data/design/story/story_first_playable_alpha_slice_contract_v1.json`
- `data/design/story/story_alpha_chapter_001_sequence_contract_v1.json`
- `data/design/story/story_alpha_slice_forbidden_scope_v1.json`
