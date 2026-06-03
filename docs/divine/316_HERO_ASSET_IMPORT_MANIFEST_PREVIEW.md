# 316 — Hero Asset Import Manifest Preview

Pack: `MEGA_RELEASE_ACCELERATION_MASTER_BATCH_EXECUTION_PLAN_PACK_v54`
Track: C
Tag: `PUBLIC_SYNC_TAG_v54_MEGA_RELEASE_ACCELERATION_MASTER_BATCH_EXECUTION_PLAN`

Scanner **read-only** di `frontend/assets/heroes/` che produce un manifest preview.

## Stati di readiness
- `ready_to_import`
- `missing_required_asset`
- `missing_optional_asset`
- `needs_manual_review`
- `rejected_wrong_contract`

## Slot richiesti
splash, portrait, card, detail, fullscreen, combat_base

## Slot opzionali
idle_sheet, attack_sheet, skill_sheet, hit_sheet, death_sheet, battle_animations_json, metadata

## Garanzie
- nessuna copia di asset
- nessuna mutation di `frontend/assets/heroes/`
- nessun tocco a Character Bible / final_numbers
- se la directory non esiste → scaffold + istruzioni drop-pack

Output: `data/design/assets/hero_asset_import_manifest_preview_v1.json`
