# 321 — Generic Visual Battle Preview Router Shell

Pack: `MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW_PACK_v55`
Track: B
Tag: `PUBLIC_SYNC_TAG_v55_MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW`

Nuova schermata **deeplink-only** `/visual-battle-preview-router`.

## Caratteristiche
- nessun home menu wiring
- nessuna chiamata backend
- nessun battle_engine
- nessun /api/battle/simulate
- nessun /api/story/battle
- nessun claim button
- nessuna mutation
- testo italiano

## Query params accettati
`mode`, `source_route`, `track_id`, `stage_id`, `chapter_id`, `battle_seed_preview`, `team_power`, `recommended_power`, `enemy_family_preview`

## Comportamento
- non crasha se i param mancano (mostra fallback messaging)
- visualizza modalità, source route, seed preview, team vs recommended power
- griglia 3x3 placeholder
- 3 warning visibili in italiano: preview non autoritativa, nessun reward assegnato, routing preview only
