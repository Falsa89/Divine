# 218 — PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY

## Decisione canonica utente

> Tutte le modalità che prevedono una battaglia devono mostrare la **battaglia reale/visuale** al player.
>
> Unica eccezione: **Guild War** può/deve risolvere automaticamente la battaglia, ma deve fornire all'utente un **link/entrypoint per visualizzare la battaglia o il replay** appena avvenuto.

Questo pack è **DESIGN/CONTRACT/AUDIT-ONLY**. Nessuna conversione runtime in questa fase.

## Perché Home PLAY → `/story` resta corretto

Il fix v28 (`PROJECT_BATTLE_ENTRYPOINT_ROUTING_AND_AUTORESOLVE_AUDIT_FIX_PACK`) ha già ricablato il PLAY centrale della Home dallo storico `/combat` a `/story`. Quel fix resta valido perché:

- `/combat` non era un entrypoint contestualizzato (era un simulatore visuale generico senza payload mode-aware);
- la Home deve aprire un hub (Storia), non lanciare una battaglia random;
- la futura visual battle dovrà partire da uno stage/contesto preciso (stage Story, nodo Raid, piano Tower, ecc.), non da Home direttamente.

## Perché lo Story auto-resolve è ora **debito transitorio**

Lo schermo `frontend/app/story.tsx` chiama `/api/story/battle` e mostra il risultato via Alert (auto-resolve invisibile). Sotto la nuova policy canonica, questo viola il principio "Story è una modalità con battaglia → deve essere visuale".

**Non viene convertito in questo pack** per le seguenti ragioni di sicurezza:

- la conversione richiede un battle instance/payload contract che ancora non esiste;
- il flusso reward deve diventare idempotente (un singolo `battle_instance_id`) per evitare doppi reward / doppia EXP / doppio quest_progress / doppio daily_progress / doppio achievement_progress se l'utente refresha la visual battle;
- serve un meccanismo di commit one-shot del risultato server-authoritative;
- serve un viewer di replay separato che non possa rilanciare battaglia né concedere reward.

Questi requisiti sono codificati nel contract `battle_visual_routing_contract_v1.json`.

## Perché `/combat` non può diventare il target universale subito

`frontend/app/combat.tsx` lancia `/api/battle/simulate` on-mount. È utile come visual battle player ma:

- non riceve un `battle_instance_id` o `mode_id`;
- non implementa idempotency su reward;
- non sa se la battaglia ha già prodotto rewards o no (rischio doppia grant);
- non distingue tra "visualizza" e "risolvi".

Resta quindi route diretta/dev/QA finché PHASE_3 non lo generalizza in un visual battle runner contract-safe.

## Battle Instance/Payload Contract richiesto (future)

Cfr. `battle_visual_routing_contract_v1.json → future_visual_battle_payload_contract`:

- `battle_instance_id`
- `mode_id`
- `source_entrypoint`
- `team_snapshot`, `enemy_snapshot`, `formation_snapshot`
- `battle_seed_or_precomputed_log`
- `reward_policy` (idempotency_key, granted_state, claim_window)
- `result_commit_policy` (commit_once, server_authoritative)
- `replay_snapshot_policy` (ttl, scope, pii_safe)

## Rischi Reward/EXP/Idempotency

- **Doppia grant**: se il client può rilanciare visual battle dopo auto-resolve, il server DEVE rifiutare ogni grant successivo con stesso `battle_instance_id`.
- **Doppia EXP**: stessa logica, server-side ledger.
- **Daily/Quest/Achievement**: ogni progress increment deve essere chiavato su `battle_instance_id`.
- **Replay farming**: il viewer replay NON deve mai riavviare la risoluzione battaglia né concedere reward.
- **War score (Guild War)**: nessuna mutazione score on view.

## Eccezione Guild War + Replay Link

Cfr. `guild_war_autoresolve_replay_policy_v1.json`:

- Auto-resolve permesso (asincrono server-side).
- Replay/view link richiesto, target futuro: `/battle-replay`.
- View-only: nessun rerun, nessun reward su view, nessuna mutazione war_score, no leak di dati privati.
- Snapshot completi richiesti: attacker/defender, result_summary, timeline/battle_log.
- Policy di expiration + privacy obbligatorie.

Future pack dedicato: `PROJECT_GUILD_WAR_AUTORESOLVE_REPLAY_LINK_PACK`.

## Mode Conversion Roadmap

Cfr. `mode_visual_battle_conversion_roadmap_v1.json`:

1. **PHASE_0_CONTRACT** — questo pack.
2. **PHASE_1_STORY_VISUAL_BATTLE_CONTRACT_AND_PAYLOAD** — design payload Story.
3. **PHASE_2_STORY_VISUAL_BATTLE_IMPLEMENTATION** — wiring Story → visual con fallback.
4. **PHASE_3_GENERIC_VISUAL_BATTLE_RUNNER** — generalizza `/combat` in runner riutilizzabile.
5. **PHASE_4_MODE_BY_MODE_CONVERSION** — Material Raid → Raid → Tower → Trials → Boss → Events → PvP.
6. **PHASE_5_GUILD_WAR_AUTORESOLVE_REPLAY_LINK** — view link Guild War.
7. **PHASE_6_REWARD_IDEMPOTENCY_HARDENING** — ledger server-side + auditor.

Ogni fase richiede: DB write audit, reward duplication guard, EXP duplication guard, economy regression guard, replay/snapshot guard.

## File creati in questo pack

- `data/design/battle_visual_routing/battle_visual_routing_contract_v1.json`
- `data/design/battle_visual_routing/guild_war_autoresolve_replay_policy_v1.json`
- `data/design/battle_visual_routing/mode_visual_battle_conversion_roadmap_v1.json`
- `data/design/battle_visual_routing/battle_visual_routing_contract_proof_marker_v1.json`
- `data/design/battle_entrypoints/battle_entrypoint_registry_v2.json` (supersedes v1)
- `backend/scripts/validate_project_visual_battle_routing_contract_and_guild_war_replay_policy_v1.py`
- `docs/divine/218_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY.md` (questo file)

## File NON toccati

- `frontend/app/story.tsx`, `frontend/app/combat.tsx`, `frontend/constants/homeAssetsManifest.ts`
- `backend/battle_engine.py`, `backend/server.py`, `backend/.env`, `backend/routes/artifacts.py`
- `backend/routes/material_raid_preview.py`, `backend/routes/gem_socket_preview.py`, `backend/routes/forge.py`
- `frontend/app/battlepass.tsx`, `frontend/app/vip.tsx`
- `/api/story/battle`, `/api/battle/simulate` (zero modifiche)
- Character Bible, hero final_numbers

## Garanzie

- `db_writes` = 0
- nessuna conversione runtime
- nessuna modifica a reward/EXP/quest/daily/achievement/economy
- nessuna modifica a gacha/pity/shop/BP/VIP/IAP
- nessuna modifica a Material Raid / Gem Socket / Rune / Artifact / Divine Weapon
- tuple count v29 = 1 (no duplicate)

## Verdict atteso

- Locale: `PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`
- Pubblico (dopo Save to GitHub + verifica): `PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY_COMPLETE_PUBLIC_REPO_VERIFIED`

## Prossimo pack consigliato

`PROJECT_STORY_VISUAL_BATTLE_WIRING_CONTRACT_PACK` — trasforma Story stage da auto-resolve a visual battle in modo sicuro: payload `battle_instance_id`, idempotency reward, story progress protetto.
