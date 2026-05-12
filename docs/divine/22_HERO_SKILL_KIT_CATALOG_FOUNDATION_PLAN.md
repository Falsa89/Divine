# RM1.26-A — Hero Skill Kit Catalog Foundation

## Goal

Install inert/read-only hero skill kit catalogs for Divine RPG / Divine Waifus.

This task creates the first machine-readable foundation for official hero kits without connecting anything to battle runtime.

## Files

- `data/design/hero_skill_kits/hero_skill_kit_catalog_requirements_v1.json`
- `data/design/hero_skill_kits/hero_skill_kit_schema_v1.json`
- `data/design/hero_skill_kits/hero_skill_kits_5star_manifest_v1.json`
- `data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json`
- `backend/scripts/validate_hero_skill_kit_catalog_foundation.py`

## Scope

### 5★ launch_base

The 5★ file is a manifest shell for the 20 official native 5★ launch_base heroes.
It intentionally does not invent full machine-readable kit details in this task.
Before filling those details, use the approved consolidated 5★ skill design source.

### 6★ launch_base + Borea

The 6★ file contains approved direction summaries for the 12 native 6★ launch_base heroes plus `greek_borea` as extra premium.
These are still inert design catalogs, not live runtime kits.

## Safety

This task must not:
- modify DB
- run migrations
- touch battle_engine.py
- activate skills/status/VFX/icons
- modify HP bar
- modify gacha/roster/Borea/Bible/assets
- import these files into battle runtime

## Validator

Run:

```bash
python /app/backend/scripts/validate_hero_skill_kit_catalog_foundation.py
```

Expected PASS:
- 20 5★ entries
- 13 6★ entries
- Borea is `launch_extra_premium`
- all 6★ have all expected slots and divine_weapon_id
- no runtime flags active
