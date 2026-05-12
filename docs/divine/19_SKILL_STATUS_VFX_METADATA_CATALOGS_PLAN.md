# RM1.25-B — Skill / Status / Icon / VFX Inert Metadata Catalogs

## Objective
Install inert JSON metadata catalogs that translate the approved Skill Data Schema v1.1, Status Effect Runtime Schema v1, Status Icon Bible v1, and VFX Modular Bible v1 into machine-readable design data.

This task is intentionally **non-runtime**. These JSON files must not be imported by battle logic, gacha, frontend combat UI, or roster activation code during this task.

## Files

- `data/design/skill_status_vfx_catalogs/skill_slot_progression_v1.json`
- `data/design/skill_status_vfx_catalogs/status_effect_catalog_v1.json`
- `data/design/skill_status_vfx_catalogs/status_icon_registry_v1.json`
- `data/design/skill_status_vfx_catalogs/vfx_modular_catalog_v1.json`
- `data/design/skill_status_vfx_catalogs/skill_schema_examples_v1.json`
- `backend/scripts/validate_skill_status_vfx_metadata_catalogs.py`

## Hard rules

- No DB writes.
- No migrations.
- No `--apply`.
- No `battle_engine.py` changes.
- No battle balance changes.
- No live skill/status/VFX/icon activation.
- No frontend HP bar changes.
- No gacha changes.
- No roster activation.
- Do not activate Borea.
- Do not modify legacy `borea`.

## Expected validator output

The validator should confirm:

- 7 official elements.
- 40 core statuses.
- 12 VFX types.
- Skill slot progression matches approved rarity structure.
- Every status has icon registry metadata.
- Every status has apply/persistent/expire/cleanse VFX refs.
- Examples include `presentation_flow` with source motion and target impact.

## Next phase after this task

After RM1.25-B is installed and validated, a future RM1.25-C may create frontend/backend type-only declarations or UI registry scaffolding. Runtime battle behavior must remain behind a future explicit task and feature flag.
