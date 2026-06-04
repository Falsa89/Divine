# 414 — Training + Combat Onboarding Preview UI

**Pack:** `MEGA_RELEASE_ACCELERATION_18_v69`

## Screen
- `frontend/app/training-combat-onboarding-preview.tsx` (nuova, deeplink-only).

## Comportamento
- 6 step tutorial in italiano.
- Controlli step avanti/indietro/reset.
- Pannello guardrail con `result_authoritative=false`, `db_writes=0`, `battle_engine_runtime_used=false`, `reward_grant_enabled=false`, `permanent_progress_enabled=false`.
- Link informativo (testuale) alle altre anteprime deeplink-only.

## Divieti
Nessuna fetch backend, nessun import da `story.tsx`/`combat.tsx`, nessun uso di Reanimated/AsyncStorage, nessun pulsante claim/reward.
