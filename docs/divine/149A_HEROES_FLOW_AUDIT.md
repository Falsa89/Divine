# 149A — HEROES COLLECTION & HERO DETAIL FLOW AUDIT

## Track A — `PROJECT_FRONTEND_B_TRACK_A`

**Verdict:** `TRACK_A_HEROES_COLLECTION_AND_HERO_DETAIL_FLOW_AUDIT_READY`

## Routes auditate (7)

- `/(tabs)/heroes` (506 LOC)
- `/hero-collection` (383 LOC)
- `/hero-detail` (743 LOC)
- `/hero-viewer`, `/hero-encyclopedia`, `/hero-training`, `/select-home-hero`

## Flow steps (7)

1. Tab Heroes → lista eroi posseduti (`GET /api/user/heroes`)
2. Filtro/sort client-side
3. Tap eroe → hero-detail (`GET /api/heroes/{id}`)
4. Stats, skill, lore, evolution
5. Hero-training (livellamento, ascendenza)
6. Hero-viewer 3D/sprite
7. Set main hero (`POST /api/user/main-hero`)

## Gap identificati (4)

| Gap | Severity |
|---|---|
| Empty/loading skeleton non uniformi tra hero-collection e tab heroes | medium |
| hero-detail 743 LOC, candidato a estrazione componenti | low_refactor |
| Mancanza breadcrumb hero-detail → evolution/training | medium |
| hero-collection vs heroes tab: ruoli sovrapposti | low |

## Validator

`validate_project_frontend_b_heroes_flow_audit_v1.py` → **PASS**.
