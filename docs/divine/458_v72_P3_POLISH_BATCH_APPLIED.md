# 458 — v72 P3 Polish Batch Applied (v75)

Pack: `MEGA_RELEASE_ACCELERATION_24_v75`

## 3 micro-patch applicate

### P3.1 — alpha-preview-hub copy shortening
- file: `frontend/app/alpha-preview-hub.tsx`
- patch_type: copy_shortening
- Banner sub copy ora: "Mappa locale anteprime alpha. No routing pubblico, no reward, no writes."
- behavior/routing/fetch/db/reward/battle_engine/story-combat-import change: tutti `false`

### P3.2 — first-session state label line-height/margin
- file: `frontend/app/first-session-onboarding-preview.tsx`
- patch_type: style_line_height_margin
- stateMachineLabel: marginTop 4->6, marginBottom 4->6, lineHeight 14 added. Pure style.
- behavior/routing/fetch/db/reward/battle_engine/story-combat-import change: tutti `false`

### P3.3 — alpha-preview-hub QA priority ordering
- file: `frontend/app/alpha-preview-hub.tsx`
- patch_type: qa_priority_ordering
- ENTRIES ora ordinate con P0 (first-session-onboarding-preview) in prima posizione.
- behavior/routing/fetch/db/reward/battle_engine/story-combat-import change: tutti `false`

## Riepilogo

- micro_patches_count: 3
- micro_patches_applied_count: 3
- files_modified_count: 2
- alpha_menu_preview_modified: false
- all_patches_safe: true
- ts_clean_on_patched_files: true
- static_scan_no_forbidden_patterns: true
- md5_invariants_unchanged: true
- db_writes: 0
- deferred_findings_count: 0
- backlog_cleared: true
