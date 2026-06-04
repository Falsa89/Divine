# 407 — Story Alpha Slice Preview Screen

**Pack:** `MEGA_RELEASE_ACCELERATION_17_STORY_PLAYABLE_ALPHA_AND_BOSS_TOWER_ALPHA_LOOP_SUPER_PACK_v68`

## Screen
- `frontend/app/story-alpha-slice-preview.tsx` (nuova, deeplink-only).
- Lo screen v67 `story-first-node-runtime-preview.tsx` resta intatto.

## Comportamento
- Mini-loop sui nodi `story_alpha_node_001` / `002` / `003`.
- Mostra il nodo corrente, la timeline degli step e l'avanzamento del capitolo.
- Controlli: nodo precedente / nodo successivo / step successivo / reset capitolo / play-pause autoplay (con cleanup).
- Mostra result preview dopo `story_alpha_node_003`.
- Reward preview e progress preview disabilitati.

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
