# 215 — PROJECT_GEM_SOCKET_RUNTIME_SERVER_REGISTRATION_SYNC_FIX_v27c

## Scopo

Micro-pack di solo sync per risolvere l'ultimo blocker pubblico residuo sul push v27/v27b del `PROJECT_GEM_SOCKET_RUNTIME_PACK`.

## Contesto

Dopo la verifica della main pubblica successiva al v27b:

- `backend/scripts/run_hero_skill_kit_validator_suite.py` risulta correttamente aggiornato su GitHub (contiene `PUBLIC_SYNC_TAG_v27_GEM_SOCKET_RUNTIME`, `PUBLIC_SYNC_TAG_RESYNC_v27b_GEM_SOCKET_RUNTIME`, `GEM_SOCKET_RUNTIME_REGISTRATION_SENTINEL`, tupla parent + `validate_project_gem_socket_runtime_v1.py`).
- `backend/server.py` pubblico **NON** mostra ancora la registrazione del router preview Gem Socket: mancavano i due token canonici.

Lo stato locale del container era già corretto (righe 544-545 originali), quindi questo pack aggiunge esclusivamente il sentinel `PUBLIC_SYNC_TAG_RESYNC_v27c_GEM_SOCKET_SERVER_REGISTRATION` insieme al blocco di commento v27c richiesto, per forzare GitHub a riconoscere il blob come modificato in fase di Save to GitHub.

## Modifiche eseguite (scope strettissimo)

1. `backend/server.py` (UNICO file modificato):
   - Aggiunto sentinel di commento: `# PUBLIC_SYNC_TAG_RESYNC_v27c_GEM_SOCKET_SERVER_REGISTRATION`.
   - Aggiunto blocco di commento esplicativo v27c (preview-only, no DB writes, no live commit, gear sockets ≠ Rune scroll/talisman, ≠ premium currency `users.gems`).
   - **Nessuna duplicazione** di `from routes.gem_socket_preview import ...` o `app.include_router(gem_socket_preview_router)` (preesistenti, ora circondati dai sentinel).
   - **Nessuna modifica** ad altre route registrations, gacha, auth, seed, battle, economy.

2. Creati:
   - `data/design/gem_socket_runtime/gem_socket_runtime_server_registration_sync_fix_v27c_marker_v1.json` — proof marker v27c.
   - `docs/divine/215_GEM_SOCKET_RUNTIME_SERVER_REGISTRATION_SYNC_FIX_v27c.md` — questo documento.

## File NON toccati (forbidden scope)

- `backend/routes/gem_socket_preview.py`
- `backend/scripts/validate_project_gem_socket_runtime_v1.py`
- `backend/scripts/run_hero_skill_kit_validator_suite.py` (locale già a posto, non modificato)
- `frontend/app/gem-socket-test.tsx`, `frontend/constants/gemSocket.ts`
- `backend/routes/forge.py`, `backend/routes/equipment.py`, `backend/routes/material_raid_preview.py`
- `backend/battle_engine.py`, `backend/.env`, `backend/routes/artifacts.py`
- `frontend/app/battlepass.tsx`, `frontend/app/vip.tsx`, `frontend/app/combat.tsx`
- gacha / shop / BP / VIP / IAP / economy / Artifact / Divine Weapon / Rune runtime / Character Bible / hero final_numbers

## Garanzie

- `db_writes` = 0
- `runtime_semantics_changed` = false
- `live_socket_commit_enabled` = false
- `gear_mutation_enabled` = false
- `premium_gems_currency_used` = false
- `material_spend_enabled` = false
- `rune_runtime_changed` = false
- `material_raid_behavior_changed` = false
- `battle_runtime_changed` = false
- `economy_changed` = false
- MD5 invarianti su `battle_engine.py`, `.env`, `artifacts.py`, `battlepass.tsx`, `vip.tsx` → invariate.

## Verdict atteso

- Locale: `PROJECT_GEM_SOCKET_RUNTIME_SERVER_REGISTRATION_SYNC_FIX_v27c_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`
- Pubblico (dopo Save to GitHub + verifica): `PROJECT_GEM_SOCKET_RUNTIME_PREVIEW_COMPLETE_PUBLIC_REPO_VERIFIED`
