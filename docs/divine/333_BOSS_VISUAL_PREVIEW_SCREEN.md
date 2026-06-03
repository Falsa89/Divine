# 333 — Boss Visual Preview Screen

Pack: `MEGA_RELEASE_ACCELERATION_6_BOSS_VISUAL_PREVIEW_ROUTE_PACK_v57`
Track: B
Tag: `PUBLIC_SYNC_TAG_v57_MEGA_RELEASE_ACCELERATION_6_BOSS_VISUAL_PREVIEW_ROUTE`

Nuova schermata `/boss-visual-preview` deeplink-only.

## Caratteristiche
- statica / local
- nessun backend, nessun battle_engine
- nessun claim button, nessun reward, nessuna mutation
- nessun Reanimated, nessun import di `combat.tsx`
- nessun home menu mandatory routing
- testo italiano

## Query params accettati (tutti opzionali)
`boss_family_id`, `boss_display_name`, `boss_phase_preview`, `battle_seed_preview`, `team_power`, `recommended_power`

## Default fallback (se params mancanti)
- `boss_family_id = training_boss_preview`
- `boss_display_name = Boss Preview`
- `boss_phase_preview = phase_1`
- `battle_seed_preview = boss-alpha-v57`

## UI elementi
- titolo "Boss Visual Preview"
- boss card (display_name + family_id)
- phase preview
- weakness hint preview
- enrage hint preview
- team power vs recommended
- 2 warning italiani: "Preview visuale boss non autoritativa", "Nessun reward verrà assegnato"
- guardrails visibili (result_authoritative=false, db_writes=0, battle_engine_runtime_used=false, backend_used=false)
- pulsanti sicuri: apri router generico, reset preview, indietro
