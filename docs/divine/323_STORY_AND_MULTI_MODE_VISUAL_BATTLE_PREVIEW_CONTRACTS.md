# 323 — Story and Multi-Mode Visual Battle Preview Contracts

Pack: `MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW_PACK_v55`
Track: D
Tag: `PUBLIC_SYNC_TAG_v55_MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW`

Contratti **design-only** per Story / Boss / Tower / Event / Arena.

## Story contract
- runtime_wired = false
- story_tsx_changed = false
- story_battle_endpoint_changed = false
- payload futuro minimo: mode, chapter_id, stage_id, battle_seed_preview, team_power, recommended_power, enemy_family_preview, target_frontend_route, invariants di preview

## Multi-mode contract (boss / tower / event / arena)
Per ognuno: `runtime_wiring_deferred = true`, future_payload_minimum con chiavi specifiche (`boss_id`, `floor_id`, `event_id`, `match_id`), tutte le invariants preview.

## Vincoli
No `story.tsx`. No `/api/story/battle`. No `/api/battle/simulate`. No `combat.tsx`. No `battle_engine.py`. No nuovi runtime endpoint in v55.
