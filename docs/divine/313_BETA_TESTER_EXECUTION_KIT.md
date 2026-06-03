# 313 — Beta Tester Execution Kit

Pack: `MEGA_RELEASE_ACCELERATION_MASTER_BATCH_EXECUTION_PLAN_PACK_v54`
Track: D
Tag: `PUBLIC_SYNC_TAG_v54_MEGA_RELEASE_ACCELERATION_MASTER_BATCH_EXECUTION_PLAN`

Kit operativo (docs-only) per i beta tester della alpha v54.

## Onboarding
- Iscrizione tramite link beta (placeholder).
- Login via email magic link, mai condividere password.
- Distribuzione build: Expo Go QR code o canale interno TestFlight / Internal Track.

## Device matrix
- **iOS 16+**: iPhone 13, iPhone 14 Pro, iPhone SE 3
- **Android 11+**: Pixel 6, Samsung Galaxy S22, Xiaomi Redmi Note 11

## Sessioni consigliate
- 30 min → Material Raid Alpha loop + smoke navigazione
- 60 min → Material Raid + Heroes browse + Codex
- 90 min → Full smoke matrix + bug hunting

## Severity
- **P0**: crash / data loss / app inutilizzabile
- **P1**: feature principale rotta, nessun workaround
- **P2**: feature degradata con workaround
- **P3**: polish / copy / UI minore

## Bug template (campi)
title, severity, reproduction_steps, expected, actual, device, os_version, app_version, screenshot_or_video_url, log_excerpt, frequency

## Evidence
- Screenshot **obbligatorio**
- Video **per P0/P1**
- Log console **se riproducibile**

## Daily smoke checklist
Cold start, login, home, Material Raid Alpha, alpha_battle_preview, Visual Preview, Reward Summary Preview, ritorno ad Alpha, scroll heroes, hero detail, story (no battle), navigation back/forward, rotation, 60s idle no crash, background/foreground resume.

## Focus areas
material_raid_loop, visual_preview, reward_preview, story, heroes, navigation, rotation, performance, crash.

No DB writes. No reward grant. No inventory mutation.
