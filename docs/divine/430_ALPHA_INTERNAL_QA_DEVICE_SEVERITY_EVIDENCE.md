# 430 — Alpha Internal QA Device / Severity / Evidence

**Pack:** `MEGA_RELEASE_ACCELERATION_20_v71`

## Device Matrix
- iPhone 12/13/14 (390x844, P0), iPhone 15 Pro (393x852, P1), Samsung Galaxy S21 (360x800, P0), Pixel 7 (412x915, P1), iPad Mini (744x1133, P2).
- Portrait + landscape.

## Severity Matrix
- P0: crash/blocker/security/economy mutation (SLA 4h).
- P1: broken navigation/render blocker (SLA 12h).
- P2: visual/UX mismatch (SLA 48h).
- P3: copy/polish (SLA 168h).
- Classificazioni proibite: reward_grant_required, db_write_required, account_persistence_required (qualunque bug che richieda questi pattern e' violazione di scope).

## Evidence Template
Campi obbligatori: device, os, app_build_commit, route, steps, expected, actual, severity (P0-P3), regression (bool). Campo opzionale: screenshot_or_video.
