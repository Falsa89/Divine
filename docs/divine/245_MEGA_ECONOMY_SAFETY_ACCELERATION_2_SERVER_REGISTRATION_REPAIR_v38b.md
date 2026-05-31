# 245 — MEGA_ECONOMY_SAFETY_ACCELERATION_2_SERVER_REGISTRATION_REPAIR_v38b

**Parent pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_2_GEAR_FORGE_AND_RUNE_HARDENING_PACK_v38`
**Parent commit**: `97d74515`
**Mode**: `PUBLIC_CONTENT_REPAIR_BACKEND_SERVER_REGISTRATION_ONLY`

## Contesto

Il pack v38 era completo localmente: route, design JSON, schema, guard policy,
proof marker, doc, validator e suite tuple OPTIONAL erano tutti presenti e
verificati. Tuttavia la verifica pubblica su GitHub ha rilevato che
`backend/server.py` pubblico **non includeva visibilmente** le due
registrazioni router:

- `gear_forge_fusion_safety_preview_router`
- `rune_scroll_talisman_safety_preview_router`

Le route file erano pubbliche, ma gli endpoint potevano non essere agganciati
all'app backend pubblica. Questo è un **public content repair** funzionale,
**non** un suite-runner sync-fix.

## Scope strettissimo

- Modifica solo `backend/server.py` aggiungendo un sentinel comment blob
  esplicito + ribadendo le 2 imports + 2 `app.include_router(...)`.
- Creato marker:
  `data/design/economy_safety/mega_economy_safety_acceleration_2_server_registration_repair_v38b_marker_v1.json`
- Creato questo doc (245).

## Sentinel pubblico richiesto

`backend/server.py` ora contiene visibilmente:

- `PUBLIC_CONTENT_REPAIR_v38b_GEAR_FORGE_AND_RUNE_SERVER_REGISTRATION`
- `gear_forge_fusion_safety_preview_router` (import + include_router)
- `rune_scroll_talisman_safety_preview_router` (import + include_router)

## File NON modificati (verificati)

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
- `frontend/app/battlepass.tsx`
- `frontend/app/vip.tsx`
- `frontend/app/combat.tsx`
- `frontend/app/story.tsx`
- `frontend/constants/homeAssetsManifest.ts`
- `backend/scripts/run_hero_skill_kit_validator_suite.py` (nessun sync-fix v38c)

## Invarianti di safety (invariati rispetto a v38)

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
- `economy_changed = false`
- `gacha_changed = false`
- `bp_vip_shop_changed = false`
- `battle_engine_changed = false`
- `combat_story_home_routes_changed = false`

## Verdict atteso

Locale:
`MEGA_ECONOMY_SAFETY_ACCELERATION_2_SERVER_REGISTRATION_REPAIR_v38b_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Pubblico (dopo sync GitHub):
`MEGA_ECONOMY_SAFETY_ACCELERATION_2_GEAR_FORGE_AND_RUNE_HARDENING_FUNCTIONAL_PUBLIC_CONTENT_VERIFIED_WITH_SUITE_RUNNER_STALE_CAVEAT`
