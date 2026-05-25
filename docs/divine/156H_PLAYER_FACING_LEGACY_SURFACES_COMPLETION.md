# 156H — Player-Facing Legacy Surfaces Lock & Audit — Completion (Track H)

Verdetto globale: `PROJECT_PLAYER_FACING_LEGACY_SURFACES_LOCK_AND_AUDIT_READY`
Verdetto Track H: `TRACK_H_PLAYER_FACING_LEGACY_SURFACES_COMPLETION_READY`

## Verdetti per track
| Track | Verdetto |
|-------|----------|
| A | MOBILE_QA_AND_REPO_FINDINGS_CONSOLIDATION_READY |
| B | SAFE_PREVIEWS_NAVIGATION_ONLY_FIX_IMPLEMENTED_SAFE |
| C | ARTIFACT_CONSTELLATION_LIVE_SURFACE_AUDIT_READY_NOT_APPLIED |
| D | GACHA_RATE_SANITY_AND_BANNER_GUARD_AUDIT_READY |
| E | SHOP_AND_IAP_READINESS_AUDIT_READY |
| F | BATTLE_PASS_LEGACY_SURFACE_AND_MONETIZATION_AUDIT_READY |
| G | OWNED_HEROES_LEGACY_VISIBILITY_AND_MENU_DEV_ROUTES_AUDIT_READY |
| H | COMPLETION_READY |

## File toccati
- `frontend/app/safe-previews.tsx` (md5: `2473947c7c692ddc61c70082f82bdb65` → `e40dd47e489561bfcfcbee3acfc90758`)

## MD5 invariants (preservati)
- `backend/battle_engine.py`: `151ca35ad3bc35f0a6209cb3744ed440`
- `backend/.env`: `ff60bbb79efa329b71aa8ed351ea89b3`

## DB / API / Flags
- 0 DB writes
- 0 backend changes
- 0 nuove chiamate API
- 0 flag flips
- 0 nuovi bottoni live

## Prossimi pack raccomandati (ordine priorità)
1. `PROJECT_GACHA_RATE_SANITY_FIX_OR_LOCK_PACK`
2. `PROJECT_ARTIFACT_CONSTELLATION_SURFACE_LOCK_PACK`
3. `PROJECT_SHOP_IAP_DESIGN_AND_SAFE_SHOP_LOCK_PACK`
4. `PROJECT_BATTLE_PASS_SURFACE_MODERNIZATION_PACK`
5. `PROJECT_HERO_LIST_LEGACY_OWNED_VISIBILITY_FIX_PACK`
6. `PROJECT_MENU_DEV_ROUTE_HARDENING_PACK`
7. `PROJECT_FRONTEND_D_COMBAT_UI_DECOMPOSITION_AUDIT_PACK`

## Rischi residui
- `/artifacts` live ancora esposto dal menu
- Banner gacha artifact/constellation ancora visibili
- Premium gacha rates 30% combinato (dev/test-like)
- Shop/Battle Pass espongono claim/buy live senza IAP
- Hero list non filtra legacy owned

## Stima progresso (escl. grafica/audio/art)
- pre: 56.0% → post: 56.4% (+0.4pp)
