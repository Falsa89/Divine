# 151A — Track A: Core Mode Wiring Registry

**Verdict:** `TRACK_A_CORE_MODE_WIRING_REGISTRY_READY`
**Mode:** audit-only

## Modes registered (13)
| mode_id | category | frontend_status | backend_status | risk |
|---|---|---|---|---|
| home | core | WIRED | LIVE | LOW |
| heroes | core | WIRED | LIVE | LOW |
| hero_detail | core | DEEP_LINK_ONLY | LIVE | MEDIUM |
| team_formation | core | WIRED | LIVE | MEDIUM |
| combat | combat | WIRED | LIVE | **HIGH** |
| post_battle | combat | WIRED | LIVE | MEDIUM |
| gacha | economy | WIRED | LIVE | LOW |
| shop | economy | WIRED | LIVE | MEDIUM |
| battle_pass | economy | WIRED | LIVE | LOW |
| daily_hub | daily | WIRED | READ_ONLY | LOW |
| mail | core | WIRED | LIVE | LOW |
| achievements | core | WIRED | LIVE | LOW |
| events | daily | WIRED | LIVE | LOW |

## Key findings
- **combat.tsx 1848 LOC** — high maintenance risk; engine MD5 must never change.
- **Hero detail overlap**: 3 routes (`/hero-detail`, `/hero-viewer`, `/hero-encyclopedia`).
- **Team formation**: dual synergy endpoints v1 + v2.
- **Shop hub triad** (`/shop`, `/item-shop`, `/economy`) creates UX confusion.

## Audit constraints respected
0 DB writes • 0 backend changes • 0 frontend changes • 0 flag flips.
