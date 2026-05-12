# RM1.25-C — Skill / Status / Icon / VFX Read-Only Catalog API

## Objective
Expose the inert RM1.25-B metadata catalogs through read-only backend endpoints so designers and future frontend screens can inspect skill slot progression, status definitions, status icon metadata, VFX metadata, and skill schema examples.

This task is allowed to add a pure catalog loader and read-only route module. It must not connect any catalog to battle runtime or activate live skills/status/VFX/icons.

## Source catalogs
Use only the inert JSON files already installed under:

`/app/data/design/skill_status_vfx_catalogs/`

Expected files:
- `skill_slot_progression_v1.json`
- `status_effect_catalog_v1.json`
- `status_icon_registry_v1.json`
- `vfx_modular_catalog_v1.json`
- `skill_schema_examples_v1.json`

## Recommended implementation
- Create `/app/backend/utils/skill_status_vfx_catalog_loader.py`
- Create `/app/backend/routes/skill_status_vfx_catalogs.py`
- Register the route in `/app/backend/game_systems.py`

The loader must be read-only, deterministic, and safe. In-process caching is allowed. It must not import `battle_engine.py`, gacha, roster activation scripts, or frontend code.

## Proposed endpoints
- `GET /api/skill-status-vfx/catalogs/summary`
- `GET /api/skill-status-vfx/catalogs/skill-progression`
- `GET /api/skill-status-vfx/catalogs/status-effects`
- `GET /api/skill-status-vfx/catalogs/status-icons`
- `GET /api/skill-status-vfx/catalogs/vfx`
- `GET /api/skill-status-vfx/catalogs/skill-examples`

Optional safe query filters are allowed if implementation remains simple and read-only.

## Absolute restrictions
- No DB writes
- No migrations
- No `--apply`
- No `battle_engine.py` changes
- No battle balance changes
- No live skill activation
- No live status activation
- No live VFX activation
- No status icon UI activation
- No frontend HP bar changes
- No gacha changes
- No roster activation
- Do not activate Borea
- Do not modify legacy `borea`
- Do not edit Character Bible, kit JSON, or asset files

## Acceptance criteria
The implementation is successful only if:
- requirements validator passes;
- all new endpoints return 200;
- summary endpoint reports RM1.25-B expected counts;
- `/api/heroes` remains 100;
- Borea remains hidden/pending;
- there are no runtime behavior changes in battle/gacha/roster/frontend HP bar.
