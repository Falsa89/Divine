# 230 — PROJECT_STORY_VISUAL_BATTLE_SANDBOX (PHASE_3 v32)

## Scopo

PHASE_3 della roadmap Story Visual Battle: sandbox isolato per la visualizzazione di un playback sintetico, riusando il payload preview Track A senza alcun runtime live.

## Decisioni canoniche rispettate

- Story stage_battle resta `transitional_debt` (status registry v4 = `P0`).
- Nessuna conversione runtime per i player normali.
- Niente Home/menu/tabs link verso la sandbox (dev/QA only).
- Nessun reward, nessun avanzamento story, nessun replay reward.
- Nessun DB write, nessun AsyncStorage write.
- battle_engine UNCHANGED, /api/battle/simulate UNCHANGED, /api/story/battle UNCHANGED.

## Backend

Nuovo endpoint nel router preview Track A:

- `GET /api/story/battle-instance-preview/sandbox-playback?chapter_id=...&stage_id=...&battle_seed=...`

Gated dal flag esistente `STORY_BATTLE_INSTANCE_PREVIEW_ENABLED`. Default off → 503 inert envelope.

Quando attivo restituisce:
- `timeline` deterministica (8 tick) generata via SHA256 da `battle_seed|chapter_id|stage_id`
- `final_result` sintetico (winner=player, sandbox=true, note esplicativa)
- `safety` block con tutti i flag = false / 0

## Frontend

- `frontend/app/story-visual-battle-sandbox.tsx`: nuova route Expo Router.
- UI:
  - Banner rosso SANDBOX
  - Selezione stage (1-1 / 1-3 / 2-1)
  - Bottone "1. Crea Preview Payload" → POST /create-preview
  - Bottone "2. Carica Sandbox Playback" → GET /sandbox-playback con `battle_seed`
  - Bottone "3. Play step" → incrementa visualizzazione tick by tick
  - Bottone "Reset"
  - Lista timeline tick visibili
  - Footer disclaimer dev/QA
- NON collegata da Home/menu/tabs.
- NON chiama `/api/battle/simulate`.
- NON chiama `/api/story/battle`.
- NON usa `AsyncStorage.setItem/mergeItem`.

## Garanzie

- DB writes = 0
- AsyncStorage writes = 0
- reward/EXP/story_progress/replay_reward = disabilitati
- battle_engine_changed = false, story_battle_endpoint_changed = false, battle_simulate_endpoint_changed = false
- story.tsx UNCHANGED, combat.tsx UNCHANGED, homeAssetsManifest.ts UNCHANGED
- frontend_linked_from_home/menu/tabs = false
- runtime_activation_for_normal_users = false
- MD5 invarianti su `battle_engine.py`, `.env`, `artifacts.py`, `battlepass.tsx`, `vip.tsx` → invariate.

## Verdict atteso

- Locale: `PROJECT_STORY_VISUAL_BATTLE_SANDBOX_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`
- Pubblico (dopo Save to GitHub + verifica): `PROJECT_STORY_VISUAL_BATTLE_SANDBOX_COMPLETE_PUBLIC_REPO_VERIFIED`

## Prossimo pack della roadmap Story

`PROJECT_STORY_VISUAL_BATTLE_DUAL_ROUTE_CANARY_PACK` (PHASE_4): introduzione canary gated per il routing Story a visual battle con fallback automatico ad auto-resolve, gate per percentage rollout, idempotency commit ledger preview-only.
