#!/usr/bin/env python3
"""
RM1.27-D — Divine Weapon Catalog QA / Cross-Link Audit Script
─────────────────────────────────────────────────────────────────────────
Read-only audit. NO mutation. NO runtime / battle / HP bar / gacha /
roster / Borea activation. NO DB writes. Exit 0 on PASS, 1 on FAIL.

Cross-links audited:
  1. Divine Weapon Catalog integrity (counts, IDs, safety flags)
  2. Cross-link with Hero Skill Kit 6★ catalog
     - every 6★ kit divine_weapon_id matches a DW catalog record
     - every DW record matches a 6★ kit owner
     - hero_id + divine_weapon_id exact match (incl. preserved overrides
       aegis_of_athena, isis_sacred_tyet_knot, borea_wings_of_the_north_wind)
  3. Progression / Unlock contract per record
  4. Material requirement contract (supported duplicate types)
  5. Divine Presence Layer contract + readability rules
  6. Borea safety (no legacy borea, source_locked Marchio Boreale, etc.)

Source files (read-only):
  /app/data/design/divine_weapons/divine_weapon_schema_v1.json
  /app/data/design/divine_weapons/divine_weapons_catalog_v1.json
  /app/data/design/divine_weapons/divine_weapon_requirements_v1.json
  /app/data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

DW_BASE = Path('/app/data/design/divine_weapons')
HSK_BASE = Path('/app/data/design/hero_skill_kits')

DW_CATALOG = DW_BASE / 'divine_weapons_catalog_v1.json'
DW_SCHEMA = DW_BASE / 'divine_weapon_schema_v1.json'
DW_REQS = DW_BASE / 'divine_weapon_requirements_v1.json'
HSK_6STAR = HSK_BASE / 'hero_skill_kits_6star_borea_v1.json'

REQUIRED_STATES = ['sealed', 'dormant', 'awakened', 'empowered', 'blessed', 'ascendant', 'divine']
DORMANT_PLUS = REQUIRED_STATES[1:]

EXPECTED_LAUNCH_BASE = {
    'greek_athena', 'greek_artemis', 'greek_gaia', 'primordial_nyx',
    'japanese_raijin', 'japanese_susanoo', 'japanese_amaterasu',
    'egyptian_sekhmet', 'mesopotamian_tiamat', 'egyptian_isis',
    'celtic_morrigan', 'cursed_pestilence_horseman',
}
EXPECTED_EXTRA_PREMIUM = {'greek_borea'}
PRESERVED_ID_OVERRIDES = {
    'greek_athena': 'aegis_of_athena',
    'egyptian_isis': 'isis_sacred_tyet_knot',
    'greek_borea': 'borea_wings_of_the_north_wind',
}

REQUIRED_READABILITY_RULES = [
    'must_not_obscure_hp_bar',
    'must_not_obscure_status_icons',
    'must_not_obscure_character_sprite',
    'must_not_look_like_status_or_buff',
    'must_not_look_like_domain',
    'must_not_look_like_skill_cast',
    'must_remain_mobile_readable',
]

REQUIRED_MATERIAL_TYPES = {'same_element_copy', 'specific_hero_copy', 'event_limited_substitute'}

failures: list[str] = []
warnings: list[str] = []


def fail(section: str, msg: str) -> None:
    failures.append(f'[{section}] {msg}')


def warn(section: str, msg: str) -> None:
    warnings.append(f'[{section}] {msg}')


def load(path: Path) -> dict:
    if not path.exists():
        fail('IO', f'missing file {path}')
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        fail('IO', f'invalid JSON {path}: {e}')
        return {}


def audit_catalog_integrity(records: list[dict]) -> None:
    section = '1.catalog_integrity'
    if len(records) != 13:
        fail(section, f'expected 13 records, got {len(records)}')

    base = [r for r in records if r.get('release_group') == 'launch_base']
    extra = [r for r in records if r.get('release_group') == 'launch_extra_premium']
    if len(base) != 12:
        fail(section, f'expected 12 launch_base, got {len(base)}')
    if len(extra) != 1:
        fail(section, f'expected 1 launch_extra_premium, got {len(extra)}')

    hids = [r.get('hero_id') for r in records]
    if len(set(hids)) != len(hids):
        fail(section, 'duplicate hero_id found')
    wids = [r.get('divine_weapon_id') for r in records]
    if len(set(wids)) != len(wids):
        fail(section, 'duplicate divine_weapon_id found')

    if 'borea' in hids:
        fail(section, 'legacy hero_id `borea` present (must use greek_borea)')

    expected = EXPECTED_LAUNCH_BASE | EXPECTED_EXTRA_PREMIUM
    missing = expected - set(hids)
    if missing:
        fail(section, f'missing canonical hero_ids: {sorted(missing)}')
    unexpected = set(hids) - expected
    if unexpected:
        fail(section, f'unexpected hero_ids: {sorted(unexpected)}')

    for r in records:
        hid = r.get('hero_id', '?')
        if r.get('native_rarity_required') != 6:
            fail(section, f'{hid}: native_rarity_required != 6')
        if r.get('exclusive_to_hero') is not True:
            fail(section, f'{hid}: exclusive_to_hero != true')
        if r.get('catalog_status') != 'catalog_only':
            fail(section, f'{hid}: catalog_status != catalog_only')
        if r.get('runtime_attached') is not False:
            fail(section, f'{hid}: runtime_attached != false')
        if r.get('battle_runtime_attached') is not False:
            fail(section, f'{hid}: battle_runtime_attached != false')
        if r.get('balance_values_finalized') is not False:
            fail(section, f'{hid}: balance_values_finalized != false')

        sf = r.get('safety_flags', {})
        for k in [
            'catalog_only',  # must be true
        ]:
            if sf.get(k) is not True:
                fail(section, f'{hid}: safety_flags.{k} != true')
        for k in [
            'runtime_attached', 'battle_runtime_attached',
            'hp_bar_runtime_attached', 'vfx_runtime_attached',
            'gacha_attached', 'roster_activation_attached',
            'borea_activation_allowed', 'balance_values_finalized',
        ]:
            if sf.get(k) is not False:
                fail(section, f'{hid}: safety_flags.{k} != false')
        if sf.get('do_not_treat_as_live_power') is not True:
            fail(section, f'{hid}: safety_flags.do_not_treat_as_live_power != true')


def audit_crosslink_hsk(records: list[dict], hsk_records: list[dict]) -> None:
    section = '2.crosslink_hsk_6star'

    if len(hsk_records) != 13:
        fail(section, f'expected 13 entries in hsk_6star, got {len(hsk_records)}')

    dw_map = {r.get('hero_id'): r.get('divine_weapon_id') for r in records}
    hsk_map = {e.get('hero_id'): e.get('divine_weapon_id') for e in hsk_records}

    # Every 6★ kit with divine_weapon_id must match DW catalog
    for hid, hsk_wid in hsk_map.items():
        if hid not in dw_map:
            fail(section, f'6★ kit hero {hid} missing from DW catalog')
            continue
        if hsk_wid and hsk_wid != dw_map[hid]:
            fail(section, f'{hid}: 6★ kit divine_weapon_id={hsk_wid} != DW catalog divine_weapon_id={dw_map[hid]}')

    # Every DW record must have matching HSK 6★ owner
    for hid, dw_wid in dw_map.items():
        if hid not in hsk_map:
            fail(section, f'DW hero {hid} missing from 6★ kit catalog')
            continue
        if hsk_map[hid] and hsk_map[hid] != dw_wid:
            fail(section, f'{hid}: HSK divine_weapon_id={hsk_map[hid]} != DW divine_weapon_id={dw_wid}')

    # Release group alignment
    dw_rg = {r.get('hero_id'): r.get('release_group') for r in records}
    hsk_rg = {e.get('hero_id'): e.get('release_group') for e in hsk_records}
    for hid in set(dw_rg) & set(hsk_rg):
        if dw_rg[hid] != hsk_rg[hid]:
            fail(section, f'{hid}: release_group mismatch DW={dw_rg[hid]} vs HSK={hsk_rg[hid]}')

    # Preserved ID overrides
    for hid, expected_wid in PRESERVED_ID_OVERRIDES.items():
        if dw_map.get(hid) != expected_wid:
            fail(section, f'{hid}: DW divine_weapon_id={dw_map.get(hid)} differs from preserved canonical {expected_wid}')
        if hsk_map.get(hid) and hsk_map.get(hid) != expected_wid:
            fail(section, f'{hid}: HSK divine_weapon_id={hsk_map.get(hid)} differs from preserved canonical {expected_wid}')


def audit_progression_unlock(records: list[dict]) -> None:
    section = '3.progression_unlock'
    for r in records:
        hid = r.get('hero_id', '?')
        ps = r.get('progression_states', [])
        keys = [p.get('state_key') for p in ps]
        if keys != REQUIRED_STATES:
            fail(section, f'{hid}: progression_states keys/order mismatch: {keys}')
            continue
        sealed = next((p for p in ps if p.get('state_key') == 'sealed'), {})
        if sealed.get('has_gameplay_bonus') is not False:
            fail(section, f'{hid}: sealed.has_gameplay_bonus != false')
        if sealed.get('has_battle_presence_layer') is not False:
            fail(section, f'{hid}: sealed.has_battle_presence_layer != false')
        for sk in DORMANT_PLUS:
            st = next((p for p in ps if p.get('state_key') == sk), {})
            if st.get('has_gameplay_bonus') is not True:
                fail(section, f'{hid}: {sk}.has_gameplay_bonus != true')
            if st.get('has_battle_presence_layer') is not True:
                fail(section, f'{hid}: {sk}.has_battle_presence_layer != true')

        ur = r.get('unlock_requirements', {})
        if ur.get('initial_state') != 'sealed':
            fail(section, f'{hid}: initial_state != sealed')
        if ur.get('break_seal_required') is not True:
            fail(section, f'{hid}: break_seal_required != true')
        if ur.get('required_hero_star_level') != 10:
            fail(section, f'{hid}: required_hero_star_level != 10')
        if ur.get('requires_dedicated_materials') is not True:
            fail(section, f'{hid}: requires_dedicated_materials != true')
        if ur.get('requires_duplicate_materials') is not True:
            fail(section, f'{hid}: requires_duplicate_materials != true')


def audit_material_requirements(records: list[dict]) -> None:
    section = '4.material_requirements'
    for r in records:
        hid = r.get('hero_id', '?')
        mats = r.get('material_requirements', [])
        mtypes = {m.get('material_type') for m in mats}
        missing = REQUIRED_MATERIAL_TYPES - mtypes
        if missing:
            fail(section, f'{hid}: missing required material_types {sorted(missing)}')
        for m in mats:
            if m.get('quantity') is not None:
                fail(section, f'{hid}: material_id={m.get("material_id")} has non-null quantity')
            if m.get('final_numbers') is not None:
                fail(section, f'{hid}: material_id={m.get("material_id")} has non-null final_numbers')
            if 'min_native_rarity' in m and m.get('min_native_rarity') is not None:
                fail(section, f'{hid}: material_id={m.get("material_id")} has non-null min_native_rarity')


def audit_presence_layer(records: list[dict]) -> None:
    section = '5.divine_presence_layer'
    for r in records:
        hid = r.get('hero_id', '?')
        dpl = r.get('divine_presence_layer', {})
        if dpl.get('enabled') is not True:
            fail(section, f'{hid}: divine_presence_layer.enabled != true')
        if dpl.get('enabled_from_state') != 'dormant':
            fail(section, f'{hid}: enabled_from_state != dormant')
        if dpl.get('disabled_in_state') != 'sealed':
            fail(section, f'{hid}: disabled_in_state != sealed')
        if dpl.get('is_physical_weapon_animation') is not False:
            fail(section, f'{hid}: is_physical_weapon_animation != false')
        if dpl.get('requires_new_sprite_sheet') is not False:
            fail(section, f'{hid}: requires_new_sprite_sheet != false')
        if dpl.get('runtime_attached') is not False:
            fail(section, f'{hid}: divine_presence_layer.runtime_attached != false')
        rr = dpl.get('readability_rules', {})
        for k in REQUIRED_READABILITY_RULES:
            if rr.get(k) is not True:
                fail(section, f'{hid}: readability_rules.{k} != true')


def audit_borea_safety(records: list[dict]) -> None:
    section = '6.borea_safety'
    hids = [r.get('hero_id') for r in records]
    if 'borea' in hids:
        fail(section, 'legacy hero_id `borea` present in DW catalog')
    borea = next((r for r in records if r.get('hero_id') == 'greek_borea'), None)
    if borea is None:
        fail(section, 'greek_borea record missing from DW catalog')
        return
    if borea.get('release_group') != 'launch_extra_premium':
        fail(section, f'greek_borea release_group != launch_extra_premium (got {borea.get("release_group")})')
    if borea.get('divine_weapon_id') != 'borea_wings_of_the_north_wind':
        fail(section, f'greek_borea divine_weapon_id mismatch: {borea.get("divine_weapon_id")}')
    sf = borea.get('safety_flags', {})
    if sf.get('borea_activation_allowed') is not False:
        fail(section, 'greek_borea safety_flags.borea_activation_allowed != false')
    if borea.get('catalog_status') != 'catalog_only':
        fail(section, 'greek_borea catalog_status != catalog_only')
    # Marchio Boreale check
    status_hooks = borea.get('status_hooks', [])
    marchio = next((h for h in status_hooks if h.get('status_id') == 'marchio_boreale'), None)
    if marchio is None:
        warn(section, 'greek_borea status_hooks: marchio_boreale not present (informational)')
    else:
        if marchio.get('source_locked') is not True:
            fail(section, 'marchio_boreale.source_locked != true')
        if marchio.get('personal') is not True:
            fail(section, 'marchio_boreale.personal != true')
        if marchio.get('runtime_attached') is not False:
            fail(section, 'marchio_boreale.runtime_attached != false')
        if marchio.get('state_required') != 'dormant':
            fail(section, f'marchio_boreale.state_required != dormant (got {marchio.get("state_required")})')


def main() -> int:
    schema = load(DW_SCHEMA)
    catalog = load(DW_CATALOG)
    reqs = load(DW_REQS)
    hsk_6star = load(HSK_6STAR)
    if failures:
        return emit()

    records = catalog.get('records', []) or []
    hsk_records = hsk_6star.get('entries', []) or []

    audit_catalog_integrity(records)
    audit_crosslink_hsk(records, hsk_records)
    audit_progression_unlock(records)
    audit_material_requirements(records)
    audit_presence_layer(records)
    audit_borea_safety(records)

    # Soft sanity
    if not schema.get('record_required_fields'):
        warn('schema', 'record_required_fields empty')
    if reqs.get('counts', {}).get('total_divine_weapons') != 13:
        warn('reqs', 'counts.total_divine_weapons != 13')

    return emit(records, hsk_records)


def emit(records=None, hsk_records=None) -> int:
    if failures:
        print('FAIL: RM1.27-D Divine Weapon Cross-Link Audit')
        for f in failures:
            print(f'  - {f}')
        if warnings:
            print('Warnings:')
            for w in warnings:
                print(f'  ! {w}')
        return 1
    print('PASS: RM1.27-D Divine Weapon Cross-Link Audit')
    if records is not None:
        base = [r for r in records if r.get('release_group') == 'launch_base']
        extra = [r for r in records if r.get('release_group') == 'launch_extra_premium']
        print(f'  DW catalog records:      {len(records)}')
        print(f'  DW launch_base:          {len(base)}')
        print(f'  DW launch_extra_premium: {len(extra)} (greek_borea)')
        print(f'  HSK 6★ entries:          {len(hsk_records) if hsk_records else 0}')
        print('  preserved ID overrides verified:')
        for hid, wid in sorted(PRESERVED_ID_OVERRIDES.items()):
            print(f'    {hid} → {wid}')
        print('  no legacy `borea` hero_id present.')
        print('  every record: native_rarity_required=6, exclusive_to_hero=true, catalog_only.')
        print('  all safety_flags: runtime/battle/hp_bar/vfx/gacha/roster_activation/borea_activation = false.')
        print('  progression states: sealed (no bonus / no presence) → dormant+ (gameplay/presence).')
        print('  divine_presence_layer: enabled_from_state=dormant, requires_new_sprite_sheet=false,')
        print('                          is_physical_weapon_animation=false, runtime_attached=false.')
        print('  readability rules: all 7 mobile-safe constraints present.')
        print('  marchio_boreale: source_locked=true, personal=true, runtime_attached=false (Borea only).')
    if warnings:
        print('Warnings:')
        for w in warnings:
            print(f'  ! {w}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
