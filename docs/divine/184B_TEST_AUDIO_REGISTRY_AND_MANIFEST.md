# 184B — Test Audio Registry & Manifest

**Track:** B — Test Audio Registry & Manifest
**Verdict:** `TRACK_B_TEST_AUDIO_REGISTRY_AND_MANIFEST_READY`
**Pack:** `PROJECT_AUDIO_PLACEHOLDER_FOUNDATION`

## Schema metadata (13 required keys)
```
audio_key, mode_id, screen_id, file_path, audio_status,
replace_before_release, final_audio_expected, runtime_attached,
category, duration_target_ms, loop, volume_hint, notes
```

## 12 audio entries

| # | audio_key | mode_id | screen_id | category | duration | loop |
|---|---|---|---|---|---|---|
| 1 | `test_ui_click` | global_ui | any | ui_click | 50ms | ❌ |
| 2 | `test_ui_confirm` | global_ui | any | ui_short | 120ms | ❌ |
| 3 | `test_ui_back_cancel` | global_ui | any | ui_short | 100ms | ❌ |
| 4 | `test_ui_error_locked` | global_ui | any | ui_error | 300ms | ❌ |
| 5 | `test_reward_basic` | global_ui | reward_panel | reward_short | 500ms | ❌ |
| 6 | `test_notification_basic` | global_ui | notification_overlay | notification_short | 250ms | ❌ |
| 7 | `test_mode_enter` | global_ui | any_mode_lobby | mode_transition | 400ms | ❌ |
| 8 | `test_battle_start` | combat | combat_battle | battle_intro | 700ms | ❌ |
| 9 | `test_battle_hit_soft` | combat | combat_battle | battle_hit | 80ms | ❌ |
| 10 | `test_battle_victory_stinger` | combat | combat_victory | victory_stinger | 1500ms | ❌ |
| 11 | `test_battle_defeat_stinger` | combat | combat_defeat | defeat_stinger | 1500ms | ❌ |
| 12 | `test_ambient_placeholder_loop` | global_ui | any_idle_screen | ambient_loop | 4000ms | **✅** |

## Invarianti registry
```
all_replace_before_release_true   = true
all_final_audio_expected_true     = true
all_runtime_attached_false        = true
all_audio_status_test_placeholder = true
loop_entries                      = 1 (ambient only)
```

## Manifest runtime
- Path: `frontend/assets/audio/test_placeholders/manifest.json`
- Format: JSON array di 12 entries
- Field `file` (rel to asset_root) invece di `file_path` (rel to repo)
- Required for runtime attach: **true**
- Loaded by: future runtime loader (NOT YET IMPLEMENTED)

## Categories breakdown
```
ui_click            = 1
ui_short            = 2 (confirm, back)
ui_error            = 1
reward_short        = 1
notification_short  = 1
mode_transition     = 1
battle_intro        = 1
battle_hit          = 1
victory_stinger     = 1
defeat_stinger      = 1
ambient_loop        = 1
```

## Verdict
`TRACK_B_TEST_AUDIO_REGISTRY_AND_MANIFEST_READY` — 12 entries con 13 metadata keys, manifest emesso, schema canonico, zero runtime attach.
