# 205F — LEGACY +20 MIGRATION DEBT

**Track**: F | **Verdict**: `TRACK_F_LEGACY_PLUS_20_MIGRATION_DEBT_READY`

## Stato attuale

`PREVIEW_ONLY_NO_LIVE_MIGRATION_YET`.

## Debt locations (mantenute apposta)

1. `data/design/hero_gear_progression_bible/D_gear_progression_bible_v1.json` —
   `gear_level_cap_legacy_to_replace: 20`. Debt marker storico, utile per audit.
2. `backend/scripts/validate_project_hero_gear_progression_bible_v1.py` —
   il validator OPTIONAL verifica che la Bible esponga **entrambi** cap=50 e legacy=20.

## Runtime debt locations

**ZERO** (audit track A).

## Migration steps (futuri)

1. Abilitare `GEAR_CAP_PLUS_50_PREVIEW_ENABLED=true` sul backend canary.
2. Soft-wire hero/equipment screens al constants `gearCap.ts` (preview badge).
3. Validazione API `0 ≤ gear_level ≤ GEAR_CAP_CANONICAL` prima di mutation (pack futuro).
4. Pack `PROJECT_GEAR_FORGE_FUSION_RUNTIME_PACK` aggancia la cost policy track E.
5. Pack di chiusura debt rimuove fisicamente `20` dalla Bible.
