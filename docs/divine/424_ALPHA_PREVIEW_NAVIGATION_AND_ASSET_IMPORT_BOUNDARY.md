# 424 — Alpha Preview Navigation + Deferred Asset Import Boundary

**Pack:** `MEGA_RELEASE_ACCELERATION_19_v70`

## File
- `data/design/release_acceleration/first_session_event_arena_alpha_navigation_boundary_v1.json`
- `data/design/release_acceleration/alpha_preview_navigation_map_v1.json`
- `data/design/release_acceleration/v70_deferred_asset_import_gate_v1.json`

## Navigation Boundary
- `preview_navigation_only = true`
- `public_menu_routing_enabled = false`
- `deep_link_only = true`
- `account_mutation = false`, `db_writes = 0`, `reward_grant = false`

## Navigation map (safe links)
training-combat-onboarding-preview, story-alpha-slice-preview, boss-tower-alpha-loop-preview, event-arena-alpha-gate-preview, event-arena-first-alpha-slice-preview, first-session-onboarding-preview.

## Deferred Asset Import Gate
- `asset_staging_import_deferred = true`
- `requires_real_asset_pack_before_import = true`
- `real_asset_import = false`, `file_copy_enabled = false`, `runtime_asset_resolver_changed = false`, `character_bible_changed = false`, `hero_roster_changed = false`
- Manual approval obbligatoria.
