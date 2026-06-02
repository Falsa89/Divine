# 300 — Asset Import Readiness (~40 Heroes)

**Pack**: `MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION_PACK_v51`
**Track**: D
**Public Sync Tag**: `PUBLIC_SYNC_TAG_v51_MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION`
**Contract**: `hero_asset_import_readiness_schema_v1`

## Scopo
Definire lo schema di readiness per l'import futuro di ~40 eroi completi,
senza importare alcun asset reale in v51.

## Required asset slots (20)
hero_id, rarity, faction, element, role,
splash, portrait, card, detail, fullscreen,
combat_base,
idle_sheet, attack_sheet, skill_sheet, hit_sheet, death_sheet,
battle_animations_json,
source_reference_notes, chroma_status, alpha_cleanup_status

## Categorie di readiness
- `ready_to_import`
- `missing_non_blocking_metadata`
- `missing_required_asset`
- `needs_manual_review`
- `rejected_wrong_contract`

## Drop zone (per l'utente, quando avrà il pack)
- `data/staging/hero_asset_pack/<hero_id>/`
- Naming: `<hero_id>__<slot>.<ext>`
- File: `battle_animations.json` per metadati frame/durata

## Garanzie
- Nessun asset reale importato in v51.
- `frontend/assets/heroes` UNCHANGED.
- Hero contracts / Character Bible / final_numbers UNCHANGED.
- Il validator deve passare anche con zero scaffold (nessun eroe ancora droppato).
