# 231 - PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT_PACK

**Phase**: PHASE_3 sister (Generic Visual Battle Runner Contract)  
**Mode**: DESIGN_CONTRACT_AUDIT_ONLY  
**Pack version**: v33  
**Created (UTC)**: 2026-05-31T16:50:00Z

## Obiettivo

Definire il *contract foundation* per il futuro **Generic Visual Battle Runner**, una view layer riusabile capace di renderizzare visual battles per tutte le modalita' del gioco (Story, Story Sandbox, Direct QA Combat, Guild War Replay, Tower, Raid, Material Raid, Boss, Event, Trial, PvP).

Questo pack **NON converte alcun runtime live**. E' interamente design/contract/audit-only.

## Stato attuale (preservato)

- `frontend/app/combat.tsx` resta **direct/dev/QA** e chiama `/api/battle/simulate` on mount. **NON viene refactorato.**
- `frontend/app/story.tsx` resta **auto-resolve transitorio** via `/api/story/battle`. **NON viene modificato.**
- `frontend/app/story-visual-battle-sandbox.tsx` resta **sandbox preview-only**. **NON viene modificato.**
- Home routes (`play -> /story`, `battle -> /story`) restano invariati.
- `backend/battle_engine.py` resta invariato (MD5-locked).
- `/api/story/battle` e `/api/battle/simulate` restano invariati.
- Nessuna nuova rotta backend creata in questo pack.

## Contratto runner desiderato (sintesi)

Il runner futuro:

- **e' un view layer**, mai authoritative;
- **non concede mai reward, EXP o progress** (story/daily/quest/achievement);
- **non scrive mai sul DB**;
- **non consuma stamina/ticket**;
- **non rieffettua mai la battaglia client-side** nelle modalita' authoritative;
- accetta `battle_instance_id` server-issued;
- accetta `mode_id`, `source_entrypoint`, `viewer_kind`;
- accetta snapshots immutabili (team/enemy/formation/background);
- accetta `battle_seed` **oppure** `precomputed_battle_log`;
- accetta `playback_timeline`, `result_summary`;
- accetta policy (reward/exp/progress/result_commit/replay_snapshot/ui/privacy);
- accetta `created_at` e `expires_at` (TTL hard).

L'eventuale commit di reward/EXP/progress sara' delegato in futuro a un **mode service server-authoritative**, con `idempotency_key_required=true`.

## Viewer kinds

- `live_preview`
- `live_commit_pending_future`
- `replay_view`
- `guild_war_view`
- `sandbox_preview`
- `qa_direct`

Di questi, `replay_view`, `guild_war_view`, `sandbox_preview`, `qa_direct` sono **view-only**: i pulsanti di commit/claim sono nascosti.

## Mode adapter matrix

Definita per 11 modalita': `story`, `story_sandbox`, `direct_qa_combat`, `guild_war_replay`, `tower`, `raid`, `material_raid`, `boss`, `event_battle`, `trial`, `pvp`. Ogni adapter dichiara:

- `runtime_changed_this_pack=false`
- `can_grant_rewards_in_runner=false`
- `can_advance_progress_in_runner=false`

Guild War e' marcata come **unica eccezione auto-resolve** ammessa, sempre con replay/view link futuro `/battle-replay`.

## Registry v5

Il registry v5 supersede v4 e marca:

- `direct_visual_combat_route` -> `generic_runner_contract_ready_runtime_pending`
- `story_stage_battle` -> `sandbox_ready_runner_contract_ready_runtime_pending`
- `story_visual_battle_sandbox` -> `sandbox_preview_ready`
- `guild_war` -> unica eccezione auto-resolve, con replay/view link via generic runner
- tutte le altre modalita' richiedono visual battle via generic runner

## Safety invariants (zero live mutation)

- `db_writes=0`
- nessun reward grant
- nessun EXP grant
- nessun story/daily/quest/achievement progress
- economy/gacha/pity/shop/BP/VIP/IAP invariati
- Material Raid / Gem Socket / Rune / Artifact / Divine Weapon / Guild War runtime invariati
- Character Bible / hero `final_numbers` invariati
- 5 file MD5-locked **non toccati** (`battle_engine.py`, `backend/.env`, `routes/artifacts.py`, `battlepass.tsx`, `vip.tsx`)

## Suite runner registration

Nel file `backend/scripts/run_hero_skill_kit_validator_suite.py` viene aggiunta esattamente **una tupla OPTIONAL v33** con sentinelle:

- `PUBLIC_SYNC_DIAGNOSTIC_BLOCK_v33_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT`
- `PUBLIC_SYNC_TAG_v33_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT`
- `GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT_REGISTRATION_SENTINEL`

Tupla:

```python
("PROJECT-GENERIC-VISUAL-BATTLE-RUNNER-CONTRACT",
 "validate_project_generic_visual_battle_runner_contract_v1.py")
```

Count = 1. No duplicate.

## Public sync caveat

E' accettato il caveat `SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION`. Nessun pack v33b/v33c sync-fix verra' tentato.

## Verdict atteso

Locale: `PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Public (con caveat): `PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT_FUNCTIONAL_PUBLIC_CONTENT_VERIFIED_WITH_SUITE_RUNNER_STALE_CAVEAT`

## Prossimo pack suggerito

`PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE_PACK` — creazione (futura) di una rotta preview gated 503 che consuma il payload schema definito qui, ancora **senza** alcuna conversione runtime live.
