# 220 — PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_SUITE_RUNNER_SYNC_FIX_v29c

## Scopo

Secondo micro-pack di solo sync per risolvere lo stato stale persistente del `backend/scripts/run_hero_skill_kit_validator_suite.py` su GitHub main, dopo che v29b ha pubblicato marker e doc ma il blob del suite runner non ha rinfrescato i token v29.

## Catena dei commit

- Parent v29: `0c6601b4` — contract + design + doc 218 + validator + tupla suite (locale OK, pubblico parziale).
- Sync v29b: `9f030a88` — marker + doc 219 + sentinel `RESYNC_v29b` (locale OK, pubblico ancora stale sul suite runner).
- Sync v29c (questo): — marker + doc 220 + sentinel `RESYNC_v29c` per forzare un secondo refresh del blob.

## Stato pubblico atteso DOPO Save to GitHub di v29c

Il suite runner pubblico dovrà contenere:

- `PUBLIC_SYNC_TAG_v29_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY`
- `PUBLIC_SYNC_TAG_RESYNC_v29b_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY`
- `PUBLIC_SYNC_TAG_RESYNC_v29c_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY`
- `VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY_REGISTRATION_SENTINEL`
- tupla `('PROJECT-VISUAL-BATTLE-ROUTING-CONTRACT-AND-GUILD-WAR-REPLAY-POLICY', 'validate_project_visual_battle_routing_contract_and_guild_war_replay_policy_v1.py')`

## Modifiche eseguite (scope strettissimo)

1. `backend/scripts/run_hero_skill_kit_validator_suite.py` (UNICO file modificato):
   - Aggiunti 4 nuovi commenti sentinel `PUBLIC_SYNC_TAG_RESYNC_v29c_*` immediatamente sotto il sentinel `v29b` esistente, per forzare il diff del blob.
   - **Nessuna modifica** alla tupla (resta `tuple_count = 1`).
   - **Nessuna modifica** ai sentinel preesistenti `v29` e `v29b`.
   - **Nessun cambiamento di semantica**.

2. Creati:
   - `data/design/battle_visual_routing/battle_visual_routing_contract_suite_runner_sync_fix_v29c_marker_v1.json` — proof marker v29c.
   - `docs/divine/220_VISUAL_BATTLE_ROUTING_CONTRACT_SUITE_RUNNER_SYNC_FIX_v29c.md` — questo documento.

## File NON toccati (forbidden scope)

- Tutti i 7 file del parent v29 (contract, guild war policy, roadmap, proof marker, registry v2, doc 218, validator): **UNCHANGED**.
- Marker e doc v29b: **UNCHANGED**.
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

- Locale: `PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_SUITE_RUNNER_SYNC_FIX_v29c_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`
- Pubblico (dopo Save to GitHub + verifica blob suite runner): `PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY_COMPLETE_PUBLIC_REPO_VERIFIED`
