# 207D — FRONTEND UI MVP

**Track**: D | **Verdict**: `TRACK_D_FRONTEND_FORGE_UI_MVP_READY`

## File

- `frontend/constants/gearForge.ts` (constants + helper)
- `frontend/app/gear-forge-test.tsx` (sandbox `/gear-forge-test`)

## Wiring

- Deeplink-only (`/gear-forge-test`).
- **NO** wiring in `home.tsx`, `menu.tsx`, `_layout.tsx`, `tower-of-the-hells.tsx`, `guide.tsx`, `forge.tsx`/`equipment.tsx`.
- Safe area aware, back navigation via `router.back()`.

## Schermata

- Lista 4 subsystem con stato runtime esplicito.
- Lista 6 qualità canoniche.
- Box informativo con feature flag, default 503, fusion commit DISABLED.
