# 182E — Test Asset/Audio Registry (Schema + Initial Inventory)

**Track:** E — Test Asset/Audio Registry Design
**Verdict:** `TRACK_E_TEST_ASSET_AUDIO_REGISTRY_READY`
**Pack:** `PROJECT_FULL_RUNTIME_FEATURE_REALITY_AUDIT_WITH_TEST_ASSET_REGISTRY`

## Nuova regola canonica
Per ogni modalità/screen/audio/VFX senza final assets:
- implementazione può usare placeholder funzionali;
- ogni placeholder DEVE essere esplicitamente registrato come TEST;
- audit successivi devono poter trovarli;
- final release NON può contenere placeholder non ricontrollati.

## Schema Registry

### Required metadata (7 keys)
```
mode_id
screen_id
asset_key
asset_status
audio_key
audio_status
replace_before_release
```

### Optional metadata
`final_asset_expected`, `final_audio_expected`, `owner_system`, `notes`, `user_sketch_provided`, `user_sketch_path`, `sketch_required_for_next_stage`, `created_at_utc`, `last_audit_utc`, `placeholder_naming_convention`.

### Allowed statuses (6)
- `test_placeholder`
- `placeholder_dev`
- `missing_final_asset`
- `missing_final_audio`
- `final_ready`
- `not_required`

### Placeholder naming convention
`test_<mode_id>_<screen_id>_<purpose>` — esempi:
- `test_guild_war_lobby_background`
- `test_combat_victory_jingle`
- `test_tower_floor_select_panel_bg`
- `test_story_chapter1_intro_voice`

### Audit queries design
- Find all `replace_before_release == true` — elenco completo prima di RELEASE_TAG_v1
- Find all `asset_status == 'test_placeholder'` OR `audio_status == 'test_placeholder'`
- Find missing finals: `asset_status IN ('missing_final_asset', 'missing_final_audio')`
- Find unsketched complex modes: `sketch_required_for_next_stage == true AND user_sketch_provided == false`

### Final release blocker rules
1. Any entry with `replace_before_release=true` blocks `RELEASE_TAG_v1`.
2. Any benchmark canonical mode senza placeholder registrato OR `final_ready` blocca `RELEASE_TAG_v1`.
3. Any mode con `sketch_required_for_next_stage=true && user_sketch_provided=false` blocca `NEXT_STAGE_TAG`.

## User sketch policy
- Sketches **opzionali globalmente**
- Sketches **raccomandati** per: guild_war, war_three_thrones, housing, tower, world_boss, guild_raid, sanctuary, event_hub, live multi-panel modes, territory_map
- **Non bloccanti** per l'audit

## Asset categories
background, panel_bg, icon, button, banner, hero_portrait, vfx_overlay, status_icon, map_tile, cutscene_still, loading_screen

## Audio categories
ambient_loop, bgm_track, sfx_short, voice_line, jingle, ui_click, battle_hit, victory_fanfare, defeat_sting

## Storage layout design
- Placeholder assets: `frontend/assets/test_placeholders/<mode_id>/<screen_id>/`
- Placeholder audio: `frontend/assets/test_placeholders_audio/<mode_id>/<screen_id>/`
- Registry: `data/design/runtime_audit/test_asset_audio_registry_initial_inventory_v1.json` (+ delta files futuri)

---

## Initial Inventory — 20 entries registrate

### Distribuzione status
```
asset_status:
  test_placeholder       = 1
  placeholder_dev        = 8
  missing_final_asset    = 11
  final_ready            = 0

audio_status:
  test_placeholder       = 0
  placeholder_dev        = 0
  missing_final_audio    = 16
  not_required           = 4
```

### Counts
- **Total entries:** 20
- **Replace before release count:** 20 (tutte)
- **Sketch required count:** 8
- **Sketch provided count:** 0

### Entries highlight (full list nel JSON)
| Mode | Screen | Asset | Audio | Sketch needed? |
|---|---|---|---|---|
| home | home_main | placeholder | missing | no |
| combat | combat_battle | placeholder_dev | missing | no |
| combat | combat_victory | placeholder_dev | missing | no |
| gacha | gacha_main | placeholder_dev | missing | no |
| story | story_chapter_select | missing | missing | no |
| guild_war | guild_war_lobby | missing | missing | **✅ yes** |
| war_three_thrones | territory_map | missing | missing | **✅ yes** |
| tower | tower_floor_select | missing | missing | **✅ yes** |
| world_boss | world_boss_lobby | missing | missing | **✅ yes** |
| guild_raid | guild_raid_lobby | missing | missing | **✅ yes** |
| housing | housing_main | missing | missing | **✅ yes** |
| sanctuary | sanctuary_main | missing | missing | **✅ yes** |
| event_hub | event_hub_main | missing | missing | **✅ yes** |
| daily_guide | daily_hub | placeholder_dev | missing | no |
| arena_pvp | pvp_main | missing | missing | no |
| shop | shop_main | placeholder_dev | not_required | no |
| battle_pass | battlepass_main | placeholder_dev | not_required | no |
| vip | vip_main | placeholder_dev | not_required | no |
| global_ui | navigation_tabs | placeholder_dev | missing | no |
| global_ui | loading_screen | missing | not_required | no |

## Verdict
`TRACK_E_TEST_ASSET_AUDIO_REGISTRY_READY` — Schema canonico + 20 entries initial inventory. Zero asset finali aggiunti. Zero DB writes. Future audit queries definite.
