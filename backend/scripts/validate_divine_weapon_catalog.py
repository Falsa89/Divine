#!/usr/bin/env python3
"""
RM1.27-A — Divine Weapon Catalog Foundation Validator

Reads:
  - /app/data/design/divine_weapons/divine_weapon_schema_v1.json
  - /app/data/design/divine_weapons/divine_weapons_catalog_v1.json
  - /app/data/design/divine_weapons/divine_weapon_requirements_v1.json

Validates 32 hard rules from the RM1.27-A prompt and prints PASS / FAIL.
Exit code: 0 = PASS, 1 = FAIL.

Read-only / inert / catalog-only. Does NOT touch DB, runtime, battle, gacha,
roster, Borea visibility, or any asset.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

BASE = Path('/app/data/design/divine_weapons')
SCHEMA_PATH = BASE / 'divine_weapon_schema_v1.json'
CATALOG_PATH = BASE / 'divine_weapons_catalog_v1.json'
REQS_PATH = BASE / 'divine_weapon_requirements_v1.json'

EXPECTED_HERO_IDS_LAUNCH_BASE = [
    'greek_athena', 'greek_artemis', 'greek_gaia', 'primordial_nyx',
    'japanese_raijin', 'japanese_susanoo', 'japanese_amaterasu',
    'egyptian_sekhmet', 'mesopotamian_tiamat', 'egyptian_isis',
    'celtic_morrigan', 'cursed_pestilence_horseman',
]
EXPECTED_HERO_IDS_EXTRA = ['greek_borea']
BOREA_DIVINE_WEAPON_ID = 'borea_wings_of_the_north_wind'
REQUIRED_PROGRESSION_STATES = [
    'sealed', 'dormant', 'awakened', 'empowered', 'blessed', 'ascendant', 'divine'
]
DORMANT_PLUS = REQUIRED_PROGRESSION_STATES[1:]

failures: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def load_json(path: Path) -> dict:
    if not path.exists():
        fail(f'Missing file: {path}')
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        fail(f'Invalid JSON in {path}: {e}')
        return {}


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    catalog = load_json(CATALOG_PATH)
    reqs = load_json(REQS_PATH)
    if failures:
        return _emit()

    records = catalog.get('records', [])
    # 1. Exactly 13 records
    if len(records) != 13:
        fail(f'[1] Expected 13 Divine Weapon records, got {len(records)}')

    # 2/3. Split 12 launch_base + 1 launch_extra_premium
    base = [r for r in records if r.get('release_group') == 'launch_base']
    extra = [r for r in records if r.get('release_group') == 'launch_extra_premium']
    if len(base) != 12:
        fail(f'[2] Expected 12 launch_base, got {len(base)}')
    if len(extra) != 1:
        fail(f'[3] Expected 1 launch_extra_premium, got {len(extra)}')

    # 4. Extra premium must be greek_borea
    if not extra or extra[0].get('hero_id') != 'greek_borea':
        fail('[4] Extra premium must be greek_borea')

    # 5. greek_borea must have divine_weapon_id = borea_wings_of_the_north_wind
    if extra and extra[0].get('divine_weapon_id') != BOREA_DIVINE_WEAPON_ID:
        fail(f'[5] greek_borea divine_weapon_id must be {BOREA_DIVINE_WEAPON_ID}, '
             f'got {extra[0].get("divine_weapon_id")}')

    # 6. Every hero_id is unique
    hids = [r.get('hero_id') for r in records]
    if len(set(hids)) != len(hids):
        fail('[6] Duplicate hero_id found in catalog')

    # 7. Every divine_weapon_id is unique
    wids = [r.get('divine_weapon_id') for r in records]
    if len(set(wids)) != len(wids):
        fail('[7] Duplicate divine_weapon_id found in catalog')

    # 8. All expected hero IDs exist in catalog
    expected_all = set(EXPECTED_HERO_IDS_LAUNCH_BASE + EXPECTED_HERO_IDS_EXTRA)
    missing = expected_all - set(hids)
    if missing:
        fail(f'[8] Missing expected hero IDs: {sorted(missing)}')

    # 9. No legacy `borea` hero_id
    if 'borea' in hids:
        fail('[9] Legacy hero_id `borea` present (use greek_borea)')

    # Per-record checks
    for r in records:
        hid = r.get('hero_id', '?')

        # 10. native_rarity_required = 6
        if r.get('native_rarity_required') != 6:
            fail(f'[10] {hid}: native_rarity_required != 6')

        # 11. exclusive_to_hero = true
        if r.get('exclusive_to_hero') is not True:
            fail(f'[11] {hid}: exclusive_to_hero != true')

        # 12. catalog_status = catalog_only
        if r.get('catalog_status') != 'catalog_only':
            fail(f'[12] {hid}: catalog_status != catalog_only')

        # 13. runtime_attached = false
        if r.get('runtime_attached') is not False:
            fail(f'[13] {hid}: runtime_attached != false')

        # 14. battle_runtime_attached = false
        if r.get('battle_runtime_attached') is not False:
            fail(f'[14] {hid}: battle_runtime_attached != false')

        sf = r.get('safety_flags', {})

        # 15. vfx_runtime_attached = false if present
        if 'vfx_runtime_attached' in sf and sf['vfx_runtime_attached'] is not False:
            fail(f'[15] {hid}: safety_flags.vfx_runtime_attached != false')

        # 16. balance_values_finalized = false
        if r.get('balance_values_finalized') is not False:
            fail(f'[16] {hid}: balance_values_finalized != false')

        # 17. final_numbers null where present
        def check_final_numbers_null(items, label):
            for it in items or []:
                if 'final_numbers' in it and it['final_numbers'] is not None:
                    fail(f'[17] {hid}: {label} entry has non-null final_numbers')
        check_final_numbers_null(r.get('effect_tracks'), 'effect_tracks')
        check_final_numbers_null(r.get('material_requirements'), 'material_requirements')

        # 18. progression states sealed..divine in order
        ps = r.get('progression_states', [])
        keys = [p.get('state_key') for p in ps]
        if keys != REQUIRED_PROGRESSION_STATES:
            fail(f'[18] {hid}: progression_states keys/order mismatch: {keys}')

        # 19. sealed.has_gameplay_bonus = false
        sealed = next((p for p in ps if p.get('state_key') == 'sealed'), {})
        if sealed.get('has_gameplay_bonus') is not False:
            fail(f'[19] {hid}: sealed.has_gameplay_bonus != false')

        # 20. sealed.has_battle_presence_layer = false
        if sealed.get('has_battle_presence_layer') is not False:
            fail(f'[20] {hid}: sealed.has_battle_presence_layer != false')

        # 21. dormant+ has_gameplay_bonus = true
        for sk in DORMANT_PLUS:
            st = next((p for p in ps if p.get('state_key') == sk), {})
            if st.get('has_gameplay_bonus') is not True:
                fail(f'[21] {hid}: {sk}.has_gameplay_bonus != true')

        # 22. dormant+ has_battle_presence_layer = true
        for sk in DORMANT_PLUS:
            st = next((p for p in ps if p.get('state_key') == sk), {})
            if st.get('has_battle_presence_layer') is not True:
                fail(f'[22] {hid}: {sk}.has_battle_presence_layer != true')

        ur = r.get('unlock_requirements', {})
        # 23. required_hero_star_level = 10
        if ur.get('required_hero_star_level') != 10:
            fail(f'[23] {hid}: unlock_requirements.required_hero_star_level != 10')

        # 24. break_seal_required = true
        if ur.get('break_seal_required') is not True:
            fail(f'[24] {hid}: unlock_requirements.break_seal_required != true')

        # 25. material requirements support same_element_copy AND specific_hero_copy
        mats = r.get('material_requirements', [])
        mtypes = {m.get('material_type') for m in mats}
        if 'same_element_copy' not in mtypes:
            fail(f'[25] {hid}: missing material_type same_element_copy')
        if 'specific_hero_copy' not in mtypes:
            fail(f'[25] {hid}: missing material_type specific_hero_copy')

        dpl = r.get('divine_presence_layer', {})
        # 26. enabled_from_state = dormant
        if dpl.get('enabled_from_state') != 'dormant':
            fail(f'[26] {hid}: divine_presence_layer.enabled_from_state != dormant')
        # 27. disabled_in_state = sealed
        if dpl.get('disabled_in_state') != 'sealed':
            fail(f'[27] {hid}: divine_presence_layer.disabled_in_state != sealed')
        # 28. requires_new_sprite_sheet = false
        if dpl.get('requires_new_sprite_sheet') is not False:
            fail(f'[28] {hid}: divine_presence_layer.requires_new_sprite_sheet != false')
        # 29. divine_presence_layer.runtime_attached = false
        if dpl.get('runtime_attached') is not False:
            fail(f'[29] {hid}: divine_presence_layer.runtime_attached != false')

        # 30. safety_flags.catalog_only = true
        if sf.get('catalog_only') is not True:
            fail(f'[30] {hid}: safety_flags.catalog_only != true')

        # 31. safety_flags.borea_activation_allowed = false for all (and Borea)
        if sf.get('borea_activation_allowed') is not False:
            fail(f'[31] {hid}: safety_flags.borea_activation_allowed != false')

        # 32. No record implies roster/gacha/battle activation
        if sf.get('gacha_attached') is not False:
            fail(f'[32] {hid}: safety_flags.gacha_attached != false')
        if sf.get('roster_activation_attached') is not False:
            fail(f'[32] {hid}: safety_flags.roster_activation_attached != false')
        if sf.get('battle_runtime_attached') is not False:
            fail(f'[32] {hid}: safety_flags.battle_runtime_attached != false')
        if sf.get('hp_bar_runtime_attached') is not False:
            fail(f'[32] {hid}: safety_flags.hp_bar_runtime_attached != false')

    # Reqs sanity (only soft check)
    if reqs.get('counts', {}).get('total_divine_weapons') != 13:
        warnings.append('requirements.counts.total_divine_weapons != 13')

    # Schema sanity (only soft check)
    if not schema.get('record_required_fields'):
        warnings.append('schema.record_required_fields is empty')

    return _emit(records, base, extra)


def _emit(records=None, base=None, extra=None) -> int:
    if failures:
        print('FAIL: Divine Weapon Catalog Foundation (RM1.27-A)')
        for f in failures:
            print(f'  - {f}')
        if warnings:
            print('Warnings:')
            for w in warnings:
                print(f'  ! {w}')
        return 1

    print('PASS: Divine Weapon Catalog Foundation (RM1.27-A) validated')
    if records is not None:
        print(f'  total Divine Weapons: {len(records)}')
        print(f'  launch_base:          {len(base)}')
        print(f'  launch_extra_premium: {len(extra)} (greek_borea)')
        borea = extra[0] if extra else {}
        print(f'  Borea divine_weapon_id: {borea.get("divine_weapon_id")}')
        print(f'  Borea catalog_status:   {borea.get("catalog_status")}')
        print(f'  Borea activation_allowed: {borea.get("safety_flags", {}).get("borea_activation_allowed")}')
        print('  All hero IDs verified:')
        for hid in sorted([r.get('hero_id') for r in records]):
            print(f'    - {hid}')
        print('  All records: native_rarity_required=6, exclusive_to_hero=true, catalog_only.')
        print('  All records: runtime_attached=false, battle_runtime_attached=false, '
              'hp_bar_runtime_attached=false, vfx_runtime_attached=false.')
        print('  sealed = no gameplay bonus and no battle presence (verified for all).')
        print('  dormant+ = gameplay/design hook and battle presence metadata (verified for all).')
        print('  Divine Presence Layer: enabled_from_state=dormant, requires_new_sprite_sheet=false, '
              'runtime_attached=false.')
        print('  10★ seal-break requirement: verified.')
    if warnings:
        print('Warnings:')
        for w in warnings:
            print(f'  ! {w}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
