# 151C — Track C: Legacy Route & Old Endpoint Detection

**Verdict:** `TRACK_C_LEGACY_ROUTE_AND_OLD_ENDPOINT_DETECTION_READY`
**Mode:** audit-only (no rename, no delete, no redirect)

## Legacy / duplicate backend endpoints (7)
| endpoint | source | replacement |
|---|---|---|
| `GET /api/servers` | routes/economy.py | `/api/server-profiles/select` (503) |
| `POST /api/server/select` | routes/economy.py | `/api/server-profiles/select` (503) |
| `GET /api/synergies/team` | routes/synergies.py | `/api/synergies/team_v2` |
| `GET /api/factions`, `POST /api/faction/join` | routes/guild.py | `/api/player-factions/v2/*` |
| `GET /api/exclusive-items`, `POST /api/exclusive-items/craft` | routes/raids.py | `/api/unique-items` |
| `GET /api/shops`, `POST /api/shops/buy` | routes/soul_forge.py | overlap with `/api/shop` |
| `POST /api/soul/forge` | routes/soul_forge.py | `/api/soul-forge` |

## Frontend route overlaps (5)
- `/hero-detail` vs `/hero-viewer` vs `/hero-encyclopedia`
- `/shop` vs `/item-shop` vs `/economy`
- `/artifacts` vs `/artifacts-preview`
- `/synergy-codex` vs `/collection-synergies-preview`
- `/sanctuary` vs `/select-home-hero` (sub-flow)

## Backend without frontend (6)
- `/api/forge/*`, `/api/runes/*`
- `/api/hoplite-reel`
- `/api/admin/*` (correctly hidden)
- `/api/affinity/gift-spend/_admin/*` (correctly hidden)
- `/api/hero-skill-kits/runtime/debug/*` (correctly hidden)

## Frontend without backend
0 detected.

## Audit constraints respected
0 deletions • 0 renames • 0 redirects • 0 file removals.
