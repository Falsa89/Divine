# 417 — Hero Asset Dry-run + Manifest Readiness

**Pack:** `MEGA_RELEASE_ACCELERATION_18_v69`

## File
- `data/design/assets/hero_asset_dryrun_manifest_contract_v1.json`
- `data/design/assets/hero_asset_expected_folder_schema_v1.json`
- `data/design/assets/hero_asset_readiness_matrix_v1.json`
- `data/design/assets/hero_asset_import_forbidden_scope_v1.json`
- `backend/scripts/hero_asset_dryrun_manifest_scanner_v1.py` (read-only)

## Slot attesi per ogni hero_id
`splash`, `no_background`, `combat_base`, `idle_sheet` (idle.png), `attack_sheet` (attack.png), `skill_sheet` (skill.png), `hit_sheet` (hit.png), `death_sheet` (death.png), opzionale `chibi_home_later`.

## Scanner
- Read-only. Argomento `--path` opzionale.
- Se path assente o non valido, produce placeholder readiness report con `scan_executed=false`.
- Output JSON: readiness matrix, missing assets per hero, naming issues, duplicate hero_id warnings.

## Divieti
Nessun import reale di asset, nessuna copia di file, nessun overwrite, nessuna modifica di Character Bible / hero roster / final_numbers / asset runtime resolver. Nessun uso di PIL/OpenCV. Nessun image processing.
