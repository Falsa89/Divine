# 237 - PROJECT_BATTLE_REPLAY_PREVIEW_ROUTE_PACK

**Phase**: PHASE_6 (Battle Replay Preview Route)  
**Mode**: BATTLE_REPLAY_PREVIEW_ROUTE_GATED_VIEW_ONLY  
**Pack version**: v36  
**Created (UTC)**: 2026-05-31T18:30:00Z  
**Parent contract**: v35 PROJECT_GUILD_WAR_AUTORESOLVE_REPLAY_LINK_CONTRACT_PACK (Track B)  
**Parent shell**: v35 PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_RUNTIME_SHELL_PACK (Track A)

## Obiettivo

Creare il **primo guscio preview view-only** del futuro replay Guild War, basato sul contract v35. Il pack aggiunge:

- 4 endpoint backend gated sotto `/api/battle-replay-preview/*`;
- una route frontend deeplink-only `/battle-replay-preview` che **riusa** il `VisualBattlePreviewShell` v35 via un local adapter puro;
- un sample replay Guild War deterministico conforme allo schema v35 (17 required_fields);
- registry v8 (supersede v7) con una nuova entry isolata per la preview route;
- proof marker + design contract + validator + tupla OPTIONAL v36 nel suite runner.

**`/battle-replay` live NON viene creato.** **Guild War runtime NON viene mutato.** **War score / guild points NON vengono mutati.**

## Feature flag

`BATTLE_REPLAY_PREVIEW_ENABLED`

- default: unset / `false` -> tutti gli endpoint restituiscono HTTP **503** con envelope `status:disabled` + safety flags esplicite (incluso `viewer_kind=guild_war_view`, `war_score_mutation_enabled=false`, `guild_points_mutation_enabled=false`)
- `true`: gli endpoint restituiscono 200 con replay payload v35-compliant + playback display-only (`runner_mode=replay_view`, `viewer_kind=guild_war_view`)

## Endpoint

| Method | Path | Behavior (flag off) | Behavior (flag on) |
|---|---|---|---|
| GET | `/api/battle-replay-preview/config` | 503 disabled | 200 config + safety_flags + viewer_kind=guild_war_view |
| GET | `/api/battle-replay-preview/sample-guild-war-replay` | 503 disabled | 200 con replay payload v35 (17 fields) |
| POST | `/api/battle-replay-preview/validate-replay-payload` | 503 disabled | 200 `{valid: bool, errors, missing_fields}` |
| POST | `/api/battle-replay-preview/playback-preview` | 503 disabled | 200 envelope display-only con `guild_war_context` + `war_score_delta_display_only` |

## Frontend route

`frontend/app/battle-replay-preview.tsx` -> deeplink `/battle-replay-preview`

- **NON** linkata da Home / menu / Guild War / Story / combat
- Mostra stato disabled (503) di default
- Con flag on: fetch replay sample, validate, playback preview, **riusa `VisualBattlePreviewShell` v35**
- Adapter puro locale `adaptReplayPayloadForShell`:
  - `attacker_snapshot` -> `team_snapshot`
  - `defender_snapshot` -> `enemy_snapshot` (`hero_id` -> `enemy_id`)
  - `battle_seed_or_precomputed_log` -> `battle_seed_or_precomputed_battle_log`
  - `playback_timeline` -> `playback_timeline`
  - `result_summary` -> `result_summary`
- Card aggiuntive:
  - `ReplayMetadataCard` (guild_war_battle_id, war_id, attacker/defender guild names)
  - `WarScoreDisplayOnlyCard` (mostra `attacker_delta`/`defender_delta` con etichetta `DISPLAY ONLY · NOT APPLIED`)
  - `SafetyFooter` (11 safety flag con viewer_kind=guild_war_view)
- **NO** bottoni claim / commit / war score
- **NO** AsyncStorage writes
- **NO** chiamate a `/api/story/battle` o `/api/battle/simulate`

## Riutilizzo dello shell v35

La route monta `VisualBattlePreviewShell` solo se `shellPayload` e `playback?.status === 'preview_ok'`. Il shell rendera':
- HP bars deterministici (replay del precomputed log)
- Timeline stepper con hit markers
- Result summary display-only
- Safety panel v35 (14 flag)

## Consumo del payload v35

Il sample payload espone tutti e 17 i required_fields v35: `guild_war_battle_id`, `battle_instance_id`, `war_id`, `guild_id_attacker`, `guild_id_defender`, `attacker_snapshot`, `defender_snapshot`, `battle_seed_or_precomputed_log`, `playback_timeline`, `result_summary`, `war_score_delta_display_only`, `reward_policy`, `guild_points_policy`, `privacy_policy`, `retention_policy`, `created_at`, `expires_at`.

## Privacy & retention

Il sample replica le policy v35:
- `privacy_policy.no_pii_in_share_payload=true`, `redact_other_players=true`
- `retention_policy.default_retention_days=14`, `max=30`, `ttl_hard_required=true`, `client_local_persistence_allowed=false`, `async_storage_writes_allowed=false`

## Vincoli rispettati

- nessuna rotta `/battle-replay` live creata
- nessuna mutazione runtime Guild War
- nessuna mutazione war_score / guild_points
- `combat.tsx`, `story.tsx`, `story-visual-battle-sandbox.tsx`, `generic-visual-battle-runner-preview.tsx` invariati
- Home routes invariate
- `backend/battle_engine.py`, `/api/story/battle`, `/api/battle/simulate` invariati
- 5 file MD5-locked invariati
- nessuna nuova dipendenza installata
- `backend/server.py` scoped diff (solo `include_router`)

## Public sync caveat

`SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION` accettato. Nessun pack v36b/v36c sync-fix.

## Verdict atteso

Locale: `PROJECT_BATTLE_REPLAY_PREVIEW_ROUTE_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Public con caveat: `PROJECT_BATTLE_REPLAY_PREVIEW_ROUTE_FUNCTIONAL_PUBLIC_CONTENT_VERIFIED_WITH_SUITE_RUNNER_STALE_CAVEAT`

## Prossimi pack candidati

- `PROJECT_GEM_SOCKET_COMMIT_SAFETY_HARDENING_PACK` (P2)
- `PROJECT_MATERIAL_RAID_LIVE_CLAIM_SAFETY_HARDENING_PACK` (P2)
- Futuro PHASE_5 Story runtime apply (richiede idempotency ledger prima)
- Futuro PHASE_5 Guild War replay live route (richiede idempotency ledger e mode service)
