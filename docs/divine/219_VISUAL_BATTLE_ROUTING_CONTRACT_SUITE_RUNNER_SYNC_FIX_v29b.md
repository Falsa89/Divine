# 219 — PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_SUITE_RUNNER_SYNC_FIX_v29b

## Scopo

Micro-pack di solo sync per risolvere lo stato stale del `backend/scripts/run_hero_skill_kit_validator_suite.py` su GitHub main dopo il push del parent pack `PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY_PACK` (commit `0c6601b4`).

## Contesto

La main pubblica contiene già correttamente i 7 file design/doc/validator del parent v29:

- `data/design/battle_visual_routing/battle_visual_routing_contract_v1.json`
- `data/design/battle_visual_routing/guild_war_autoresolve_replay_policy_v1.json`
- `data/design/battle_visual_routing/mode_visual_battle_conversion_roadmap_v1.json`
- `data/design/battle_visual_routing/battle_visual_routing_contract_proof_marker_v1.json`
- `data/design/battle_entrypoints/battle_entrypoint_registry_v2.json`
- `docs/divine/218_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY.md`
- `backend/scripts/validate_project_visual_battle_routing_contract_and_guild_war_replay_policy_v1.py`

Ma il `backend/scripts/run_hero_skill_kit_validator_suite.py` pubblico NON contiene ancora:

- sentinel `PUBLIC_SYNC_TAG_v29_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY`
- sentinel `VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY_REGISTRATION_SENTINEL`
- tupla `('PROJECT-VISUAL-BATTLE-ROUTING-CONTRACT-AND-GUILD-WAR-REPLAY-POLICY', 'validate_project_visual_battle_routing_contract_and_guild_war_replay_policy_v1.py')`

Lo stato locale del container era già corretto (tupla + sentinels presenti dalla v29). Questo pack v29b aggiunge UN solo sentinel nuovo `PUBLIC_SYNC_TAG_RESYNC_v29b_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY` per forzare GitHub a riconoscere il blob come modificato in fase di Save to GitHub.

## Modifiche eseguite (scope strettissimo)

1. `backend/scripts/run_hero_skill_kit_validator_suite.py` (UNICO file modificato):
   - Aggiunto commento sentinel `PUBLIC_SYNC_TAG_RESYNC_v29b_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY` immediatamente sotto il sentinel `v29` esistente.
   - **Nessuna modifica** alla tupla (resta `tuple_count = 1`).
   - **Nessuna modifica** ai sentinel preesistenti.
   - **Nessun cambiamento di semantica**.

2. Creati:
   - `data/design/battle_visual_routing/battle_visual_routing_contract_suite_runner_sync_fix_v29b_marker_v1.json` — proof marker v29b.
   - `docs/divine/219_VISUAL_BATTLE_ROUTING_CONTRACT_SUITE_RUNNER_SYNC_FIX_v29b.md` — questo documento.

## File NON toccati (forbidden scope)

- Tutti i 7 file del parent v29 sopra elencati: **UNCHANGED**.
- `frontend/app/story.tsx`, `frontend/app/combat.tsx`, `frontend/constants/homeAssetsManifest.ts`
- `backend/battle_engine.py`, `backend/server.py`, `backend/.env`, `backend/routes/artifacts.py`
- `backend/routes/material_raid_preview.py`, `backend/routes/gem_socket_preview.py`, `backend/routes/forge.py`
- `frontend/app/battlepass.tsx`, `frontend/app/vip.tsx`
- Economy / gacha / BP / VIP / shop / IAP / Material Raid / Gem Socket / Rune / Artifact / Divine Weapon runtime
- Character Bible, hero final_numbers

## Garanzie

- `db_writes` = 0
- `runtime_semantics_changed` = false
- `parent_contract_changed` = false
- Tuple count parent = **1** (no duplicate)
- MD5 invarianti su `battle_engine.py`, `.env`, `artifacts.py`, `battlepass.tsx`, `vip.tsx` → invariate.

## Verdict atteso

- Locale: `PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_SUITE_RUNNER_SYNC_FIX_v29b_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`
- Pubblico (dopo Save to GitHub + verifica): `PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY_COMPLETE_PUBLIC_REPO_VERIFIED`
