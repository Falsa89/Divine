# 205D — FRONTEND UI MVP

**Track**: D | **Verdict**: `TRACK_D_FRONTEND_GEAR_CAP_UI_MVP_READY`

## File

- `frontend/constants/gearCap.ts` (constants + helper)
- `frontend/components/GearCapBadge.tsx` (badge read-only)
- `frontend/app/gear-cap-test.tsx` (sandbox `/gear-cap-test`)

## Wiring

- Deeplink-only (`/gear-cap-test`).
- **NO** wiring in `home.tsx`, `menu.tsx`, `_layout.tsx`, `tower-of-the-hells.tsx`, `guide.tsx`.
- Safe area aware, back navigation via `router.back()`.
