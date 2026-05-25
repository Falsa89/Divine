# 160C — Backend/Frontend Wiring Matrix Refresh (Track C)

Verdetto: `TRACK_C_BACKEND_FRONTEND_WIRING_MATRIX_REFRESH_READY`
File: `data/design/audit/alignment_fix/backend_frontend_wiring_matrix_v1.json`

## Snapshot
- 57 frontend routes
- 117 frontend API callsites (49 mutating, post V2 lock)
- 219 backend endpoints

## Distribution stati
- LIVE: 10
- LOCKED: 5
- LOCKED_PREVIEW: 1
- PREVIEW: 2
- GUARDED_DESTRUCTIVE: 1 (soul_forge)
- DEV_HIDDEN: 2
- NEEDS_FIX: 1 (/exclusive)
- MISSING_BACKEND: 6 (announcements, maintenance, patch notes, banner, live feed, push)
- PARTIAL: 1 (red-dot)
