# v105 — Backend Endpoint Inventory

**Pack**: `MEGA_RELEASE_ACCELERATION_54_v105_MASTER_REPO_DESIGN_CONSISTENCY_AUDIT`
**Source JSON**: `data/design/master_audit/v105_backend_endpoint_inventory_v1.json`

## Sintesi

- **29 routers** registrati (include `app.include_router(...)` in `server.py`).
- **262 endpoint unici** totali.
- **16 endpoint** sotto prefisso `/api/` (ingress-safe).
- **246 endpoint** senza prefisso `/api/` (raggiungibili solo via proxy dev interno).

## Categorie

| Category | Routers |
|---|---|
| runtime_battle | 1 (`battle_router`) |
| readonly_catalog | 3 (`game_router`, `sprite_router`, `v95_readonly_catalog_router`) |
| mutation_inventory | 1 (`items_router`) |
| server_profile | 2 (`server_profiles_router`, `v103_server_profiles_router` QA fallback) |
| auth | 3 (`v96_auth_router`, `auth_extra_router`, `provider_status_router`) |
| team_mutation | 1 (`v96_team_formation_router`) |
| admin_gdpr | 1 (`v98_admin_router`) |
| preview | 8 (housing, hero_elevation, gear_cap, gear_forge, material_raid, gem_socket, story_battle_instance, generic_visual_battle_runner, battle_replay) |
| safety_preview | 8 (gem_socket_commit, material_raid_claim, gear_forge_fusion, rune_scroll_talisman, artifact_upgrade, divine_weapon_upgrade, battle_pass_claim, mail_claim) |

## Critical findings

- **0 endpoint** accetta `server_id`.
- **0 endpoint** filtra/enforcza per `server_id`.
- **42 endpoint** mutano economia/inventario/team senza scoping per server.
- **8 safety_preview routers** — tutti dry-run, da promuovere a live canary in v111.
- **8 preview routers** — da convertire o rimuovere durante v108.
- Distribuzione `/api/` prefix non uniforme: solo 16/262 endpoint sono ingress-safe; gli altri 246 sono raggiungibili solo via dev proxy. Decisione architetturale richiesta.

## Critical endpoints

`/api/health`, `/api/login`, `/api/register`, `/api/user/profile`, `/api/user/heroes`, `/api/heroes`, `/api/team`, `/api/gacha/pull`, `/api/gacha/pull10`, `/api/server-profiles/list`, `/api/expo-connect`, `/api/admin/bots/status`, `/api/admin/bots/run-cycle`
