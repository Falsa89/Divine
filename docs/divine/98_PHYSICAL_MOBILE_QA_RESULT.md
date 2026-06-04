# 98 — Physical Mobile QA Result

## Pack

`MEGA_RELEASE_ACCELERATION_47_v98`

## Stato

**`MANUAL_QA_REQUIRED`** — device fisici non disponibili in container Emergent. No fake pass.

## Local smoke verified (in container)

- ✓ auth_session (guest/google/apple sandbox)
- ✓ refresh_rotation
- ✓ data_export
- ✓ privacy_status
- ✓ hard_delete_disabled (response corretta)
- ✓ formation_fetch authenticated
- ✓ battle_engine_smoke: 21/21 PASS
- ✓ 15_modes design ready
- ✓ live_guild_qa
- ✓ live_announcements_sandbox
- ✓ bot_status_endpoint

## Manual QA checklist Android (richiesta)

1. Build dev su device fisico Android (API 26+).
2. Login guest + refresh rotation + logout-all.
3. Delete account request (soft) → privacy-status → data-export.
4. Formation fetch authenticated.
5. 15 modes smoke (story/tower/arena/training/raid/event/guild_live/guild_war/guild_raid/world_boss/faction_boss/territory/crepuscolo_titani/assalto_ragnarok/summer_invasion).
6. Battle engine smoke.
7. Live/Guild QA Hub.
8. Live Announcements QA sandbox.
9. Bot admin status (read-only).
10. Hard-delete-confirm → response DISABLED.
11. Performance low-memory device.

## Manual QA checklist iOS

- Tutti i punti Android +
- Sign in with Apple button visible (iOS-only).
- Background/foreground transitions.
- TestFlight upload.

## Closed alpha blocker

**SÌ** — physical device run obbligatorio.
