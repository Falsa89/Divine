# 151E — Track E: Unreachable Implemented Mode Audit

**Verdict:** `TRACK_E_UNREACHABLE_IMPLEMENTED_MODE_AUDIT_READY`
**Mode:** audit-only (no menu changes)

## Findings (10)
### Frontend (7)
- `/affinity-gifts-preview` — locked preview esiste, **non in menu né hub**.
- `/hero-viewer` — deep-link only, duplicato di `/hero-detail`.
- `/hero-encyclopedia` — sub-flow intenzionale di hero detail.
- `/synergy-codex` — deep-link only, possibile sovrapposizione con `/collection-synergies-preview`.
- `/select-home-hero` — sub-flow di `/sanctuary` (intenzionale).
- `/combat` — entered da modalità battaglia (intenzionale).
- `/index` — gate route (intenzionale).

### Backend (3)
- `/api/forge/*` e `/api/runes/*` — nessuna route frontend dedicata.
- `/api/hoplite-reel` — endpoint legacy probabile orfano.
- `/api/affinity/gift-spend` (canary) — dry-run senza UI player.

## Classification legend
- **player_visible_now**: []
- **locked_preview**: `/artifacts-preview`, `/housing-preview`, `/status-codex`, `/affinity-gifts-preview`, `/collection-synergies-preview`
- **dev_admin_only**: `/dev-combat-qa-lab`, `/sprite-test`
- **intentional_hidden**: `/select-home-hero`, `/combat`, `/index`
- **should_be_removed_later**: []
- **should_be_linked_by_future_pack**: `/affinity-gifts-preview`

## Critical issues: 0

## Audit constraints respected
0 menu changes • 0 route changes.
