# 205I — RELEASE GATES AND ROLLBACK

**Track**: I | **Verdict**: `TRACK_I_RELEASE_GATES_AND_ROLLBACK_READY`

## Gates

| ID | Label                                            | Status                                            |
|----|--------------------------------------------------|---------------------------------------------------|
| R1 | Preview locale (questo pack)                     | ACHIEVED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING      |
| R2 | Envelope preview attivabile (interno canary)     | DEFERRED_TO_FUTURE_PACK                           |
| R3 | Forge runtime live (mutation reale)              | DEFERRED_TO_FUTURE_PACK                           |

## Rollback plan

1. Rimuovere `include_router(gear_cap_preview_router)` da `backend/server.py`.
2. Cancellare `backend/routes/gear_cap_preview.py`.
3. Rimuovere i tre file frontend (`constants/gearCap.ts`, `components/GearCapBadge.tsx`, `app/gear-cap-test.tsx`).
4. Rimuovere la tupla di registrazione validator dalla suite runner.
5. Rimuovere `data/design/gear_cap_plus_50/*` e `docs/divine/205*.md`.
6. La **Bible D** (`D_gear_progression_bible_v1.json`) NON viene mai toccata.
