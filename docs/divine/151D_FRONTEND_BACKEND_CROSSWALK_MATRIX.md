# 151D — Track D: Frontend↔Backend Crosswalk Matrix

**Verdict:** `TRACK_D_FRONTEND_BACKEND_CROSSWALK_MATRIX_READY`
**Mode:** audit-only

## Summary
- 43 frontend routes auditati
- 1 route con legacy endpoint usato (`/servers`)
- 24 route con live mutations (player-facing, esistenti pre-audit)
- 19 route pure read-only
- 0 endpoint mancanti

## High-risk crosswalk entries
| frontend | backend | legacy_used | exposes_live_action |
|---|---|---|---|
| `/servers` | `/api/servers` + `POST /api/server/select` | **YES** | YES |
| `/artifacts` | `/api/artifacts/pull` + `/api/constellations/equip` | NO | YES (gated by 5 sig) |
| `/combat` | `/api/story/battle` etc | NO | YES (intentional gameplay) |

## Pure read-only routes (audit-safe)
`/safe-previews`, `/daily-hub`, `/artifacts-preview`, `/housing-preview`, `/status-codex`, `/collection-synergies-preview`, `/synergy-codex`, `/divine-weapons-catalog`, `/hero-skill-kits-catalog`, `/skill-status-vfx-catalogs`, `/sprite-test`, `/dev-combat-qa-lab`, `/rankings`, `/dm`, `/events`, `/hero-encyclopedia`, `/affinity-gifts-preview`, `/hero-detail`, `/hero-collection`.

## Audit constraints respected
0 endpoint replacements • 0 mutations performed • 0 DB writes.
