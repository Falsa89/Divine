# 182B — Route & Backend Inventory Audit

**Track:** B — Route & Backend Inventory Audit
**Verdict:** `TRACK_B_ROUTE_AND_BACKEND_INVENTORY_AUDIT_READY`
**Pack:** `PROJECT_FULL_RUNTIME_FEATURE_REALITY_AUDIT_WITH_TEST_ASSET_REGISTRY`

## Frontend
- **Totale route `.tsx`:** 55
- **Tab routes (5):** home, battle, gacha, heroes, menu
- **Stack player-facing:** 29 route (story, combat, hero-collection, treasury, inventory, equipment, economy, cosmetics, achievements, daily-hub, events, mail, friends, dm, plaza, rankings, servers, player-faction, select-home-hero, exclusive, guild, gvg, raid, pvp, tower, territory, sanctuary, artifacts, hero-training, hero-detail, hero-viewer)
- **Stack locked (4):** `shop.tsx` (`SHOP_LOCKED_V2`), `item-shop.tsx` (`ITEM_SHOP_LOCKED_V2`), `battlepass.tsx` (`BP_LOCKED_V2` + `BP_PREMIUM_BUY_LOCKED_V2`), `vip.tsx` (`VIP_LOCKED_V2`)
- **Preview/internal (5):** artifacts-preview, affinity-gifts-preview, collection-synergies-preview, housing-preview, safe-previews
- **Dev/catalog (8):** dev-combat-qa-lab, divine-weapons-catalog, hero-encyclopedia, hero-skill-kits-catalog, skill-status-vfx-catalogs, sprite-test, status-codex, synergy-codex

## Backend
- **Totale route file:** 33
- **Totale endpoint stimato:** ~191
- **Endpoint con writes:** 18 file
- **File con stamina_violation:** **5** (combat.py, cosmetics.py, economy.py, gvg.py, raids.py) ⚠️
- **Frontend file con stamina_violation:** **5** (events.tsx, gvg.tsx, shop.tsx, tower.tsx, treasury.tsx)

### Top route per endpoint count
| File | Endpoints | Writes | Note |
|---|---|---|---|
| `hero_progression.py` | 15 | ✅ | player-facing |
| `social.py` | 14 | ✅ | player-facing |
| `economy.py` | 14 | ✅ | include VIP/BP endpoints gated, stamina violation |
| `artifacts.py` | 12 | ❌ | POST mutations HTTP 423; banner hidden; canary internal |
| `combat.py` | 11 | ✅ | stamina violation |
| `soul_forge.py` | 10 | ✅ | inline confirm panel functional |
| `forge.py` | 9 | ✅ | |
| `heroes.py` | 8 | ✅ | |
| `sanctuary.py` | 7 | ❌ | design preview / readonly |
| `affinity_gifts.py` | 6 | ❌ | preview/read-only |
| `cosmetics.py` | 5 | ✅ | stamina violation |
| `raids.py` | 5 | ✅ | stamina violation |
| `gvg.py` | 4 | ✅ | stamina violation, canonical mismatch |

### Backend core files
- `server.py` — FastAPI app + auth + global wiring
- `battle_engine.py` — Combat resolver (MD5 LOCKED `151ca3...`)
- `battle_core.py` — Lower-level combat math
- `bot_system.py` — PvE bot generation
- `game_systems.py` — Game systems orchestration
- `synergy_system.py` — Synergy resolver

## Counts riassuntivi
```
total_frontend_routes              = 55
total_backend_route_files          = 33
total_backend_endpoints_estimated  = 191
endpoints_with_writes              = 18
locked_frontend_routes             = 4
preview_internal_routes            = 5
dev_catalog_routes                 = 8
stamina_violation_backend_files    = 5  ⚠️
stamina_violation_frontend_files   = 5  ⚠️
```

## Verdict
`TRACK_B_ROUTE_AND_BACKEND_INVENTORY_AUDIT_READY` — Inventario completo. 5+5 stamina violations identificate per Track D. Zero code changes.
