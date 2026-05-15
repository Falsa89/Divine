#!/usr/bin/env python3
"""
RM1.32-A — 5★ Balance Foundation Validator
─────────────────────────────────────────────────────────────────────────
Read-only validator. Verifies the post-RM1.32-A 5★ catalog state:
foundation_draft final_numbers everywhere, runtime stays disabled,
no 5★ ultimate/DW/Domain/Borea leak, status references still resolve.

NO mutation. NO DB. NO runtime.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

HSK_5STAR = Path('/app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json')
HSK_6STAR = Path('/app/data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json')
STATUS_CAT = Path('/app/data/design/skill_status_vfx_catalogs/status_effect_catalog_v1.json')
CONTRACT = Path('/app/data/design/hero_skill_kits/hero_skill_kits_5star_balance_contract_v1.json')

EXPECTED_HEROES = {
    'angelic_bastion_angel','celtic_mist_banshee','creature_crimson_phoenix',
    'creature_lernaean_hydra','cursed_pestilence_herald','demonic_gehenna_witch',
    'egyptian_bastet','egyptian_claw_of_sekhmet','greek_atalanta','greek_circe',
    'greek_medusa','greek_nemean_lioness','greek_nike','japanese_miko_of_raijin',
    'norse_dawn_valkyrie','norse_eir','norse_rime_jotunn','norse_volva_of_fate',
    'yokai_oni_kunoichi','yokai_yuki_onna',
}
SLOTS_5 = {'basic','passive_base','skill_1','passive_advanced','skill_2'}
FORBIDDEN_HERO_IDS = {'borea','primordial_gaia','greek_boreas','olympian_borea'}

# Ranges per contract
RANGES = {
    ('basic','damage_multiplier_pct'): (70,130),
    ('basic','status_chance_pct'): (0,50),
    ('basic','status_duration_turns'): (0,3),
    ('basic','cooldown_turns'): (0,0),
    ('basic','target_count'): (1,1),
    ('skill_1','damage_multiplier_pct'): (80,260),
    ('skill_1','healing_multiplier_pct'): (80,220),
    ('skill_1','shield_multiplier_pct'): (80,220),
    ('skill_1','status_chance_pct'): (30,90),
    ('skill_1','status_duration_turns'): (0,3),
    ('skill_1','cooldown_turns'): (2,3),
    ('skill_1','target_count'): (1,5),
    ('skill_2','damage_multiplier_pct'): (120,400),
    ('skill_2','healing_multiplier_pct'): (120,280),
    ('skill_2','shield_multiplier_pct'): (120,280),
    ('skill_2','status_chance_pct'): (40,95),
    ('skill_2','status_duration_turns'): (0,3),
    ('skill_2','cooldown_turns'): (4,5),
    ('skill_2','target_count'): (1,5),
    ('passive','stat_modifier_pct'): (5,25),
    ('passive','internal_cooldown_turns'): (0,6),
}
FORBIDDEN_FIELDS = {'final_runtime_attached','battle_runtime_id','live_hooks','db_resolver','runtime_target','vfx_runtime'}

failures: list[str] = []

def fail(sec, msg): failures.append(f'[{sec}] {msg}')

def check_range(slot_name, field, val, section, hid):
    if val is None:
        return
    key = (slot_name, field)
    if key not in RANGES:
        # passive variants
        if slot_name.startswith('passive') and field in ('stat_modifier_pct','internal_cooldown_turns'):
            key = ('passive', field)
        else:
            return
    lo, hi = RANGES[key]
    if not (isinstance(val,(int,float)) and lo <= val <= hi):
        fail(section, f'{hid}.{slot_name}.{field}={val} out of range [{lo},{hi}]')

def main() -> int:
    if not HSK_5STAR.exists():
        fail('IO', f'missing {HSK_5STAR}'); return emit()
    c5 = json.loads(HSK_5STAR.read_text(encoding='utf-8'))

    # Top-level
    if c5.get('balance_pass_id') != 'RM1.32-A':
        fail('top','balance_pass_id != RM1.32-A')
    if c5.get('balance_values_finalized') is not False: fail('top','balance_values_finalized != false')
    if c5.get('runtime_attached') is not False: fail('top','runtime_attached != false')
    if c5.get('battle_runtime_attached') is not False: fail('top','battle_runtime_attached != false')
    if c5.get('do_not_treat_as_live_kit') is not True: fail('top','do_not_treat_as_live_kit != true')
    if not isinstance(c5.get('last_balance_foundation_write'), dict):
        fail('top','last_balance_foundation_write block missing')

    entries = c5.get('entries') or []
    if len(entries) != 20: fail('entries', f'expected 20, got {len(entries)}')
    ids = {e.get('hero_id') for e in entries}
    if ids != EXPECTED_HEROES:
        fail('entries', f'hero_id set mismatch: missing={sorted(EXPECTED_HEROES-ids)}, extra={sorted(ids-EXPECTED_HEROES)}')
    forb = ids & FORBIDDEN_HERO_IDS
    if forb: fail('entries', f'forbidden hero_ids: {sorted(forb)}')

    total_slots = 0
    for e in entries:
        hid = e.get('hero_id')
        sp = e.get('skill_package') or {}
        if set(sp.keys()) != SLOTS_5:
            fail('slot_set', f'{hid}: {sorted(set(sp.keys()))}')
        if 'ultimate' in sp:
            fail('slot_set', f'{hid}: ultimate slot present (forbidden in 5★)')
        if 'divine_weapon_id' in e:
            fail('5star_boundaries', f'{hid}: divine_weapon_id present (forbidden in 5★)')
        rec = json.dumps(e, ensure_ascii=False).lower()
        for tok in ('marchio_boreale','greek_borea','domain_effect_apply','ultimate_signature_upgrade'):
            if tok in rec:
                fail('5star_boundaries', f'{hid}: forbidden token "{tok}"')
        for slot_name, slot in sp.items():
            if not isinstance(slot, dict): continue
            total_slots += 1
            fn = slot.get('final_numbers')
            if not isinstance(fn, dict):
                fail('final_numbers', f'{hid}.{slot_name}: final_numbers is not an object')
                continue
            if fn.get('status') != 'foundation_draft':
                fail('final_numbers', f'{hid}.{slot_name}.status != foundation_draft')
            if fn.get('runtime_ready') is not False:
                fail('final_numbers', f'{hid}.{slot_name}.runtime_ready != false')
            # Forbidden fields
            extra_forb = set(fn.keys()) & FORBIDDEN_FIELDS
            if extra_forb:
                fail('final_numbers', f'{hid}.{slot_name} has forbidden fields: {sorted(extra_forb)}')
            # is_true_ultimate for skill_2
            if slot_name == 'skill_2':
                if fn.get('is_true_ultimate') is not False:
                    fail('skill_2', f'{hid}.skill_2.is_true_ultimate != false')
            # Ranges
            for field in ('damage_multiplier_pct','healing_multiplier_pct','shield_multiplier_pct',
                          'status_chance_pct','status_duration_turns','cooldown_turns','target_count'):
                if field in fn:
                    check_range(slot_name, field, fn[field], 'ranges', hid)
            if slot_name.startswith('passive'):
                for field in ('stat_modifier_pct','internal_cooldown_turns'):
                    if field in fn:
                        check_range(slot_name, field, fn[field], 'ranges', hid)
            # target_count semantics: only set on non-passive
            if slot_name.startswith('passive') and 'target_count' in fn:
                fail('ranges', f'{hid}.{slot_name}: target_count must not be set on passive')

    if total_slots != 100:
        fail('count', f'expected 100 final_numbers objects, got {total_slots}')

    # 6★ must remain final_numbers=null
    if HSK_6STAR.exists():
        c6 = json.loads(HSK_6STAR.read_text(encoding='utf-8'))
        for e in c6.get('entries') or []:
            for sn, slot in (e.get('skill_package') or {}).items():
                if isinstance(slot, dict) and slot.get('final_numbers') is not None:
                    fail('6star_invariant', f'{e.get("hero_id")}.{sn}: 6★ final_numbers no longer null')

    # Status resolver: all status references in 5★ resolve
    if STATUS_CAT.exists():
        statuses = json.loads(STATUS_CAT.read_text(encoding='utf-8')).get('statuses') or []
        ids_set = {s.get('status_id') for s in statuses}
        for e in entries:
            hid = e['hero_id']
            for sn, slot in (e.get('skill_package') or {}).items():
                if not isinstance(slot, dict): continue
                for f in ('status_tags','status_interactions'):
                    for tag in slot.get(f) or []:
                        if tag not in ids_set:
                            fail('status_resolver', f'5★ {hid}.{sn}.{f}: "{tag}" not in status catalog')

    return emit(total_slots, len(entries))


def emit(total_slots: int = 0, n_entries: int = 0) -> int:
    if failures:
        print('FAIL: RM1.32-A — 5★ Balance Foundation Validator')
        for f in failures: print(f'  - {f}')
        return 1
    print('PASS: RM1.32-A — 5★ Balance Foundation Validator')
    print(f'  5★ entries:              {n_entries}/20')
    print(f'  final_numbers objects:   {total_slots}/100')
    print(f'  status = foundation_draft on all slots')
    print(f'  runtime_ready=false on all slots')
    print(f'  top-level safety flags: runtime/battle_runtime/balance_finalized=false; do_not_treat_as_live_kit=true')
    print(f'  skill_2.is_true_ultimate=false on all 20')
    print(f'  6★ final_numbers remain null')
    print(f'  no 5★ ultimate / no DW / no Domain / no Borea leak')
    print(f'  numeric values within conservative ranges')
    print(f'  status references all resolve in RM1.25-B catalog')
    return 0


if __name__ == '__main__':
    sys.exit(main())
