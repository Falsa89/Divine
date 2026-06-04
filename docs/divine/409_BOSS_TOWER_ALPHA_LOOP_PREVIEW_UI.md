# 409 — Boss + Tower Alpha Loop Preview UI

**Pack:** `MEGA_RELEASE_ACCELERATION_17_STORY_PLAYABLE_ALPHA_AND_BOSS_TOWER_ALPHA_LOOP_SUPER_PACK_v68`

## Screen
- `frontend/app/boss-tower-alpha-loop-preview.tsx` (nuova, deeplink-only).
- Le pagine `boss-visual-preview.tsx` e `tower-visual-preview.tsx` esistenti restano intatte (extra unchanged guardrail).

## Comportamento
- Schermata unica con due card alpha loop (Boss e Tower).
- Per ciascuna card: banner alpha loop, timeline 6-7 step, result preview disabilitato/no grant, controlli step successivo / play-pause / reset.
- Cleanup automatico timer a smontaggio.

## Pannello guardrail
- `result_authoritative = false`
- `db_writes = 0`
- `battle_engine_runtime_used = false`
- `reward_grant_enabled = false`
- `permanent_progress_enabled = false`

## Divieti
- Nessuna fetch backend.
- Nessun import da `frontend/app/story.tsx` o `frontend/app/combat.tsx`.
- Nessun uso di Reanimated/AsyncStorage.
- Nessun pulsante claim/reward.
- TypeScript-only.
