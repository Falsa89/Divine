# v105 — Mode Runtime Audit

**Pack**: `MEGA_RELEASE_ACCELERATION_54_v105_MASTER_REPO_DESIGN_CONSISTENCY_AUDIT`
**Source JSON**: `data/design/master_audit/v105_mode_runtime_audit_v1.json`

## Sintesi

24 modalità auditate:

| Status | Count |
|---|---|
| real | 6 |
| preview | 12 |
| catalog-only | 2 |
| auto-resolve | 1 (story) |
| safety_preview | 5 |
| disabled | 2 (guild_raid, world_boss) |

## Highlight P0

- **Story**: ancora auto-resolve via `/api/story/battle`. Richiede sostituzione con Battle Launch Contract (v107) e conversione runtime (v108).
- **Arena/PvP**: preview, no MMR, no matchmaking server-bound.
- **Tower**: catalog-only, no real runtime.
- **Material Raid**: 3 route preview duplicate (alpha, test, visual-preview).
- **Guild War**: preview, no scheduling, no MMR.

## Real runtime (6)

`gacha` (account-wide), `vip`, `shop`/`item-shop`, `soul-forge`, `synergy/faction`, `forge` (parziale).

## Required Fix Packs

- **v107** Battle Launch Contract + pre-battle-lobby unification
- **v108** Story/Tower/Arena/Boss/Training real runtime conversion
- **v109** Event/Live/Guild/Bot server-scoped runtime
- **v111** Economy live canary controlled
