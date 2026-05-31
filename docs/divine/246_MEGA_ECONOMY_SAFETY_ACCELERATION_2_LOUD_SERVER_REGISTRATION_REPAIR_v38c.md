# 246 — MEGA_ECONOMY_SAFETY_ACCELERATION_2_LOUD_SERVER_REGISTRATION_REPAIR_v38c

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_2_LOUD_SERVER_REGISTRATION_REPAIR_PACK_v38c`
**Parent v38**: `97d74515`
**Parent v38b**: `189b09a1`
**Mode**: `PUBLIC_CONTENT_REPAIR_BACKEND_SERVER_REGISTRATION_ONLY_LOUD`

## Contesto

Il pack **v38** ha pubblicato correttamente le 2 route file:
- `backend/routes/gear_forge_fusion_safety_preview.py`
- `backend/routes/rune_scroll_talisman_safety_preview.py`

più registry, design, schema, guard policy, proof marker, doc, validator e
suite tuple OPTIONAL.

Il pack **v38b** ha pubblicato marker e doc per il repair della
registrazione router in `backend/server.py`, ma la verifica GitHub successiva
ha mostrato che il **raw public blob** di `backend/server.py` continuava a
**non esporre** visibilmente:

- `PUBLIC_CONTENT_REPAIR_v38b_GEAR_FORGE_AND_RUNE_SERVER_REGISTRATION`
- `gear_forge_fusion_safety_preview_router`
- `rune_scroll_talisman_safety_preview_router`

Il marker v38b reclamava la riparazione, ma il blob pubblico era ancora
stale.

## Strategia v38c (LOUD)

Questo pack è un **public content repair** funzionale, **non** un suite-runner
sync-fix.

- Aggiunto un blocco diagnostico top-level **molto più grande**,
  banner-style, in `backend/server.py`, immediatamente sopra il blocco v38b
  preesistente (che viene preservato per traceability storica).
- Il sentinel uppercase `PUBLIC_CONTENT_REPAIR_v38c_GEAR_FORGE_AND_RUNE_SERVER_REGISTRATION_LOUD`
  è unico e altamente distinguibile a livello di hash del file.
- **Nessuna duplicazione**: le 2 `include_router(...)` esistono ESATTAMENTE
  una volta ciascuna (grep count = 1).

## Sentinel pubblici richiesti (verificati)

In `backend/server.py`:

- `PUBLIC_CONTENT_REPAIR_v38c_GEAR_FORGE_AND_RUNE_SERVER_REGISTRATION_LOUD` ✅
- `gear_forge_fusion_safety_preview_router` ✅
- `rune_scroll_talisman_safety_preview_router` ✅
- `app.include_router(gear_forge_fusion_safety_preview_router)` count=1 ✅
- `app.include_router(rune_scroll_talisman_safety_preview_router)` count=1 ✅

## File NON modificati

- `backend/routes/gear_forge_fusion_safety_preview.py`
- `backend/routes/rune_scroll_talisman_safety_preview.py`
- `backend/routes/forge.py`
- `backend/routes/equipment.py` (se presente)
- `backend/routes/gem_socket_preview.py`
- `backend/routes/material_raid_preview.py`
- `backend/routes/gem_socket_commit_safety_preview.py`
- `backend/routes/material_raid_claim_safety_preview.py`
- `backend/battle_engine.py`
- `backend/.env`
- `backend/routes/artifacts.py`
- `backend/scripts/run_hero_skill_kit_validator_suite.py`
- frontend (`battlepass.tsx`, `vip.tsx`, `combat.tsx`, `story.tsx`,
  `homeAssetsManifest.ts`)
- economy/gacha/BP/VIP/shop files
- Character Bible / hero final_numbers

## Invarianti di safety (invariati da v38/v38b)

- `db_writes = 0`
- `gear_forge_live_commit_enabled = false`
- `rune_scroll_talisman_live_commit_enabled = false`
- `gear_mutation_enabled = false`
- `rune_inventory_mutation_enabled = false`
- `hero_rune_slot_mutation_enabled = false`
- `user_materials_mutation_enabled = false`
- `premium_users_gems_used = false`
- `materials_consumed = false`
- `currency_consumed = false`
- `reward_grant_enabled = false`
- `exp_grant_enabled = false`
- `bp_delta_runtime_enabled = false`
- `battle_engine_changed = false`
- `combat_story_home_routes_changed = false`
- `validator_weakening = false`
- `fake_pass = false`
- `duplicate_router_registration = false`
- `suite_runner_sync_fix_attempted = false` (caveat noto accettato)

## Verdict atteso

Locale:
`MEGA_ECONOMY_SAFETY_ACCELERATION_2_LOUD_SERVER_REGISTRATION_REPAIR_v38c_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Pubblico (dopo sync GitHub):
`MEGA_ECONOMY_SAFETY_ACCELERATION_2_GEAR_FORGE_AND_RUNE_HARDENING_FUNCTIONAL_PUBLIC_CONTENT_VERIFIED_WITH_SUITE_RUNNER_STALE_CAVEAT`
