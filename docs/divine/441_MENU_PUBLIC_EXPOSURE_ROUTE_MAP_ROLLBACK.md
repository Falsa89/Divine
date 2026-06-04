# 441 — Menu Public Exposure Route Map e Rollback Runbook (v73)

Pack: `MEGA_RELEASE_ACCELERATION_22_v73`

## Route map (7 candidate)

1. `alpha-preview-hub`
2. `first-session-onboarding-preview`
3. `training-combat-onboarding-preview`
4. `story-alpha-slice-preview`
5. `boss-tower-alpha-loop-preview`
6. `event-arena-alpha-gate-preview`
7. `event-arena-first-alpha-slice-preview`

Tutte deeplink-only oggi. Target section: `alpha_preview_section` (NON home root, NON tab bar).

## Rollback runbook (max 5 step)

1. flag_disable -> `public_menu_exposure_enabled=false`
2. remove_section_entry da menu component
3. keep_deeplinks (verifica file presence)
4. verify_md5_invariants 8/8
5. validator_suite_replay con 0 REQUIRED FAIL

Data loss su rollback: **NO**.

## Observation plan

- Window: 60 minuti
- Rollback trigger: qualsiasi P0 fail oppure >=2 P1 fail
