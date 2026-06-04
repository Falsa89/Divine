# 416 — Event + Arena Alpha Gate Preview UI

**Pack:** `MEGA_RELEASE_ACCELERATION_18_v69`

## Screen
- `frontend/app/event-arena-alpha-gate-preview.tsx` (nuova, deeplink-only).

## Comportamento
- Due card: Event Alpha Gate + Arena Alpha Gate.
- Required gates checklist per ciascuna card.
- Disabled state visibili per rewards/ranking/currency.
- Pannello guardrail con `db_writes=0`, `reward_grant_enabled=false`, `arena_ranking_enabled=false`, `event_currency_enabled=false`, `matchmaking_live=false`, `public_pvp_enabled=false`, `battle_engine_runtime_used=false`.

## Divieti
Nessuna fetch backend, nessuna mutazione ranking/leaderboard/currency, nessun import da story.tsx/combat.tsx.
