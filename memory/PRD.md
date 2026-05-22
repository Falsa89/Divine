# Divine Waifus - PRD

## Overview
Idle auto-battle RPG gacha mobile game featuring 2D HD graphics.
Characters are gods, heroes, and mythological beasts reimagined as anime girls.

## Core Features
- Grid combat (9x9, 6 characters per team)
- Auto-battle with speed controls (Hokage Crisis style)
- Active/passive skills and ultimate moves
- Gacha system with multiple banners
- Team formation with positional buffs
- Equipment and inventory
- Guild/Faction system
- Community Plaza

## Technical Stack
- Frontend: Expo (React Native) with expo-router
- Backend: FastAPI + MongoDB
- Landscape orientation
- File-based routing

## Combat System (Hokage Crisis Style)
- Turn-based auto-battle
- 6v6 on 9x9 grid
- Position zones: Front (DEF+HP), Mid (ATK+SPD), Back (CRIT)
- Formation patterns give bonus buffs
- NAD (Normal Attack), SAD (Strong Attack), SP (Ultimate)
- Element system: fire, water, earth, wind, light, dark
- Status effects: burn, freeze, stun, poison, bleed, slow
- Ultimate moves with cinematic cut-in animation

---

## SLC-C — Single-Shard → Multi-Shard Migration Plan (2026-05-21) ✅ PASS (DESIGN-ONLY)

Design-only / read-only / dry-run plan to evolve from `user_id`-keyed
single-shard model to `(account_id, server_id)` multi-shard.

**No DB writes. No runtime/route changes. No Borea exposure. No AF2-N drift.**

- 11 JSON design contracts in `/app/data/design/server_lifecycle/`
- 14 Python validators/audits/simulators in `/app/backend/scripts/`
- Final doc: `/app/docs/divine/93_SLC_C_MULTISHARD_MIGRATION_PLAN.md`
- Suite globale: pass=258, fail=0, miss=0
- `execution_ready=false`, `second_server_opening_allowed=false`
- AF2-N intact: cap=50000, allowlist=2500
- `/api/heroes`=100; `primordial_gaia`=404; borea/greek_borea
  catalog-only stato pre-esistente documentato come baseline (non
  introdotto da SLC-C)

---

## SLC-BE — Server Profile Creation + Selection Contract (2026-05-22) ✅ PASS (DESIGN-ONLY / CONTRACT-ONLY)

Foundation contracts for future multi-server runtime: server profile
creation, server selection endpoints, active server resolution, new-player
routing, server status policy, dry-run scenarios, runtime safety audit,
readiness rollup.

**No DB writes. No runtime route creation. No auth changes. No UI.**

- 8 JSON design contracts (server_lifecycle/ + system_safety/)
- 11 Python validators/audits in `/app/backend/scripts/`
- Final doc: `/app/docs/divine/94_SLC_BE_SERVER_PROFILE_SELECTION_CONTRACT.md`
- Suite globale: pass=269, fail=0, miss=0 (11 nuovi OPTIONAL aggiunti)
- SLC-C combo regression: ancora 14/14 PASS
- `runtime_enabled=false`, `db_write=false`, `migration_applied=false`,
  `second_server_opening_allowed=false`, `borea_safe=true`,
  `af2n_invariant_intact=true`
- AF2-N invariato: cap=50000, allowlist=2500
- 7 blockers documentati prima di runtime enable
- 4 future feature flags tutti `false`

---

## LIVE-MODES-RECONCILIATION-A + SLC-NEXT-PREP-A (2026-05-22) ✅ PASS (DESIGN-ONLY)

Riconciliazione definitiva delle 16 modalità live/special di Divine Waifus con benchmark corretti + piano SLC-Next design-only post SLC-BE.

**No DB writes. No runtime route creation. No UI. No battle/gacha/roster changes. No AF2-N drift.**

- 11 JSON design (7 live_modes/ + 3 server_lifecycle/ + 1 system_safety/)
- 10 script Python (8 validator + 1 audit + 1 combo) in `/app/backend/scripts/`
- Final doc: `/app/docs/divine/95_LIVE_MODES_RECONCILIATION_AND_SLC_NEXT_A.md`
- Suite globale: pass=278, fail=0, miss=0 (9 nuovi OPTIONAL)
- Mapping corretti: Troni dell'Eclissi (not_present), Giudizio di Asgard (not_present), Titanomachia (Protect Seireitei)
- Sanctuary Housing solo design note
- SLC-F/G/D/H tutti execute_now=false
- AF2-N intatto: cap=50000, allowlist=2500
- 7 blocker documentati a `slc_next_runtime_allowed=false`

---

## BENCHMARK-CANONICAL-SOURCE-OF-TRUTH-A (2026-05-22) ✅ PASS (DESIGN-ONLY)

Fonte canonica interna al progetto per tutte le decisioni benchmark-derived (non solo 16 modalità).

**No DB writes. No runtime route creation. No UI. No battle/gacha/roster/catalog changes. No AF2-N drift.**

- 13 JSON design canonical in `/app/data/design/benchmark_canonical/`
- 14 script Python (13 validator + 1 audit + 1 combo) in `/app/backend/scripts/`
- 4 doc MD in `/app/docs/divine/` (96_BENCHMARK_CANONICAL_SOURCE_OF_TRUTH.md + 3 sources verbatim dal pack)
- Suite globale: pass=292, fail=0, miss=0 (14 nuovi OPTIONAL)
- Copertura: 16 live modes · server lifecycle/calendar/merge · event hub/daily guide · summon/pity/fragments/wishlist · cosmetics/skins/titles/furniture · Sanctuary Housing · guild/social/co-op · tower/castle/roguelike · equipment/relic/forge · battle stats/reporting · monetized events guardrails · benchmark risk policy
- SLC-F come prossimo checkpoint design-only (execute_now=false)
- Hard invariants confermati: AF2-N cap=50000, allowlist=2500, primordial_gaia=404, borea hidden from /api/heroes, second_server_opening_allowed=false

---

## SLC-F — Server-Aware Route Patch Dry-Run Canonical (2026-05-22) ✅ PASS (DESIGN-ONLY)

Inventario, risk matrix, patch contract, dry-run simulation, validators e
audit per preparare la futura migrazione server-aware delle route, senza
toccare il runtime.

**No DB writes. No runtime route implementation. No UI. No battle/gacha/roster changes. No AF2-N drift.**

- 9 JSON design (8 server_lifecycle/ + 1 system_safety/)
- 11 script Python (9 validator/audit + 1 simulator + 1 combo) in `/app/backend/scripts/`
- Doc: `/app/docs/divine/97_SLC_F_ROUTE_PATCH_DRYRUN_CANONICAL.md`
- Suite globale: pass=302, fail=0, miss=0 (10 nuovi OPTIONAL)
- Combo SLC-F: 9/9 PASS
- Route inventory: 30 family classificate (0 unsafe_unknown), 343 user_id refs totali
- Collection matrix: 19 collections con future key strategy
- Endpoint patch contract: 14 endpoint (NOT implemented; AF2-N + heroes catalog protected)
- Legacy S1 compat: default_legacy_server_id=s1, backfill_executed=false
- Risk matrix: 11 rischi (5 P0, 4 P1, 2 P2) tutti con mitigation
- Runtime safety: protected files SHA-256 match, 0 leak future routes, 0 multishard cols in DB
- 7 blockers documentati a runtime_patch_applied=false
- AF2-N intatto: cap=50000, allowlist=2500
- API smoke: /api/heroes=100, primordial_gaia=404, borea/greek_borea baseline immutato
