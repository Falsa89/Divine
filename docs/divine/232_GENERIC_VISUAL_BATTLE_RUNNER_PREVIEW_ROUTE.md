# 232 - PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE_PACK

**Phase**: PHASE_4 (Generic Visual Battle Runner Preview Route)  
**Mode**: PREVIEW_ROUTE_GATED_NO_LIVE_COMMIT  
**Pack version**: v34  
**Created (UTC)**: 2026-05-31T17:20:00Z  
**Parent contract**: v33 PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT_PACK

## Obiettivo

Creare il **primo guscio preview** del Generic Visual Battle Runner, basato sul contract v33. Il pack aggiunge:

- 4 endpoint backend gated sotto `/api/generic-visual-battle-runner-preview/*`;
- una route frontend deeplink-only `/generic-visual-battle-runner-preview`;
- un sample payload deterministico conforme allo schema v33 (21 campi required);
- registry v6 (supersede v5) con una nuova entry isolata per la preview route;
- proof marker + design contract + validator + tupla OPTIONAL v34 nel suite runner.

## Perche' "primo guscio preview"

Il contract v33 ha congelato il design del runner generico. Per evitare di convertire direttamente `/combat` o `/story` (rischio P0 di rottura economia/progress), questo pack introduce uno **strato preview completamente isolato** che permette di:

- esercitare il payload schema v33 end-to-end via API + UI;
- verificare che il contract sia consumabile da un client React Native;
- mantenere `runtime_enabled=false` di default (HTTP 503 disabled envelope);
- garantire `db_writes=0`, `reward_grant_enabled=false`, `exp_grant_enabled=false`, `progress_enabled=false` per costruzione (nessun import DB, nessuna chiamata a battle engine).

## Feature flag

`GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ENABLED`

- **default**: unset / `false` -> tutti gli endpoint restituiscono HTTP **503** con envelope `status:disabled` + safety flags esplicite
- **true**: gli endpoint restituiscono 200 con sample payload v33-compliant + playback display-only

## Endpoint

| Method | Path | Behavior (flag off) | Behavior (flag on) |
|---|---|---|---|
| GET | `/api/generic-visual-battle-runner-preview/config` | 503 disabled | 200 config + safety_flags |
| GET | `/api/generic-visual-battle-runner-preview/sample-payload` | 503 disabled | 200 v33 payload (21 fields) |
| POST | `/api/generic-visual-battle-runner-preview/validate-payload` | 503 disabled | 200 `{valid: bool, errors, missing_fields}` |
| POST | `/api/generic-visual-battle-runner-preview/playback-preview` | 503 disabled | 200 display-only timeline envelope |

## Frontend sandbox route

`frontend/app/generic-visual-battle-runner-preview.tsx` -> deeplink `/generic-visual-battle-runner-preview`

- **NON** linkata da Home / menu / Story / combat
- Mostra stato disabled (503) di default
- Con flag on: fetch sample payload, validate, playback preview, render timeline + safety cards
- **NO** bottone claim / commit
- **NO** AsyncStorage writes
- **NO** chiamate a `/api/story/battle` o `/api/battle/simulate`

## Consumo del payload v33

Il sample payload espone tutti e 21 i required_fields v33: `battle_instance_id`, `runner_mode`, `mode_id`, `source_entrypoint`, `viewer_kind`, `team_snapshot`, `enemy_snapshot`, `formation_snapshot`, `battle_background_context`, `battle_seed_or_precomputed_battle_log`, `playback_timeline`, `result_summary`, `reward_policy`, `exp_policy`, `progress_policy`, `result_commit_policy`, `replay_snapshot_policy`, `ui_policy`, `privacy_policy`, `created_at`, `expires_at`.

Default values:
- `runner_mode = sandbox_preview`
- `mode_id = generic_preview`
- `viewer_kind = sandbox_preview`
- `source_entrypoint = generic_visual_battle_runner_preview`
- tutti i `*.grant_enabled / advance_enabled / commit_enabled / write_enabled / show_claim_buttons / share_contains_pii = false`

## Safety invariants enforced by code

- nessun import di `battle_engine` nel modulo route;
- nessuna chiamata HTTP a `/api/battle/simulate` o `/api/story/battle`;
- nessun token DB (`db.*.update_one`, `insert_one`, ecc.);
- nessun bottone claim/commit nella UI;
- nessuna AsyncStorage write nella UI;
- `db_writes=0`, `reward_grant_enabled=false`, `exp_grant_enabled=false`, `progress_enabled=false` esposti negli envelope di OGNI endpoint (sia disabled che enabled).

## Nessuna conversione runtime live

- `/combat` invariato (refactor vietato; valida `combat.tsx` contiene ancora `/api/battle/simulate`)
- `/story` invariato (auto-resolve transitorio via `/api/story/battle`)
- `story-visual-battle-sandbox.tsx` invariato
- Home routes invariate (Play/Battle -> `/story`)
- `backend/battle_engine.py` invariato
- `/api/story/battle` invariato
- `/api/battle/simulate` invariato
- `backend/server.py` modificato **solo** per `include_router` del nuovo preview router

## Suite runner

Aggiunta **una sola** tupla OPTIONAL v34 con sentinelle:
- `PUBLIC_SYNC_DIAGNOSTIC_BLOCK_v34_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE`
- `PUBLIC_SYNC_TAG_v34_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE`
- `GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE_REGISTRATION_SENTINEL`

Tupla:
```python
("PROJECT-GENERIC-VISUAL-BATTLE-RUNNER-PREVIEW-ROUTE",
 "validate_project_generic_visual_battle_runner_preview_route_v1.py")
```

## Caveat public sync

`SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION` accettato. Nessun pack v34b/v34c sync-fix.

## Verdict atteso

Locale: `PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Public con caveat: `PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE_FUNCTIONAL_PUBLIC_CONTENT_VERIFIED_WITH_SUITE_RUNNER_STALE_CAVEAT`

## Prossimi pack candidati

- `PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_RUNTIME_SHELL_PACK` — RN component runtime per render della timeline (ancora preview-only)
- `PROJECT_GUILD_WAR_AUTORESOLVE_REPLAY_LINK_PACK` — replay/view link `/battle-replay`
- `PROJECT_STORY_VISUAL_BATTLE_RUNTIME_APPLY_PACK` — futuro PHASE_5 della catena Story (richiede idempotency ledger + server-authoritative commit service prima dell'attivazione)
