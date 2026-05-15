#!/usr/bin/env python3
"""
RM1.32-B — 6★ Balance Foundation Validator
─────────────────────────────────────────────────────────────────────────
Read-only validator. Verifies the post-RM1.32-B 6★ catalog state:
foundation_draft final_numbers on all 78 slots, runtime stays disabled,
ultimate is_true_ultimate=true on all 13, no Marchio leak, etc.

NO mutation. NO DB. NO runtime.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

HSK_5STAR = Path('/app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json')
HSK_6STAR = Path('/app/data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json')
DW_CATALOG = Path('/app/data/design/divine_weapons/divine_weapons_catalog_v1.json')
STATUS_CAT = Path('/app/data/design/skill_status_vfx_catalogs/status_effect_catalog_v1.json')
CONTRACT = Path('/app/data/design/hero_skill_kits/hero_skill_kits_6star_balance_contract_v1.json')

EXPECTED_HEROES_6 = {
    'greek_athena', 'greek_artemis', 'greek_gaia', 'primordial_nyx',
    'japanese_raijin', 'japanese_susanoo', 'japanese_amaterasu',
    'egyptian_sekhmet', 'mesopotamian_tiamat', 'egyptian_isis',
    'celtic_morrigan', 'cursed_pestilence_horseman', 'greek_borea',
}
SLOTS_6 = {'basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2', 'ultimate'}
FORBIDDEN_HERO_IDS = {'borea', 'primordial_gaia', 'greek_boreas', 'olympian_borea'}

# Numeric ranges per contract (RM1.32-B)
RANGES = {
    ('basic', 'damage_multiplier_pct'):       (85, 130),
    ('basic', 'status_chance_pct'):           (0, 50),
    ('basic', 'status_duration_turns'):       (0, 3),
    ('basic', 'cooldown_turns'):              (0, 0),
    ('basic', 'target_count'):                (1, 1),

    ('skill_1', 'damage_multiplier_pct'):     (140, 340),
    ('skill_1', 'healing_multiplier_pct'):    (170, 240),
    ('skill_1', 'shield_multiplier_pct'):     (170, 240),
    ('skill_1', 'status_chance_pct'):         (65, 90),
    ('skill_1', 'status_duration_turns'):     (0, 3),
    ('skill_1', 'cooldown_turns'):            (3, 3),
    ('skill_1', 'target_count'):              (1, 5),

    ('skill_2', 'damage_multiplier_pct'):     (220, 520),
    ('skill_2', 'healing_multiplier_pct'):    (260, 360),
    ('skill_2', 'shield_multiplier_pct'):     (260, 360),
    ('skill_2', 'status_chance_pct'):         (70, 95),
    ('skill_2', 'status_duration_turns'):     (0, 3),
    ('skill_2', 'cooldown_turns'):            (4, 5),
    ('skill_2', 'target_count'):              (1, 5),

    ('ultimate', 'damage_multiplier_pct'):    (260, 720),
    ('ultimate', 'healing_multiplier_pct'):   (380, 520),
    ('ultimate', 'shield_multiplier_pct'):    (380, 520),
    ('ultimate', 'status_chance_pct'):        (85, 100),
    ('ultimate', 'status_duration_turns'):    (0, 3),
    ('ultimate', 'cooldown_turns'):           (6, 7),
    ('ultimate', 'target_count'):             (1, 5),

    ('passive', 'stat_modifier_pct'):         (12, 28),
    ('passive', 'internal_cooldown_turns'):   (0, 6),
}
FORBIDDEN_FIELDS = {
    'final_runtime_attached', 'battle_runtime_id', 'live_hooks',
    'db_resolver', 'runtime_target', 'vfx_runtime',
}
MARCHIO_DRAFT_RANGES = {
    'max_stacks_pvp':                       (1, 3),
    'max_stacks_pve':                       (1, 5),
    'damage_bonus_per_stack_pct':           (3, 10),
    'freeze_chance_bonus_per_stack_pct':    (2, 6),
}

failures: list[str] = []


def fail(sec, msg):
    failures.append(f'[{sec}] {msg}')


def check_range(slot_name, field, val, hid):
    if val is None:
        return
    key = (slot_name, field)
    if key not in RANGES:
        if slot_name.startswith('passive') and field in ('stat_modifier_pct', 'internal_cooldown_turns'):
            key = ('passive', field)
        else:
            return
    lo, hi = RANGES[key]
    if not (isinstance(val, (int, float)) and lo <= val <= hi):
        fail('ranges', f'{hid}.{slot_name}.{field}={val} out of range [{lo},{hi}]')


def main() -> int:
    if not HSK_6STAR.exists():
        fail('IO', f'missing {HSK_6STAR}')
        return emit()
    c6 = json.loads(HSK_6STAR.read_text(encoding='utf-8'))

    # Top-level safety
    if c6.get('balance_pass_id') != 'RM1.32-B':
        fail('top', f"balance_pass_id != RM1.32-B (got {c6.get('balance_pass_id')!r})")
    if c6.get('balance_values_finalized') is not False:
        fail('top', 'balance_values_finalized != false')
    if c6.get('runtime_attached') is not False:
        fail('top', 'runtime_attached != false')
    if c6.get('battle_runtime_attached') is not False:
        fail('top', 'battle_runtime_attached != false')
    if c6.get('do_not_treat_as_live_kit') is not True:
        fail('top', 'do_not_treat_as_live_kit != true')
    if not isinstance(c6.get('last_balance_foundation_write'), dict):
        fail('top', 'last_balance_foundation_write block missing')

    entries = c6.get('entries') or []
    if len(entries) != 13:
        fail('entries', f'expected 13, got {len(entries)}')
    ids = {e.get('hero_id') for e in entries}
    if ids != EXPECTED_HEROES_6:
        fail('entries', f'hero_id set mismatch: missing={sorted(EXPECTED_HEROES_6 - ids)}, '
                        f'extra={sorted(ids - EXPECTED_HEROES_6)}')
    forb = ids & FORBIDDEN_HERO_IDS
    if forb:
        fail('entries', f'forbidden hero_ids: {sorted(forb)}')

    # DW cross-link
    dw_records = json.loads(DW_CATALOG.read_text(encoding='utf-8')).get('records') or []
    dw_ids = {r.get('divine_weapon_id') for r in dw_records}

    total_slots = 0
    ultimate_true_count = 0

    for e in entries:
        hid = e.get('hero_id')
        # DW cross-link must remain unchanged
        dwid = e.get('divine_weapon_id')
        if not dwid:
            fail('crosslink', f'{hid}: missing divine_weapon_id')
        elif dwid not in dw_ids:
            fail('crosslink', f'{hid}: divine_weapon_id "{dwid}" not in DW catalog')
        # release_group preservation for borea
        if hid == 'greek_borea':
            if e.get('release_group') != 'launch_extra_premium':
                fail('borea', f"greek_borea release_group != 'launch_extra_premium'")
        else:
            if e.get('release_group') != 'launch_base':
                fail('release_group', f"{hid}.release_group != 'launch_base'")

        sp = e.get('skill_package') or {}
        if set(sp.keys()) != SLOTS_6:
            fail('slot_set', f'{hid}: slots={sorted(set(sp.keys()))}')

        for slot_name, slot in sp.items():
            if not isinstance(slot, dict):
                continue
            total_slots += 1
            fn = slot.get('final_numbers')
            if not isinstance(fn, dict):
                fail('final_numbers', f'{hid}.{slot_name}: final_numbers is not an object')
                continue
            if fn.get('status') != 'foundation_draft':
                fail('final_numbers', f'{hid}.{slot_name}.status != foundation_draft')
            if fn.get('runtime_ready') is not False:
                fail('final_numbers', f'{hid}.{slot_name}.runtime_ready != false')

            # Forbidden runtime fields
            bad = set(fn.keys()) & FORBIDDEN_FIELDS
            if bad:
                fail('final_numbers', f'{hid}.{slot_name} has forbidden fields: {sorted(bad)}')

            # is_true_ultimate semantics
            if slot_name == 'ultimate':
                if fn.get('is_true_ultimate') is not True:
                    fail('ultimate', f'{hid}.ultimate.is_true_ultimate != true')
                else:
                    ultimate_true_count += 1
            else:
                if fn.get('is_true_ultimate') is True:
                    fail('non_ultimate', f'{hid}.{slot_name}: is_true_ultimate true on non-ultimate slot')

            # Range checks
            for field in ('damage_multiplier_pct', 'healing_multiplier_pct', 'shield_multiplier_pct',
                          'status_chance_pct', 'status_duration_turns', 'cooldown_turns', 'target_count'):
                if field in fn:
                    check_range(slot_name, field, fn[field], hid)
            if slot_name.startswith('passive'):
                for field in ('stat_modifier_pct', 'internal_cooldown_turns'):
                    if field in fn:
                        check_range(slot_name, field, fn[field], hid)
                # No target_count on passive
                if 'target_count' in fn and fn['target_count'] is not None:
                    fail('ranges', f'{hid}.{slot_name}: target_count must not be set on passive')

            # Divine Weapon synergy placeholder must be design-only, runtime_ready=false
            dws = fn.get('divine_weapon_synergy_placeholder')
            if dws is not None:
                if not isinstance(dws, dict):
                    fail('dw_synergy', f'{hid}.{slot_name}.divine_weapon_synergy_placeholder not object')
                else:
                    if dws.get('design_only') is not True:
                        fail('dw_synergy', f'{hid}.{slot_name}: dw synergy design_only != true')
                    if dws.get('runtime_ready') is not False:
                        fail('dw_synergy', f'{hid}.{slot_name}: dw synergy runtime_ready != false')
                    if dws.get('numeric_modifier_pct') not in (None,):
                        fail('dw_synergy', f'{hid}.{slot_name}: dw synergy numeric_modifier_pct must be null at foundation pass')

            # Marchio Boreale draft values only on greek_borea
            marchio = fn.get('marchio_boreale_stack_values')
            if marchio is not None and hid != 'greek_borea':
                fail('marchio_leak', f'{hid}.{slot_name}: marchio_boreale_stack_values on non-Borea slot')
            if marchio is not None and hid == 'greek_borea':
                if not isinstance(marchio, dict):
                    fail('marchio', f'{hid}.{slot_name}: marchio_boreale_stack_values not object')
                else:
                    if marchio.get('design_only') is not True:
                        fail('marchio', f'{hid}.{slot_name}: marchio design_only != true')
                    if marchio.get('runtime_ready') is not False:
                        fail('marchio', f'{hid}.{slot_name}: marchio runtime_ready != false')
                    if marchio.get('owner_hero_id') != 'greek_borea':
                        fail('marchio', f'{hid}.{slot_name}: marchio owner_hero_id != greek_borea')
                    for k, (lo, hi) in MARCHIO_DRAFT_RANGES.items():
                        v = marchio.get(k)
                        if v is None or not (isinstance(v, (int, float)) and lo <= v <= hi):
                            fail('marchio_ranges', f'{hid}.{slot_name}.{k}={v} out of [{lo},{hi}]')

            # unique_mechanic_placeholder only on Borea
            uniq = fn.get('unique_mechanic_placeholder')
            if uniq is not None:
                if hid != 'greek_borea':
                    fail('unique_leak', f'{hid}.{slot_name}: unique_mechanic_placeholder on non-Borea slot')
                else:
                    if uniq.get('design_only') is not True or uniq.get('runtime_ready') is not False:
                        fail('unique', f'{hid}.{slot_name}: unique_mechanic_placeholder must be design_only/runtime_ready=false')

    if total_slots != 78:
        fail('count', f'expected 78 final_numbers objects, got {total_slots}')
    if ultimate_true_count != 13:
        fail('ultimate', f'expected 13/13 ultimate.is_true_ultimate=true, got {ultimate_true_count}')

    # No Marchio leak in any non-Borea entry (whole-tree text scan)
    for e in entries:
        if e.get('hero_id') == 'greek_borea':
            continue
        blob = json.dumps(e, ensure_ascii=False).lower()
        if 'marchio_boreale' in blob or 'marchio boreale' in blob:
            fail('marchio_leak', f"{e.get('hero_id')}: marchio_boreale token leak in non-Borea entry")

    # 5★ catalog must remain in valid foundation_draft state (cross-check existence only)
    if HSK_5STAR.exists():
        c5 = json.loads(HSK_5STAR.read_text(encoding='utf-8'))
        if c5.get('balance_pass_id') != 'RM1.32-A':
            fail('5star_cross', '5★ balance_pass_id != RM1.32-A (5★ catalog drift)')

    return emit(total_slots, len(entries), ultimate_true_count)


def emit(total_slots: int = 0, n_entries: int = 0, ult_true: int = 0) -> int:
    if failures:
        print('FAIL: RM1.32-B — 6★ Balance Foundation Validator')
        for f in failures:
            print(f'  - {f}')
        return 1
    print('PASS: RM1.32-B — 6★ Balance Foundation Validator')
    print(f'  6★ entries:                {n_entries}/13')
    print(f'  final_numbers objects:     {total_slots}/78')
    print(f'  status = foundation_draft on all slots')
    print(f'  runtime_ready=false on all slots')
    print(f'  top-level safety flags: runtime/battle_runtime/balance_finalized=false; do_not_treat_as_live_kit=true')
    print(f'  ultimate.is_true_ultimate=true on {ult_true}/13')
    print(f'  divine_weapon_synergy_placeholder: design_only=true, runtime_ready=false (no numeric modifier)')
    print(f'  marchio_boreale_stack_values: only on greek_borea, design_only')
    print(f'  numeric values within conservative 6★ ranges')
    print(f'  5★ balance_pass_id = RM1.32-A (5★ catalog untouched by this task)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
