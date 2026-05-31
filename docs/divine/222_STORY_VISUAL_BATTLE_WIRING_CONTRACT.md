# 222 — PROJECT_STORY_VISUAL_BATTLE_WIRING_CONTRACT (PHASE_1)

## Decisione canonica (riepilogo)

> Tutte le modalità con battaglia devono mostrare visual battle.
> Guild War è l'unica eccezione auto-resolve, e deve avere replay/view link.
> Story stage battle è ora **P0 transitional debt**: deve diventare visual battle.

Questo pack è **DESIGN/CONTRACT/AUDIT-ONLY**. Nessuna conversione runtime.

## Stato corrente di Story

- File: `frontend/app/story.tsx`.
- Carica capitoli via `/api/story/chapters`.
- Avvia battaglia stage via `/api/story/battle`.
- Mostra risultato con `Alert` (auto-resolve invisibile).
- Il player **non vede** la battaglia.
- Story progress + reward + EXP vengono concessi server-side al ritorno della response.

Questo comportamento resta **invariato** in questo pack.

## Direzione canonica desiderata

In futuro lo stage Story deve:

1. creare/riutilizzare un `battle_instance_id` lato server (PHASE_2 preview endpoint);
2. il client naviga al visual battle viewer passando `battle_instance_id`;
3. il visual battle gira da snapshot/precomputed_log (NON rerun di RNG per i reward);
4. il server committa il risultato **una sola volta** (idempotency su `battle_instance_id`);
5. concede reward **una sola volta** (idempotency su `idempotency_key`);
6. concede EXP **una sola volta**;
7. avanza story progress **una sola volta**;
8. mostra post-battle summary al player;
9. salva snapshot replay view-only.

Il flow è codificato in `story_visual_battle_wiring_contract_v1.json → required_future_flow`.

## Perché questo pack non collega subito Story a `/combat`

`frontend/app/combat.tsx` oggi chiama `/api/battle/simulate` on-mount, senza un `battle_instance_id`, senza un `mode_id` Story, senza un `chapter_id`/`stage_id`. Se Story aprisse direttamente `/combat`:

- impossibile sapere se la battaglia ha già prodotto reward (rischio doppia grant tra `/api/story/battle` legacy e `/api/battle/simulate`);
- impossibile chiavare il commit one-shot;
- impossibile prevenire replay-farming dei rewards Story;
- impossibile differenziare "giocata" da "vista replay".

Quindi prima va attivato il payload contract (PHASE_2 preview endpoint), poi una sandbox isolata (PHASE_3), poi una canary dual-route (PHASE_4), e solo poi il runtime apply (PHASE_5).

## Battle Instance Payload (PHASE_2+)

Cfr. `story_battle_instance_payload_contract_v1.json`. Campi richiesti:

- `battle_instance_id` (stabile per attempt logico)
- `idempotency_key` (anti-doppia grant)
- `mode_id = story`
- `chapter_id`, `stage_id`
- `user_id` (runtime, non esposto a share)
- `server_id` (futuro multi-server)
- `source_entrypoint = story_stage_play`
- `team_snapshot`, `enemy_snapshot`, `formation_snapshot`
- `battle_seed` *oppure* `precomputed_battle_log`
- `reward_policy`, `exp_policy`, `story_progress_policy`
- `result_commit_policy`, `replay_snapshot_policy`
- `created_at`, `expires_at`

Regole: snapshot frozen al momento della creazione; nessun PII/token esposto a replay/share; il futuro `/combat` runner deve **richiedere** un `battle_instance_id` prima di servire Story.

## Idempotency / Reward Guard

Cfr. `story_reward_idempotency_contract_v1.json`. Garanzie obbligatorie:

- `result_commit_must_be_once_only`
- `reward_grant_must_be_once_only`
- `hero_exp_grant_must_be_once_only`
- `account_exp_grant_must_be_once_only`
- `story_progress_must_be_once_only`
- `daily_progress_must_be_once_only_if_applicable`
- `quest_progress_must_be_once_only_if_applicable`
- `achievement_progress_must_be_once_only_if_applicable`
- `replay_view_must_not_grant_rewards`
- `replay_view_must_not_advance_progress`
- `retry_same_request_returns_same_result`

Future storage: `battle_instance_ledger`, `reward_commit_ledger`, `replay_snapshot_store`, TTL policy. **In questo pack: zero ledger live, zero DB write.**

