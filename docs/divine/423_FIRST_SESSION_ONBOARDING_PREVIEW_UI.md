# 423 — First Session Onboarding Preview UI

**Pack:** `MEGA_RELEASE_ACCELERATION_19_v70`

## Screen
- `frontend/app/first-session-onboarding-preview.tsx` (nuova, deeplink-only).

## Comportamento
- 6 step in italiano (welcome -> training -> story -> event/arena -> asset explainer -> next steps).
- Controlli step prec/next/reset.
- Lista informativa testuale dei deeplink correlati (training-combat-onboarding-preview, story-alpha-slice-preview, event-arena-alpha-gate-preview, event-arena-first-alpha-slice-preview, boss-tower-alpha-loop-preview).
- Pannello guardrail con `db_writes=0`, `permanent_onboarding_complete=false`, `reward_grant_enabled=false`, `account_mutation=false`, `async_storage_persistence=false`, `battle_engine_runtime_used=false`.

## Divieti
Nessuna fetch backend, nessun auth/account mutation, nessun AsyncStorage persistence, nessuna scrittura completion. Nessun import da story.tsx/combat.tsx.
