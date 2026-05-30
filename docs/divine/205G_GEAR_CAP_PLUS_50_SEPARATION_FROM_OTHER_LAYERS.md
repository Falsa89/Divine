# 205G — SEPARATION FROM OTHER LAYERS

**Track**: G | **Verdict**: `TRACK_G_SEPARATION_FROM_OTHER_LAYERS_READY`

Il Gear Cap +50 è esplicitamente separato da:

- Hero Level, Star Up, Ascensione, Skill Upgrade, Costellazioni, Reincarnation, Hero Elevation
- Gemme, Rune/Scroll/Talisman, Artifact, Divine Weapon
- BP Delta, Combat formulas, Battle Engine
- Character Bible final_numbers
- Shop/IAP, Battle Pass, VIP
- Server profiles live

## File toccati da questo pack (additivi)

- `backend/routes/gear_cap_preview.py` (NEW)
- `backend/server.py` (solo include_router additivo)
- `frontend/constants/gearCap.ts` (NEW)
- `frontend/components/GearCapBadge.tsx` (NEW)
- `frontend/app/gear-cap-test.tsx` (NEW)
- `backend/scripts/validate_project_gear_cap_plus_50_runtime_v1.py` (NEW)
- `backend/scripts/run_hero_skill_kit_validator_suite.py` (1 tupla aggiunta nel blocco OPTIONAL)
- `data/design/gear_cap_plus_50/*.json` (NEW)
- `docs/divine/205*.md` (NEW)

Tutto il resto resta **intoccato**.
