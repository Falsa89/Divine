# 158F — Menu Dev/Legacy Route Hardening (Track F)

Verdetto: `TRACK_F_MENU_DEV_LEGACY_ROUTE_HARDENING_IMPLEMENTED_SAFE`
File: `frontend/app/(tabs)/menu.tsx`

## Voci rimosse dal menu player
- `Sprite Test` (`/sprite-test`) — dev-only
- `Combat QA Lab (DEV)` (`/dev-combat-qa-lab`) — dev-only

Entrambi i file route restano in repo per QA interno via deep link, ma non sono più raggiungibili dalla UI player.

## Voce reindirizzata
- `Artefatti & Costellazioni`: `/artifacts` (live) → `/artifacts-preview` (locked safe)

## Vincoli
- 0 cancellazioni di file route
- 0 backend changes
- 0 DB writes
- 0 menu entries rimossi che siano player-facing safe (heroes, battle, gacha, shop, BP, VIP, eventi, ecc. restano)
