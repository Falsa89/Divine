# 250 — MEGA_ECONOMY_SAFETY_ACCELERATION_3_LOUD_SERVER_REGISTRATION_REPAIR_v39b

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_3_LOUD_SERVER_REGISTRATION_REPAIR_PACK_v39b`
**Parent v39**: `6093c4f3`
**Parent v38c**: `4c2398d6`
**Mode**: `PUBLIC_CONTENT_REPAIR_BACKEND_SERVER_REGISTRATION_ONLY_LOUD`

## Contesto

Il pack **v39** ha pubblicato correttamente:

- `backend/routes/artifact_upgrade_safety_preview.py`
- `backend/routes/divine_weapon_upgrade_safety_preview.py`
- design JSON, schema, guard policy, proof marker per entrambi i track
- `endgame_economy_safety_registry_v3.json`
- rollup marker, doc 247/248/249, validator Track A/B/Rollup
- 3 tuple OPTIONAL nel suite runner locale

Tuttavia la verifica GitHub successiva ha mostrato che il **raw public blob**
di `backend/server.py` continua a **non esporre** visibilmente:

- `artifact_upgrade_safety_preview_router`
- `divine_weapon_upgrade_safety_preview_router`

Le route file sono pubbliche, ma gli endpoint potrebbero non essere agganciati
all'app backend pubblica.

## Strategia v39b (LOUD)

Questo pack è un **public content repair** funzionale, **non** un suite-runner
sync-fix. Pattern identico a v38c per v38.

- Aggiunto un blocco diagnostico top-level **molto più grande**,
  banner-style, in `backend/server.py`, immediatamente sopra il blocco v39
  preesistente (che viene preservato per traceability storica).
- Il sentinel uppercase
  `PUBLIC_CONTENT_REPAIR_v39b_ARTIFACT_AND_DIVINE_WEAPON_SERVER_REGISTRATION_LOUD`
  è unico e altamente distinguibile a livello di hash del file.
- **Nessuna duplicazione**: le 2 `include_router(...)` esistono ESATTAMENTE
  una volta ciascuna (grep count = 1).

## Sentinel pubblici richiesti (verificati)

In `backend/server.py`:

- `PUBLIC_CONTENT_REPAIR_v39b_ARTIFACT_AND_DIVINE_WEAPON_SERVER_REGISTRATION_LOUD` ✅
- `artifact_upgrade_safety_preview_router` ✅
- `divine_weapon_upgrade_safety_preview_router` ✅
- `app.include_router(artifact_upgrade_safety_preview_router)` count=1 ✅
- `app.include_router(divine_weapon_upgrade_safety_preview_router)` count=1 ✅

## File NON modificati

- `backend/routes/artifact_upgrade_safety_preview.py`
- `backend/routes/divine_weapon_upgrade_safety_preview.py`
- `backend/routes/artifacts.py` (MD5 locked)
- `backend/routes/forge.py`
- `backend/routes/gear_forge_fusion_safety_preview.py`
- `backend/routes/rune_scroll_talisman_safety_preview.py`
- `backend/routes/gem_socket_preview.py`
- `backend/routes/material_raid_preview.py`
- `backend/routes/gem_socket_commit_safety_preview.py`
- `backend/routes/material_raid_claim_safety_preview.py`
- `backend/battle_engine.py`
- `backend/.env`
- `backend/scripts/run_hero_skill_kit_validator_suite.py`
- frontend (`battlepass.tsx`, `vip.tsx`, `combat.tsx`, `story.tsx`,
  `homeAssetsManifest.ts`)
- economy/gacha/BP/VIP/shop files
- Character Bible / hero final_numbers

## Invarianti di safety (invariati da v39)

- `db_writes = 0`
- `artifact_live_upgrade_enabled = false`
- `artifact_live_fusion_enabled = false`
- `artifact_live_pull_enabled = false`
- `artifact_bonus_activation_enabled = false`
- `artifact_mutation_enabled = false`
- `divine_weapon_live_unlock_enabled = false`
- `divine_weapon_live_upgrade_enabled = false`
- `divine_weapon_live_awakening_enabled = false`
- `divine_weapon_mutation_enabled = false`
- `hero_copy_consumption_enabled = false`
- `user_materials_mutation_enabled = false`
- `premium_users_gems_used = false`
- `materials_consumed = false`
- `currency_consumed = false`
- `reward_grant_enabled = false`
- `exp_grant_enabled = false`
- `bp_delta_runtime_enabled = false`
- `battle_engine_changed = false`
- `combat_story_home_routes_changed = false`
- `artifacts_legacy_route_changed = false`
- `character_bible_changed = false`
- `hero_final_numbers_changed = false`
- `validator_weakening = false`
- `fake_pass = false`
- `duplicate_router_registration = false`
- `suite_runner_sync_fix_attempted = false` (caveat noto accettato)

## Verdict atteso

Locale:
`MEGA_ECONOMY_SAFETY_ACCELERATION_3_LOUD_SERVER_REGISTRATION_REPAIR_v39b_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Pubblico (dopo sync GitHub):
`MEGA_ECONOMY_SAFETY_ACCELERATION_3_ARTIFACT_AND_DIVINE_WEAPON_HARDENING_FUNCTIONAL_PUBLIC_CONTENT_VERIFIED_WITH_SUITE_RUNNER_STALE_CAVEAT`
