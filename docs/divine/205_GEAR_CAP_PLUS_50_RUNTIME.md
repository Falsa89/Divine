# 205 — PROJECT_GEAR_CAP_PLUS_50_RUNTIME

**Verdict**: `PROJECT_GEAR_CAP_PLUS_50_RUNTIME_PREVIEW_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

**Timestamp UTC**: 2026-05-30T10:00:00Z

**Runtime mode**: `PREVIEW_ONLY` (DISABLED-BY-DEFAULT — HTTP 503 inert envelope)

**Feature flag**: `GEAR_CAP_PLUS_50_PREVIEW_ENABLED`

---

## Cosa fa questo pack

Fase 1 dalla **Bible 202 (track D)**. Pubblica il *contract shape* e gli stage canonici
del nuovo **Gear Cap +50** in modalità **preview-only**:

- 4 stage canonici: **Avvio (0-10)**, **Intermedio (11-20)**, **Avanzato (21-35)**, **Endgame (36-50)**.
- Cap legacy **+20** documentato come *debt/migration point*, mai cancellato in questo pack.
- 6 slot canonici: `weapon`, `armor`, `helm`, `boots`, `gloves`, `accessory`.
- Cost policy preview design-only (replace_before_release = true).

## Cosa NON fa

- **NO** mutation runtime, **NO** DB writes, **NO** materiali spesi, **NO** gold spent.
- **NO** modifiche a Hero Elevation, Gemme, Rune, Artifact, Divine Weapon, BP Delta.
- **NO** modifiche a `battle_engine.py`, `combat.tsx`, Character Bible, hero `final_numbers`.
- **NO** Shop/BP/VIP/IAP unlock, **NO** server profiles live, **NO** gacha/pity changes.
- **NO** modifiche a `_layout.tsx`, `home.tsx`, `menu.tsx`, `tower-of-the-hells.tsx`,
  `guide.tsx`, `hero-elevation-test.tsx`, `soul-forge.tsx`, `equipment.tsx`.
- **NO** REQUIRED/OPTIONAL validator weakening, **NO** fake PASS.

## Audit hardcoded `+20`

Audit completo (track A) ha trovato **ZERO** superfici runtime attive che dipendono dal
cap legacy `+20`. Le uniche occorrenze del valore `20` sono:

1. `data/design/hero_gear_progression_bible/D_gear_progression_bible_v1.json` →
   campo `gear_level_cap_legacy_to_replace: 20`. **MANTENUTO** come debt marker.
2. `backend/scripts/validate_project_hero_gear_progression_bible_v1.py` →
   verifica strutturale che la Bible esponga cap=50 + legacy=20. **MANTENUTO**.

Non è stato modificato alcun file di backup o binario.

## Surface aggiunte da questo pack

### Backend

- `backend/routes/gear_cap_preview.py` (NEW)
  - `GET  /api/gear-cap/tiers`
  - `GET  /api/gear-cap/preview-tiers` (alias)
  - `GET  /api/gear-cap/{hero_id}/preview`
  - `POST /api/gear-cap/{hero_id}/upgrade/preview`
- `backend/server.py` → aggiunto **solo** `include_router(gear_cap_preview_router)`.

### Frontend

- `frontend/constants/gearCap.ts` (NEW) — `GEAR_CAP_CANONICAL`, `GEAR_CAP_LEGACY_TO_REPLACE`,
  `GEAR_STAGED_CAPS`, `GEAR_SLOTS`, `resolveGearStage(level)`.
- `frontend/components/GearCapBadge.tsx` (NEW) — badge read-only.
- `frontend/app/gear-cap-test.tsx` (NEW) — sandbox `/gear-cap-test` (deeplink-only).

### Validator

- `backend/scripts/validate_project_gear_cap_plus_50_runtime_v1.py` (NEW, OPTIONAL).
- Suite runner: tupla aggiunta a `run_hero_skill_kit_validator_suite.py` nel blocco OPTIONAL.

### Design assets

- `data/design/gear_cap_plus_50/A_..I_*.json` (9 tracks) + proof marker.

## Release gates

- **R1** (questo pack): preview locale, flag default off. ✅ ACHIEVED LOCAL CONTAINER (public sync pending).
- **R2** (futuro): envelope preview attivabile in canary (`GEAR_CAP_PLUS_50_PREVIEW_ENABLED=true`).
- **R3** (futuro): runtime live tramite `PROJECT_GEAR_FORGE_FUSION_RUNTIME_PACK` + `PROJECT_MATERIAL_RAID_RUNTIME_PACK`.

## Rollback

Vedi `data/design/gear_cap_plus_50/I_release_gates_and_rollback_v1.json` per il piano completo.
La Bible D resta intatta a prescindere.

## Tracks dedicati

- [205A_RUNTIME_SURFACE_AUDIT.md](./205A_GEAR_CAP_PLUS_50_RUNTIME_SURFACE_AUDIT.md)
- [205B_CONSTANTS_AND_SCHEMA.md](./205B_GEAR_CAP_PLUS_50_CONSTANTS_AND_SCHEMA.md)
- [205C_BACKEND_CONTRACT_PREVIEW.md](./205C_GEAR_CAP_PLUS_50_BACKEND_CONTRACT_PREVIEW.md)
- [205D_FRONTEND_UI_MVP.md](./205D_GEAR_CAP_PLUS_50_FRONTEND_UI_MVP.md)
- [205E_MATERIAL_COST_POLICY.md](./205E_GEAR_CAP_PLUS_50_MATERIAL_COST_POLICY.md)
- [205F_LEGACY_PLUS_20_MIGRATION_DEBT.md](./205F_GEAR_CAP_PLUS_50_LEGACY_PLUS_20_MIGRATION_DEBT.md)
- [205G_SEPARATION_FROM_OTHER_LAYERS.md](./205G_GEAR_CAP_PLUS_50_SEPARATION_FROM_OTHER_LAYERS.md)
- [205H_GUIDE_CODEX_AND_TUTORIAL_LINKS.md](./205H_GEAR_CAP_PLUS_50_GUIDE_CODEX_AND_TUTORIAL_LINKS.md)
- [205I_RELEASE_GATES_AND_ROLLBACK.md](./205I_GEAR_CAP_PLUS_50_RELEASE_GATES_AND_ROLLBACK.md)