## Relazione con Battle Report Replay/Save/Share Foundation

Il replay/view dello stage Story non deve mai concedere reward / EXP / progress. Riutilizza l'architettura della foundation pack: snapshot frozen, viewer puro, no rerun di battle logic.

## Roadmap (transition plan)

Cfr. `story_visual_battle_transition_plan_v1.json`:

1. **PHASE_1_CONTRACT** — questo pack.
2. **PHASE_2_STORY_BATTLE_INSTANCE_PREVIEW_ENDPOINT** — endpoint preview inert (503 default), no reward commit. Target pack: `PROJECT_STORY_BATTLE_INSTANCE_PREVIEW_ENDPOINT_PACK`.
3. **PHASE_3_STORY_VISUAL_BATTLE_SANDBOX** — sandbox payload visualization, no live story progress.
4. **PHASE_4_STORY_VISUAL_BATTLE_DUAL_ROUTE_CANARY** — canary gated dual-route con fallback auto-resolve.
5. **PHASE_5_STORY_VISUAL_BATTLE_RUNTIME_APPLY** — sostituzione del flow per il player normale, commit idempotente.
6. **PHASE_6_REPLAY_AND_REPORT_HARDENING** — replay snapshot + report + save/share alignment.
7. **PHASE_7_REMOVE_STORY_AUTORESSOLVE_DEBT** — deprecazione del flow invisibile (resta solo per debug/admin).

Ogni fase richiede: DB write audit, reward duplication guard, EXP duplication guard, story progress idempotency, fallback/rollback, validator, smoke tests.

## File creati in questo pack

- `data/design/story_visual_battle/story_visual_battle_wiring_contract_v1.json`
- `data/design/story_visual_battle/story_battle_instance_payload_contract_v1.json`
- `data/design/story_visual_battle/story_reward_idempotency_contract_v1.json`
- `data/design/story_visual_battle/story_visual_battle_transition_plan_v1.json`
- `data/design/story_visual_battle/story_visual_battle_wiring_contract_proof_marker_v1.json`
- `data/design/battle_entrypoints/battle_entrypoint_registry_v3.json` (supersedes v1+v2)
- `backend/scripts/validate_project_story_visual_battle_wiring_contract_v1.py`
- `docs/divine/222_STORY_VISUAL_BATTLE_WIRING_CONTRACT.md` (questo file)

## File NON toccati

- `frontend/app/story.tsx`, `frontend/app/combat.tsx`, `frontend/constants/homeAssetsManifest.ts`
- `backend/battle_engine.py`, `backend/server.py`, `backend/.env`, `backend/routes/artifacts.py`
- `backend/routes/material_raid_preview.py`, `backend/routes/gem_socket_preview.py`, `backend/routes/forge.py`
- `frontend/app/battlepass.tsx`, `frontend/app/vip.tsx`
- `/api/story/battle`, `/api/battle/simulate` (zero modifiche)
- Character Bible, hero final_numbers
- Guild War / Artifact / Divine Weapon / Rune runtime

## Garanzie

- `db_writes` = 0
- nessuna conversione runtime
- nessuna modifica a reward / EXP / story progress / quest / daily / achievement / economy
- nessuna modifica a gacha / pity / shop / BP / VIP / IAP
- nessuna modifica a Material Raid / Gem Socket / Rune / Artifact / Divine Weapon / Guild War
- tuple count v30 = 1 (no duplicate)

## Verdict atteso

- Locale: `PROJECT_STORY_VISUAL_BATTLE_WIRING_CONTRACT_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`
- Pubblico (dopo Save to GitHub + verifica): `PROJECT_STORY_VISUAL_BATTLE_WIRING_CONTRACT_COMPLETE_PUBLIC_REPO_VERIFIED`

## Prossimo pack consigliato

`PROJECT_STORY_BATTLE_INSTANCE_PREVIEW_ENDPOINT_PACK` (PHASE_2):
- endpoint preview inert (gated 503 default) per la creazione di `battle_instance_id` Story;
- nessun reward commit;
- prepara il payload che il futuro visual combat runner potrà consumare.

Pack paralleli sicuri:
- `PROJECT_MODE_BATTLE_ENTRYPOINT_REGISTRY_EXPANSION_PACK`
- `PROJECT_MATERIAL_RAID_GEM_TRACK_PREVIEW_UNLOCK_PACK`
- `PROJECT_GUIDE_CODEX_FILL_GAPS_PACK`
