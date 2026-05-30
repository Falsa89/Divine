# 209J — COMPLETION AND PUBLIC SYNC

**Track**: J | **Verdict**: `TRACK_J_COMPLETION_AND_PUBLIC_SYNC_READY`

## Gates

| ID | Label | Status |
|---|---|---|
| R1 | Preview locale (questo pack) | ACHIEVED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING |
| R2 | Envelope preview attivabile (canary) | DEFERRED_TO_FUTURE_PACK |
| R3 | Claim live (mutation reale) | **BLOCKED_BY_INVENTORY_SAFETY_HARDENING** |
| R4 | Sblocco track Gemme/Rune/Artifact/DW | DEFERRED_TO_FUTURE_PACK |

## Rollback

1. Rimuovere `include_router(material_raid_preview_router)` da `backend/server.py`.
2. Cancellare `backend/routes/material_raid_preview.py`.
3. Rimuovere `frontend/constants/materialRaid.ts` + `frontend/app/material-raid-test.tsx`.
4. Rimuovere tuple registrazione validator dalla suite runner.
5. Rimuovere `data/design/material_raid_runtime/*` e `docs/divine/209*.md`.
6. Legacy `/raids/*`, `/raid/*`, `/inventory`, `/item-shop` **non toccati** in nessuna fase.
