# 99 — PHYSICAL MOBILE QA — v99

> Lingua: Italiano. Politica: NO FAKE QA PASS.

## Stato esecuzione

- Eseguito: **NO**.
- Honest status: **`MANUAL_QA_REQUIRED`**.
- Reason: container Emergent **non ha device fisici** Android/iOS.

## Checklist Android (almeno 13 voci)

1. Install via Google Play Internal Testing
2. Cold start tempo <5s
3. Login guest funziona
4. Session restore dopo killapp
5. Logout pulisce sessione
6. 15 modes (story/arena/guild_war/tower/event/raid/material_raid/training/boss/world_boss/co_op/season/daily/weekend/preview)
7. Combat scene rendering + tap targets >=44dp
8. Live hub QA banners visibili
9. Bot status panel (admin gated)
10. Chat preview classifier (non production)
11. Announcements QA banner
12. Safe area insets su notch + foldable
13. Crash test: kill+restart, low-memory, airplane mode, reconnect

## Checklist iOS (almeno 12 voci)

1. Install via Apple TestFlight
2. Sign in with Apple button visibility (richiesta App Store)
3. Bundle id reale + provisioning
4. Cold start tempo <5s
5. Login guest + Apple
6. Session restore dopo background
7. Logout pulisce KeyChain
8. 15 modes (idem Android)
9. Combat scene rendering + tap targets >=44pt
10. Live hub + bot status + chat preview + announcements
11. Safe area insets + Dynamic Island handling
12. Crash test: kill+restart, low-memory, airplane mode, reconnect

## Google login dev build

Richiede credenziali reali. Status: `BLOCKED_BY_CREDENTIALS`.

## Verdict

`BLOCKER_FOR_CLOSED_ALPHA_PHYSICAL_QA_REQUIRED`
