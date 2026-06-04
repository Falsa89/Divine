# 421 — Event/Arena First Alpha Slice Preview UI

**Pack:** `MEGA_RELEASE_ACCELERATION_19_v70`

## Screen
- `frontend/app/event-arena-first-alpha-slice-preview.tsx` (nuova, deeplink-only).

## Comportamento
- Switch Event / Arena per visualizzare lo slice attivo.
- Card con titolo, sottotitolo, progress bar, timeline 6-7 step.
- Controlli step prec/next/play-pause/reset con cleanup timer.
- Result preview dopo completamento (disabled reward/currency/ranking).
- Pannello guardrail con `result_authoritative=false`, `db_writes=0`, `battle_engine_runtime_used=false`, `reward_grant_enabled=false`, `event_currency_enabled=false`, `arena_ranking_enabled=false`.

## Divieti
Nessuna fetch backend, nessun import da story.tsx/combat.tsx, nessun Reanimated/AsyncStorage, nessun pulsante claim/reward.
