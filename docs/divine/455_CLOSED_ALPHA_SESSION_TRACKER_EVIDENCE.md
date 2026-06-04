# 455 — Closed Alpha Session Tracker + Evidence Template (v75)

Pack: `MEGA_RELEASE_ACCELERATION_24_v75`

## Session Tracker (15 colonne)

slot_id, tester_nickname, device, os_version, session_start_utc, session_end_utc, flow_first_session_onboarding, flow_training_preview, flow_story_alpha_slice, flow_boss_tower_alpha_loop, flow_event_arena_alpha_preview, flow_alpha_preview_hub, feedback_form_submitted, bug_reports_count, notes.

8 row preparate (slot_01..slot_08).

## Evidence Template (7 campi)

session_id, timestamp_utc, flow_id, step_index, event_type, observation_text, screenshot_url_optional.

Storage: external shared doc. Nessuna persistenza in-app. Nessuna scrittura DB.

`db_writes=0`, `account_persistence=false`, `async_storage_persistence=false`.
