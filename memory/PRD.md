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
