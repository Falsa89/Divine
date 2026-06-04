# 447 — Menu Public Exposure Apply Controlled (v74)

Pack: `MEGA_RELEASE_ACCELERATION_23_v74`

## Apply mode

- mode: `controlled_alpha_preview_section_only`
- strategy: `new_screen_alpha_menu_preview_tsx`
- screen: `frontend/app/alpha-menu-preview.tsx`

## Cosa cambia

- Nuovo screen `alpha-menu-preview.tsx` accessibile via route/deeplink
- Sezione "Alpha Preview Menu" controllata che mostra 7 preview con badge `ALPHA_MENU_EXPOSED`
- Home `/index.tsx`, tab bar e routing pubblico produzione: **invariati**

## Cosa NON cambia

- home_root_changed: false
- tab_bar_changed: false
- production_navigation_changed: false
- public_menu_routing_enabled: false
- home_menu_routing_enabled: false
- db_writes: 0
- reward_grant: false
- permanent_progress: false
- account_persistence: false
- async_storage_persistence: false
- backend_route_changed: false
- server_py / battle_engine / story.tsx / combat.tsx: tutti **invariati** (MD5 verified)
- nessun import da story/combat
- nessun fetch backend, nessun AsyncStorage
- nessun real asset import / resolver runtime change
- nessuna release commerciale ampia

## Route esposte (7)

1. alpha-preview-hub
2. first-session-onboarding-preview
3. training-combat-onboarding-preview
4. story-alpha-slice-preview
5. boss-tower-alpha-loop-preview
6. event-arena-alpha-gate-preview
7. event-arena-first-alpha-slice-preview

## Verdict

`APPLIED_CONTROLLED_SAFE`
