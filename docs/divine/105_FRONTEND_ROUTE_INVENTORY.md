# v105 — Frontend Route Inventory

**Pack**: `MEGA_RELEASE_ACCELERATION_54_v105_MASTER_REPO_DESIGN_CONSISTENCY_AUDIT`
**Source JSON**: `data/design/master_audit/v105_frontend_route_inventory_v1.json`

## Sintesi

96 file di rotte totali in `frontend/app`. Drift strutturale documentato: ~46 surface preview/QA/sandbox/test rappresentano ~48% del totale.

## Classificazione

| Classification | Count |
|---|---|
| PLAYER_FACING_READY | 9 |
| PLAYER_FACING_BROKEN | 14 |
| PREVIEW_ONLY | 36 |
| QA_ONLY | 10 |
| SANDBOX | 3 |
| NEEDS_ROUTING_DECISION | 20 |
| HIDDEN_INTENTIONAL | 2 |
| DEPRECATED | 2 |

## Player-facing READY (9)

`/`, `/login`, `/servers`, `/(tabs)/menu`, `/equipment`, `/artifacts`, `/sanctuary`, `/vip`, `/guide` (+ catalog routes readonly)

## Player-facing BROKEN (server scope o launch context mancante)

`/(tabs)/home`, `/(tabs)/heroes`, `/(tabs)/battle`, `/(tabs)/gacha`, `/combat`, `/pre-battle-lobby`, `/story`, `/tower`, `/pvp`, `/raid`, `/events`, `/guild`, `/inventory`, `/treasury`, `/shop`, `/battlepass`, `/mail`, `/friends`, `/dm`, `/plaza`, `/rankings`, `/cosmetics`, `/achievements`, `/daily-hub`, `/soul-forge`, `/select-home-hero`, `/player-faction`, `/hero-collection`, `/hero-detail`, `/hero-training`

## PREVIEW_ONLY (36)

Vedere lista completa in JSON. Esempi rappresentativi: `alpha-codex`, `alpha-guide`, `alpha-menu-preview`, `alpha-preview-hub`, `arena-visual-preview`, `boss-tower-alpha-loop-preview`, `event-arena-alpha-gate-preview`, `story-alpha-slice-preview`, `story-first-node-runtime-preview`, `visual-battle-preview-router`, etc.

## QA_ONLY (10)

`dev-combat-qa-lab`, `gear-cap-test`, `gear-forge-test`, `gem-socket-test`, `hero-elevation-test`, `live-announcements-qa`, `live-guild-qa-hub`, `live-mode-pre-entry-lobby`, `material-raid-test`, `sprite-test`

## NEEDS_ROUTING_DECISION (route duplicate / da consolidare)

- `tower` vs `tower-of-the-hells`
- `guild` vs `gvg`
- `economy` vs `treasury`
- `shop` vs `item-shop`
- `material-raid-alpha` vs `material-raid-test` vs `material-raid-visual-preview`
- `territory`, `exclusive` (clarify scope)

## Key findings

- 96 route files totali, ~48% drift (preview/qa/sandbox/test).
- Nessuna route player-facing legge `selected_server_id` (eccetto `servers.tsx`).
- `combat.tsx`, `story.tsx`, `tower.tsx`, `pvp.tsx`, `raid.tsx`, `hero-training.tsx` richiedono Battle Launch Contract (v107).
- `alpha-menu-preview` e `alpha-preview-hub` espongono accesso a preview routes — valutare hidden-gate.
