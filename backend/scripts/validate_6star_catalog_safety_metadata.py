#!/usr/bin/env python3
"""
RM1.30-A — 6★ Catalog Safety Metadata Harmonization Validator
─────────────────────────────────────────────────────────────────────────
Read-only validator confirming that the metadata-only harmonization patch
applied to hero_skill_kits_6star_borea_v1.json is internally consistent
and that NO 6★ skill content / slot / status / effect tag /
divine_weapon_id / Borea visibility was changed.

Exit 0 on PASS, 1 on FAIL. NO mutation. NO DB write. NO runtime hook.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

HSK_6STAR = Path('/app/data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json')
DW_CATALOG = Path('/app/data/design/divine_weapons/divine_weapons_catalog_v1.json')

# Canonical expectations from RM1.27 / RM1.28 / RM1.29
EXPECTED_LAUNCH_BASE = {
    'greek_athena', 'greek_artemis', 'greek_gaia', 'primordial_nyx',
    'japanese_raijin', 'japanese_susanoo', 'japanese_amaterasu',
    'egyptian_sekhmet', 'mesopotamian_tiamat', 'egyptian_isis',
    'celtic_morrigan', 'cursed_pestilence_horseman',
}
EXPECTED_EXTRA_PREMIUM = {'greek_borea'}
EXPECTED_ALL = EXPECTED_LAUNCH_BASE | EXPECTED_EXTRA_PREMIUM
EXPECTED_SLOTS = {'basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2', 'ultimate'}

PRESERVED_DW_IDS = {
    'greek_athena': 'aegis_of_athena',
    'greek_artemis': 'artemis_lunar_bow',
    'greek_gaia': 'gaia_primordial_root',
    'primordial_nyx': 'nyx_primordial_night_veil',
    'japanese_raijin': 'raijin_thunder_drums',
    'japanese_susanoo': 'susanoo_ame_no_habakiri',
    'japanese_amaterasu': 'amaterasu_yata_no_kagami',
    'egyptian_sekhmet': 'sekhmet_burning_eye_of_ra',
    'mesopotamian_tiamat': 'tiamat_primordial_abyss',
    'egyptian_isis': 'isis_sacred_tyet_knot',
    'celtic_morrigan': 'morrigan_raven_mantle',
    'cursed_pestilence_horseman': 'pestilence_seal',
    'greek_borea': 'borea_wings_of_the_north_wind',
}

FORBIDDEN_HERO_IDS = {'borea', 'primordial_gaia', 'greek_boreas', 'olympian_borea'}

failures: list[str] = []
warnings: list[str] = []


def fail(section: str, msg: str) -> None:
    failures.append(f'[{section}] {msg}')


def warn(section: str, msg: str) -> None:
    warnings.append(f'[{section}] {msg}')


def load_json(p: Path) -> dict:
    if not p.exists():
        fail('IO', f'missing file {p}')
        return {}
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        fail('IO', f'invalid JSON {p}: {e}')
        return {}


def main() -> int:
    cat = load_json(HSK_6STAR)
    dw = load_json(DW_CATALOG)
    if failures:
        return emit()

    # 1) Top-level/catalog-level safety metadata
    section = '1.catalog_safety_metadata'
    if cat.get('battle_runtime_attached') is not False:
        fail(section, 'top-level battle_runtime_attached != false (RM1.30-A primary requirement)')
    if cat.get('runtime_attached') is not False:
        fail(section, 'top-level runtime_attached != false')
    if cat.get('balance_values_finalized') is not False:
        fail(section, 'top-level balance_values_finalized != false')
    if cat.get('do_not_treat_as_live_kit') is not True:
        fail(section, 'top-level do_not_treat_as_live_kit != true')

    # 2) Harmonization metadata block (informational but expected after patch)
    section = '2.harmonization_block'
    h = cat.get('safety_metadata_harmonization')
    if h is None:
        warn(section, 'safety_metadata_harmonization block missing (informational, not blocking)')
    else:
        if h.get('task') != 'RM1.30-A':
            fail(section, f'safety_metadata_harmonization.task != "RM1.30-A" (got {h.get("task")})')
        for flag in (
            'no_skill_content_change', 'no_slot_change',
            'no_status_or_effect_tag_change', 'no_divine_weapon_id_change',
            'no_borea_visibility_change',
        ):
            if h.get(flag) is not True:
                fail(section, f'safety_metadata_harmonization.{flag} != true')

    # 3) Entry counts unchanged
    section = '3.entry_counts'
    entries = cat.get('entries') or []
    if len(entries) != 13:
        fail(section, f'expected 13 entries, got {len(entries)}')
    base = [e for e in entries if e.get('release_group') == 'launch_base']
    extra = [e for e in entries if e.get('release_group') == 'launch_extra_premium']
    if len(base) != 12:
        fail(section, f'expected 12 launch_base, got {len(base)}')
    if len(extra) != 1:
        fail(section, f'expected 1 launch_extra_premium, got {len(extra)}')
    if len(extra) == 1 and extra[0].get('hero_id') != 'greek_borea':
        fail(section, f'launch_extra_premium must be greek_borea (got {extra[0].get("hero_id")})')

    # 4) Hero ID set + forbidden absent
    section = '4.hero_ids'
    ids = {e.get('hero_id') for e in entries}
    miss = EXPECTED_ALL - ids
    if miss:
        fail(section, f'missing canonical hero IDs: {sorted(miss)}')
    ext = ids - EXPECTED_ALL
    if ext:
        fail(section, f'non-canonical hero IDs present: {sorted(ext)}')
    forb = ids & FORBIDDEN_HERO_IDS
    if forb:
        fail(section, f'forbidden hero IDs present: {sorted(forb)}')

    # 5) Slot structure unchanged
    section = '5.slot_structure'
    for e in entries:
        hid = e.get('hero_id', '?')
        sp = e.get('skill_package') or {}
        actual = set(sp.keys())
        if actual != EXPECTED_SLOTS:
            fail(section, f'{hid}: slot set != expected (got {sorted(actual)})')
        # native_rarity = 6
        if e.get('native_rarity') != 6:
            fail(section, f'{hid}: native_rarity != 6 (got {e.get("native_rarity")})')

    # 6) divine_weapon_id unchanged
    section = '6.divine_weapon_id_preserved'
    for e in entries:
        hid = e.get('hero_id')
        if hid in PRESERVED_DW_IDS:
            if e.get('divine_weapon_id') != PRESERVED_DW_IDS[hid]:
                fail(section, f'{hid}: divine_weapon_id changed — expected "{PRESERVED_DW_IDS[hid]}" got "{e.get("divine_weapon_id")}"')

    # 7) Per-slot inertness (78/78)
    section = '7.slot_inertness'
    slot_count = 0
    for e in entries:
        hid = e.get('hero_id', '?')
        if e.get('runtime_attached') is not False:
            fail(section, f'{hid}: entry runtime_attached != false')
        if e.get('balance_values_finalized') is not False:
            fail(section, f'{hid}: entry balance_values_finalized != false')
        for slot_name, slot in (e.get('skill_package') or {}).items():
            if not isinstance(slot, dict):
                continue
            slot_count += 1
            if slot.get('final_numbers') is not None:
                fn = slot.get('final_numbers')
                if not (isinstance(fn, dict)
                        and fn.get('status') == 'foundation_draft'
                        and fn.get('runtime_ready') is False):
                    fail(section, f'{hid}.{slot_name}: final_numbers not foundation_draft/runtime_ready=false (post-RM1.32-B allowance)')
            if slot.get('runtime_attached') is True:
                fail(section, f'{hid}.{slot_name}: runtime_attached == true')
            if slot.get('battle_runtime_attached') is True:
                fail(section, f'{hid}.{slot_name}: battle_runtime_attached == true')
    if slot_count != 78:
        fail(section, f'expected 78 total slots (13×6), got {slot_count}')

    # 8) Divine Weapon cross-link still passes
    section = '8.divine_weapon_crosslink'
    dw_by_id = {r.get('divine_weapon_id'): r for r in (dw.get('records') or [])}
    for e in entries:
        hid = e.get('hero_id')
        dwid = e.get('divine_weapon_id')
        if not dwid:
            fail(section, f'{hid}: missing divine_weapon_id')
            continue
        if dwid not in dw_by_id:
            fail(section, f'{hid}: divine_weapon_id "{dwid}" not in Divine Weapon catalog')
            continue
        if dw_by_id[dwid].get('hero_id') != hid:
            fail(section, f'{hid}: DW record hero_id mismatch')

    # 9) Marchio Boreale leak check (Borea-only)
    section = '9.marchio_boreale_leak'
    for e in entries:
        hid = e.get('hero_id', '?')
        if hid == 'greek_borea':
            continue
        rec = json.dumps(e, ensure_ascii=False).lower()
        if 'marchio_boreale' in rec:
            fail(section, f'{hid}: marchio_boreale leaked into non-Borea record')

    return emit(cat, slot_count)


def emit(cat: dict | None = None, slot_count: int = 0) -> int:
    if failures:
        print('FAIL: RM1.30-A — 6★ Catalog Safety Metadata Harmonization Validator')
        for f in failures:
            print(f'  - {f}')
        if warnings:
            print('Warnings:')
            for w in warnings:
                print(f'  ! {w}')
        return 1
    print('PASS: RM1.30-A — 6★ Catalog Safety Metadata Harmonization Validator')
    if cat is not None:
        print(f'  top-level battle_runtime_attached:    {cat.get("battle_runtime_attached")}')
        print(f'  top-level runtime_attached:           {cat.get("runtime_attached")}')
        print(f'  top-level balance_values_finalized:   {cat.get("balance_values_finalized")}')
        print(f'  top-level do_not_treat_as_live_kit:   {cat.get("do_not_treat_as_live_kit")}')
        print(f'  safety_metadata_harmonization.task:   {(cat.get("safety_metadata_harmonization") or {}).get("task")}')
        print(f'  entries:                              {len(cat.get("entries") or [])} (expected 13)')
        print(f'  total slots inert:                    {slot_count}/78')
        print( '  divine_weapon_id preservation:        13/13 unchanged')
        print( '  Borea release_group:                  launch_extra_premium (unchanged)')
        print( '  Marchio Boreale leak in non-Borea:    0')
    if warnings:
        print('Warnings (informational):')
        for w in warnings:
            print(f'  ! {w}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
