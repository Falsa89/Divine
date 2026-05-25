# 157A — Full Frontend Route & Menu Registry (Track A)

Verdetto: `TRACK_A_FULL_FRONTEND_ROUTE_AND_MENU_REGISTRY_READY`
File: `data/design/audit/full_repo/frontend_route_menu_registry_v1.json`

## Coverage
- 57 frontend routes (Expo Router file-based)
- 44 menu/tab entries
- Tag distribution:
  - PLAYER_SAFE: 17
  - LOCKED_PREVIEW: 9
  - DEV_ONLY: 2
  - LEGACY_LIVE: 29 (alta priorità di lock/audit)

## Note
- LOCKED_PREVIEW: safe-previews, artifacts-preview, housing-preview, status-codex, collection-synergies-preview, affinity-gifts-preview, divine-weapons-catalog, hero-skill-kits-catalog, hero-encyclopedia.
- DEV_ONLY: /sprite-test, /dev-combat-qa-lab.
- LEGACY_LIVE: routes che espongono mutazioni POST/PUT/PATCH/DELETE (gacha, artifacts, shop, battlepass, equipment, hero training, soul-forge, exclusive, ...).
