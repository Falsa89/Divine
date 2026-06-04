# 93 — Live Announcements QA and Dynamic Feed (v93)

## Pack
`MEGA_RELEASE_ACCELERATION_42_PLAYABILITY_COMPLETION_SUPERPACK_v93`

## Scopo
Testare in QA gli annunci live statici e dinamici senza broadcast in produzione, senza push notification live, senza PII reali.

## Annunci statici (4)
- `news`
- `maintenance`
- `event_notice`
- `update_note`

Catalogo: `data/design/live_announcements/live_announcement_qa_catalog_v1.json`

## Annunci dinamici (9)
- `six_star_pull`
- `native_six_star_star_up`
- `arena_top3_change`
- `live_event_kill`
- `live_event_kill_streak`
- `global_ranking_change`
- `top_player_online`
- `guild_boss_milestone`
- `community_prestige_event`

Regole: `data/design/live_announcements/live_announcement_dynamic_event_rules_v1.json`

## Canali
`global`, `system`, `events`, `arena`, `guild`, `community`.

## Anti-spam
- max_per_user_per_minute: 3
- max_per_channel_per_minute: 30
- global_burst_cap: 100
- dedupe_window_seconds: 60
- throttle_strategy: token_bucket

## Visibility rules
Ogni tipo dichiara un `default_visibility` / `min_visibility_threshold` (es. arena_top3_change → arena_channel; top_player_online → top_50).

## Privacy / alias safety
- `alias_format`: `qa_alias_{number}`
- vietato emettere: real user id, real user name, email, IP.
- Tutti i template usano `{alias}` / `{alias_a}` / `{guild_alias}` / `{boss_alias}` / `{target_alias}`.

## UI
Schermata: `frontend/app/live-announcements-qa.tsx`
- lista annunci QA (statici)
- simulatore evento dinamico (drop-down + bottone Genera Test Event)
- ticker/banner/feed preview
- filtri anti-spam visibili
- visibility channel selector
- privacy/safety note
- bandiera 'QA SIMULATION ONLY — NO PRODUCTION BROADCAST'

## Safety
- `production_broadcast`: false
- `push_notification_live`: false
- `real_user_data_required`: false
- `privacy_safe_alias_only`: true
- `anti_spam_rules_present`: true
- `qa_simulation_only`: true
- `db_writes`: 0
