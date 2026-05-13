#!/usr/bin/env python3
"""
RM1.28-A — 5★ Passive Advanced Source Validator
─────────────────────────────────────────────────────────────────────────
Read-only audit of the approved 5★ passive_advanced design source and
the inert 5★ Hero Skill Kit full catalog after patching.

Validates 30+ rules. Exit 0 on PASS, 1 on FAIL.

Hard rules (per RM1.28-A prompt):
  - Source file exists with 20 entries.
  - Hero IDs match exactly the 20 canonical 5★ launch_base IDs.
  - No legacy/incorrect IDs present.
  - Every entry has slot=passive_advanced.
  - No true Ultimate / Divine Weapon hook / Domain field present.
  - All final_numbers = null.
  - runtime_attached=false, battle_runtime_attached=false everywhere.
  - do_not_treat_as_live_kit=true everywhere.
  - source_status != TODO_SOURCE_REQUIRED on every entry.
  - design_status = approved_source_completed on every entry.
  - status_tags only from approved status core whitelist.
  - In the inert full catalog, all 20 5★ heroes' passive_advanced slot is
    no longer 'missing_from_approved_source'.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

BASE = Path('/app/data/design/hero_skill_kits')
SOURCE = BASE / 'hero_skill_kits_5star_passive_advanced_source_v1.json'
FULL_CATALOG = BASE / 'hero_skill_kits_5star_full_v1.json'

CANONICAL_5STAR = {
    'angelic_bastion_angel', 'celtic_mist_banshee', 'creature_crimson_phoenix',
    'creature_lernaean_hydra', 'cursed_pestilence_herald', 'demonic_gehenna_witch',
    'egyptian_bastet', 'egyptian_claw_of_sekhmet', 'greek_atalanta', 'greek_circe',
    'greek_medusa', 'greek_nemean_lioness', 'greek_nike', 'japanese_miko_of_raijin',
    'norse_dawn_valkyrie', 'norse_eir', 'norse_rime_jotunn', 'norse_volva_of_fate',
    'yokai_oni_kunoichi', 'yokai_yuki_onna',
}

# IDs explicitly forbidden by the RM1.28-A prompt
FORBIDDEN_IDS = {
    'norse_frost_jotunn', 'japanese_raijin_miko', 'infernal_gehenna_witch',
    'japanese_oni_kunoichi', 'norse_fate_volva', 'japanese_yuki_onna',
    'crimson_phoenix', 'greek_lernaean_hydra',
}

APPROVED_STATUS_WHITELIST = {
    'stun', 'freeze', 'silence', 'blind', 'taunt', 'slow', 'speed_down', 'speed_up',
    'burn', 'bleed', 'poison', 'curse', 'frostbite', 'shock', 'atk_up', 'def_up',
    'crit_up', 'crit_damage_up', 'vulnerability', 'def_down', 'effect_accuracy_up',
    'magic_damage_up', 'physical_shield', 'magical_shield', 'hybrid_shield',
    'damage_reduction', 'guard', 'immunity', 'healing_up', 'healing_reduction',
    'healing_block', 'regeneration', 'cleanse', 'revive', 'revive_pending',
    'death_protection', 'mark', 'berserk', 'domain_effect',
}

# Forbidden tokens in design fields (true Ultimate / Domain / Divine Weapon)
FORBIDDEN_TOKENS_IN_RECORD = (
    'true_ultimate', 'ultimate_signature', 'divine_weapon', 'domain_effect_apply',
    'arma_divina', 'marchio_boreale',  # personal status reserved for Borea only
)

failures: list[str] = []
warnings: list[str] = []


def fail(section, msg):
    failures.append(f'[{section}] {msg}')


def load(path):
    if not path.exists():
        fail('IO', f'missing file {path}')
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        fail('IO', f'invalid JSON {path}: {e}')
        return {}


def deep_contains_forbidden_token(obj, hid):
    s = json.dumps(obj, ensure_ascii=False).lower()
    for tok in FORBIDDEN_TOKENS_IN_RECORD:
        if tok in s:
            fail('forbidden_tokens', f'{hid}: contains forbidden token "{tok}"')


def audit_source(src):
    section = '1.source_file'
    entries = src.get('entries', [])
    if len(entries) != 20:
        fail(section, f'expected 20 entries, got {len(entries)}')
    hids = [e.get('skill_id') for e in entries]  # skill_id like hero_id_passive_advanced
    hero_ids = set()
    for e in entries:
        sid = e.get('skill_id') or ''
        if not sid.endswith('_passive_advanced'):
            fail(section, f'skill_id "{sid}" does not end with _passive_advanced')
        hid_guess = sid[:-len('_passive_advanced')]
        hero_ids.add(hid_guess)
        if e.get('slot') != 'passive_advanced':
            fail(section, f'{hid_guess}: slot != passive_advanced')
        if e.get('design_status') != 'approved_source_completed':
            fail(section, f'{hid_guess}: design_status != approved_source_completed')
        if e.get('source_status') != 'approved_rm128a':
            fail(section, f'{hid_guess}: source_status != approved_rm128a')
        if e.get('final_numbers') is not None:
            fail(section, f'{hid_guess}: final_numbers != null')
        if e.get('runtime_attached') is not False:
            fail(section, f'{hid_guess}: runtime_attached != false')
        if e.get('battle_runtime_attached') is not False:
            fail(section, f'{hid_guess}: battle_runtime_attached != false')
        if e.get('do_not_treat_as_live_kit') is not True:
            fail(section, f'{hid_guess}: do_not_treat_as_live_kit != true')
        # status_tags whitelist
        tags = e.get('status_tags') or []
        bad = [t for t in tags if t not in APPROVED_STATUS_WHITELIST]
        if bad:
            fail(section, f'{hid_guess}: status_tags not in whitelist: {bad}')
        # status_interactions whitelist
        ints = e.get('status_interactions') or []
        bad2 = [t for t in ints if t not in APPROVED_STATUS_WHITELIST]
        if bad2:
            fail(section, f'{hid_guess}: status_interactions not in whitelist: {bad2}')
        # skill_interactions must be subset of skill_1/skill_2
        si = set(e.get('skill_interactions') or [])
        if not si.issubset({'skill_1', 'skill_2'}):
            fail(section, f'{hid_guess}: skill_interactions outside skill_1/skill_2: {si}')
        # Forbidden tokens / domain effect / divine weapon hook
        deep_contains_forbidden_token(e, hid_guess)

    if hero_ids != CANONICAL_5STAR:
        missing = CANONICAL_5STAR - hero_ids
        extra = hero_ids - CANONICAL_5STAR
        if missing:
            fail(section, f'missing canonical hero IDs: {sorted(missing)}')
        if extra:
            fail(section, f'unexpected hero IDs: {sorted(extra)}')
    forbidden_seen = hero_ids & FORBIDDEN_IDS
    if forbidden_seen:
        fail(section, f'forbidden non-canonical IDs used: {sorted(forbidden_seen)}')

    # source file safety flags
    for k in ['runtime_attached', 'battle_runtime_attached', 'ui_runtime_attached',
              'hp_bar_runtime_attached', 'vfx_runtime_attached',
              'balance_values_finalized', 'gacha_attached',
              'roster_activation_attached', 'borea_activation_allowed']:
        if src.get(k) is not False:
            fail(section, f'source file flag {k} != false')
    if src.get('do_not_treat_as_live_kit') is not True:
        fail(section, 'source file do_not_treat_as_live_kit != true')


def audit_full_catalog(full):
    section = '2.full_catalog_patched'
    entries = full.get('entries', [])
    if len(entries) != 20:
        fail(section, f'expected 20 entries in full catalog, got {len(entries)}')
    if full.get('runtime_attached') is not False:
        fail(section, 'full catalog runtime_attached != false')
    if full.get('balance_values_finalized') is not False:
        fail(section, 'full catalog balance_values_finalized != false')
    if full.get('do_not_treat_as_live_kit') is not True:
        fail(section, 'full catalog do_not_treat_as_live_kit != true')
    hero_ids_seen = set()
    for e in entries:
        hid = e.get('hero_id')
        hero_ids_seen.add(hid)
        sp = e.get('skill_package') or {}
        pa = sp.get('passive_advanced') or {}
        if pa.get('design_status') == 'missing_from_approved_source':
            fail(section, f'{hid}: passive_advanced still missing_from_approved_source')
        if pa.get('source_status') == 'TODO_SOURCE_REQUIRED':
            fail(section, f'{hid}: passive_advanced still TODO_SOURCE_REQUIRED')
        if pa.get('design_status') != 'approved_source_completed':
            fail(section, f'{hid}: passive_advanced design_status != approved_source_completed (got {pa.get("design_status")})')
        if pa.get('source_status') != 'approved_rm128a':
            fail(section, f'{hid}: passive_advanced source_status != approved_rm128a (got {pa.get("source_status")})')
        if pa.get('slot') != 'passive_advanced':
            fail(section, f'{hid}: slot != passive_advanced')
        if pa.get('final_numbers') is not None:
            fail(section, f'{hid}: passive_advanced final_numbers != null')
        if pa.get('runtime_attached') is not False:
            fail(section, f'{hid}: passive_advanced runtime_attached != false')
        if pa.get('battle_runtime_attached') is not False:
            fail(section, f'{hid}: passive_advanced battle_runtime_attached != false')
        if pa.get('do_not_treat_as_live_kit') is not True:
            fail(section, f'{hid}: passive_advanced do_not_treat_as_live_kit != true')
        # Slot integrity: no new ultimate slot introduced
        for forbidden_slot in ['ultimate', 'true_ultimate', 'divine_weapon', 'domain']:
            if forbidden_slot in sp:
                fail(section, f'{hid}: forbidden slot "{forbidden_slot}" introduced in skill_package')
        # The expected 5 slots remain
        expected_slots = {'basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2'}
        actual_slots = set(sp.keys())
        if not expected_slots.issubset(actual_slots):
            fail(section, f'{hid}: missing expected slots {expected_slots - actual_slots}')
        if actual_slots - expected_slots:
            warnings.append(f'[{section}] {hid}: extra slots beyond expected 5: {actual_slots - expected_slots}')
    if hero_ids_seen != CANONICAL_5STAR:
        missing = CANONICAL_5STAR - hero_ids_seen
        extra = hero_ids_seen - CANONICAL_5STAR
        if missing:
            fail(section, f'full catalog missing canonical hero IDs: {sorted(missing)}')
        if extra:
            fail(section, f'full catalog has unexpected hero IDs: {sorted(extra)}')


def main():
    src = load(SOURCE)
    full = load(FULL_CATALOG)
    if failures:
        return emit()
    audit_source(src)
    audit_full_catalog(full)
    return emit(src, full)


def emit(src=None, full=None):
    if failures:
        print('FAIL: RM1.28-A 5★ Passive Advanced Source')
        for f in failures:
            print(f'  - {f}')
        if warnings:
            print('Warnings:')
            for w in warnings:
                print(f'  ! {w}')
        return 1
    print('PASS: RM1.28-A 5★ Passive Advanced Source')
    if src is not None:
        print(f'  source file entries:           {len(src.get("entries", []))}')
        print(f'  source design_status_per_entry: {src.get("design_status_per_entry")}')
        print(f'  source source_status_per_entry: {src.get("source_status_per_entry")}')
    if full is not None:
        print(f'  full catalog entries patched:  {sum(1 for e in full.get("entries", []) if (e.get("skill_package") or {}).get("passive_advanced", {}).get("design_status") == "approved_source_completed")}/20')
        print(f'  full catalog runtime_attached:       {full.get("runtime_attached")}')
        print(f'  full catalog balance_values_finalized: {full.get("balance_values_finalized")}')
        print(f'  full catalog do_not_treat_as_live_kit: {full.get("do_not_treat_as_live_kit")}')
    print('  all 20 canonical 5★ hero IDs verified.')
    print('  no forbidden non-canonical IDs used.')
    print('  no true Ultimate / Divine Weapon / Domain slots introduced.')
    print('  status_tags + status_interactions: all from approved status core whitelist.')
    print('  final_numbers null everywhere. runtime_attached false everywhere.')
    if warnings:
        print('Warnings:')
        for w in warnings:
            print(f'  ! {w}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
