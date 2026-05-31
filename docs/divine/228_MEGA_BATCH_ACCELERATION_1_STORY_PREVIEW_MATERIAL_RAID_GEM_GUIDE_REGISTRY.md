# 228 — MEGA_BATCH_ACCELERATION_1 STORY PREVIEW + MATERIAL RAID GEM + GUIDE + REGISTRY

## Tracks

- **Track A** (PHASE_2): endpoint preview `/api/story/battle-instance-preview/*` con flag `STORY_BATTLE_INSTANCE_PREVIEW_ENABLED`. Default 503. Doc 224.
- **Track B**: `gem_material_raid` passa a `open_preview` con reward preview gem I–V. Doc 225.
- **Track C**: registry v4 esteso con arena/world_boss/dungeon/campaign_elite/resource_raid/guild_boss. Doc 226.
- **Track D**: 9 topic guida/codex (Story Visual Battle, Replay/Save/Share, Gear, Gemme, Rune, Material Raid, Artifact, Divine Weapon, Guild War). Doc 227.

## Garanzie globali

- DB writes = 0
- story_runtime_conversion = false
- battle_engine UNCHANGED
- combat.tsx UNCHANGED, story.tsx UNCHANGED, homeAssetsManifest.ts UNCHANGED
- `/api/story/battle` UNCHANGED, `/api/battle/simulate` UNCHANGED
- reward/EXP/story progress/economy/gacha/BP/VIP/shop UNCHANGED
- Material Raid live claim disabilitato (preview-only)
- Gem Socket commit disabilitato
- Rune/Artifact/Divine Weapon/Guild War runtime UNCHANGED
- Character Bible/final_numbers UNTOUCHED

## Suite runner

Strategia forte (v29d): blocco diagnostico in cima + tuple OPTIONAL vicino all'inizio + tuple count = 1 per ciascuna:

- PROJECT-STORY-BATTLE-INSTANCE-PREVIEW-ENDPOINT
- PROJECT-MATERIAL-RAID-GEM-TRACK-PREVIEW-UNLOCK
- PROJECT-MODE-BATTLE-ENTRYPOINT-REGISTRY-EXPANSION
- PROJECT-GUIDE-CODEX-FILL-GAPS
- MEGA-BATCH-ACCELERATION-1-ROLLUP

Sentinel: `PUBLIC_SYNC_TAG_v31_MEGA_BATCH_ACCELERATION_1`, `MEGA_BATCH_ACCELERATION_1_REGISTRATION_SENTINEL`.
