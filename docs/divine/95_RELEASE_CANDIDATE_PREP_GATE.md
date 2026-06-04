# 95 — Release Candidate Prep Gate

## Pack

`MEGA_RELEASE_ACCELERATION_44_v95`

## Gate per categoria

| Categoria             | Stato       | Note |
|-----------------------|-------------|------|
| battle_engine         | READY       | Runtime patch applicata, 21/21 regression PASS |
| reward_safety         | READY       | Canary sandbox isolata, 0 live reward |
| live_guild            | READY       | Tutti i score gated, ranking blocked |
| formation             | CONDITIONAL | /api/team/get-formation non esposto → BLOCKER_FOR_RELEASE_CANDIDATE |
| readonly_endpoints    | READY       | 4 endpoint v95 attivi, smoke PASS |
| mode_playability      | READY       | Lobby + catalog source attivi |
| live_announcements    | READY       | Sandbox attiva, no production broadcast |
| mobile_qa             | CONDITIONAL | Pieno run su device fisici Android/iOS richiesto |
| performance           | CONDITIONAL | Load/locust scenari engine v95 mancanti |
| known_issues          | CONDITIONAL | Expo ENOSPC / Redis / GitHub stale push (caveat ambientali, 20 OPTIONAL FAIL atteso) |
| store_readiness       | BLOCKED     | Art/audio/store/compliance/monetization fuori scope |

## Verdict complessivo

`RC_PREP_PARTIAL_READY_BLOCKERS_DOCUMENTED`

## Blocker per v96 (Release Candidate Final)

1. Esporre `/api/team/get-formation`.
2. Pieno run mobile QA Android/iOS.
3. Load/locust su scenari engine v95.
4. Caveat ambientali (Expo File Watcher ENOSPC + Redis + GitHub) → opzionali.
5. Art/audio/store/compliance/monetization (fuori scope v95).
