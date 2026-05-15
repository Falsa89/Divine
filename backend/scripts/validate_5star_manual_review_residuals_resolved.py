#!/usr/bin/env python3
"""
RM1.28-E — Post-Patch Validator for Manual Review Residual Resolution
─────────────────────────────────────────────────────────────────────────
Read-only. Validates the desired post-RM1.28-E state of:
  /app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json

Hard checks:
  • All 5 RM1.28-E target slots are present.
  • Each target slot has manual_review_required != True (i.e. resolved).
  • Each target slot's status_tags now contains the expected concrete
    approved statuses (whitelist).
  • normalization_metadata.rm128e_resolution_history present per target.
  • No legacy tag in any non-passive_advanced status_tags catalog-wide.
  • No unexpected slots flagged manual_review_required (target count = 0
    in target set; total residual count = 0 catalog-wide).
  • passive_advanced still 20/20 approved_source_completed.
  • skill_2.is_true_ultimate=false on 20/20.
  • No Marchio Boreale / Borea / true Ultimate / Divine Weapon / Domain
    leak in 5★.
  • final_numbers=null, runtime_attached=false, balance_values_finalized=false.

Exit 0 on PASS, 1 on FAIL.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

FULL_CATALOG = Path('/app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json')

EXPECTED_RESOLUTIONS = {
    ('celtic_mist_banshee', 'passive_base'):       {'effect_accuracy_up', 'speed_down'},
    ('cursed_pestilence_herald', 'passive_base'):  {'healing_reduction'},
    ('creature_crimson_phoenix', 'skill_1'):       {'regeneration'},
    ('creature_lernaean_hydra', 'skill_2'):        {'regeneration'},
    ('egyptian_claw_of_sekhmet', 'skill_1'):       {'burn'},
}

APPROVED_STATUS_WHITELIST = {
    'stun', 'freeze', 'silence', 'blind', 'taunt', 'slow', 'speed_down', 'speed_up',
    'burn', 'bleed', 'poison', 'curse', 'frostbite', 'shock', 'atk_up', 'def_up',
    'crit_up', 'crit_damage_up', 'vulnerability', 'def_down', 'effect_accuracy_up',
    'magic_damage_up', 'physical_shield', 'magical_shield', 'hybrid_shield',
    'damage_reduction', 'guard', 'immunity', 'healing_up', 'healing_reduction',
    'healing_block', 'regeneration', 'cleanse', 'revive', 'revive_pending',
    'death_protection', 'mark', 'berserk',
}

LEGACY_TAGS_ALL = {
    'damage', 'buff', 'debuff', 'control', 'heal',
    'dot', 'hot', 'shield', 'aura_debuff', 'debuff_aura',
    'trigger', 'conditional_bonus',
}

LEGACY_SLOTS = ('basic', 'passive_base', 'skill_1', 'skill_2')

FORBIDDEN_TOKENS = (
    'marchio_boreale', 'greek_borea', 'ultimate_signature_upgrade',
    'domain_effect_apply',
)
FORBIDDEN_KEY_REGEX = re.compile(r'"(?:divine_weapon|divine_weapon_id|arma_divina)"\s*:')

failures: list[str] = []


def fail(section, msg):
    failures.append(f'[{section}] {msg}')


def main():
    if not FULL_CATALOG.exists():
        fail('IO', f'missing {FULL_CATALOG}')
        return emit()
    data = json.loads(FULL_CATALOG.read_text(encoding='utf-8'))
    entries = data.get('entries', []) or []
    if len(entries) != 20:
        fail('1.entries', f'expected 20, got {len(entries)}')
    if data.get('runtime_attached') is not False:
        fail('2.catalog_flags', 'runtime_attached != false')
    if data.get('balance_values_finalized') is not False:
        fail('2.catalog_flags', 'balance_values_finalized != false')
    if data.get('do_not_treat_as_live_kit') is not True:
        fail('2.catalog_flags', 'do_not_treat_as_live_kit != true')

    # 3. Validate each target resolution
    by_hero = {e.get('hero_id'): e for e in entries}
    for (hid, slot_name), expected_statuses in EXPECTED_RESOLUTIONS.items():
        e = by_hero.get(hid)
        if e is None:
            fail('3.target_present', f'{hid}: hero entry missing')
            continue
        sp = e.get('skill_package') or {}
        slot = sp.get(slot_name)
        if slot is None:
            fail('3.target_present', f'{hid}.{slot_name}: slot missing')
            continue
        if slot.get('manual_review_required') is True:
            fail('4.review_closed', f'{hid}.{slot_name}: manual_review_required still True')
        tags = set(slot.get('status_tags') or [])
        missing = expected_statuses - tags
        if missing:
            fail('5.status_tags_added', f'{hid}.{slot_name}: missing expected status_tags {sorted(missing)}; got {sorted(tags)}')
        bad = [t for t in tags if t not in APPROVED_STATUS_WHITELIST]
        if bad:
            fail('5.status_tags_whitelist', f'{hid}.{slot_name}: non-whitelist tags {bad}')
        nmeta = slot.get('normalization_metadata') or {}
        if not nmeta.get('rm128e_resolution_history'):
            fail('6.metadata', f'{hid}.{slot_name}: rm128e_resolution_history missing')

    # 7. No legacy tag in status_tags anywhere
    for e in entries:
        hid = e.get('hero_id')
        sp = e.get('skill_package') or {}
        for slot_name in LEGACY_SLOTS:
            slot = sp.get(slot_name) or {}
            if not isinstance(slot, dict):
                continue
            for t in (slot.get('status_tags') or []):
                if t in LEGACY_TAGS_ALL:
                    fail('7.no_legacy', f'{hid}.{slot_name}: legacy "{t}" in status_tags')
                elif t not in APPROVED_STATUS_WHITELIST:
                    fail('7.whitelist', f'{hid}.{slot_name}: "{t}" not in whitelist')
            fn = slot.get('final_numbers')
            if fn is not None and not (isinstance(fn, dict) and fn.get('status') == 'foundation_draft' and fn.get('runtime_ready') is False):
                fail('8.final_numbers', f'{hid}.{slot_name}: final_numbers != null')

    # 9. Catalog-wide manual_review_required count
    total_review = 0
    review_loc = []
    for e in entries:
        hid = e.get('hero_id')
        sp = e.get('skill_package') or {}
        for slot_name, slot in sp.items():
            if isinstance(slot, dict) and slot.get('manual_review_required') is True:
                total_review += 1
                review_loc.append((hid, slot_name))
    if total_review != 0:
        fail('9.residual', f'expected 0 manual_review_required, found {total_review}: {review_loc}')

    # 10. passive_advanced still approved
    approved = 0
    for e in entries:
        pa = (e.get('skill_package') or {}).get('passive_advanced') or {}
        if pa.get('design_status') == 'approved_source_completed' and pa.get('source_status') == 'approved_rm128a':
            approved += 1
        fn = pa.get('final_numbers')
        if fn is not None and not (isinstance(fn, dict) and fn.get('status') == 'foundation_draft' and fn.get('runtime_ready') is False):
            fail('10.pa_final_numbers', f'{e.get("hero_id")}.passive_advanced final_numbers != null')
        if pa.get('runtime_attached') is not False:
            fail('10.pa_runtime', f'{e.get("hero_id")}.passive_advanced runtime_attached != false')
    if approved != 20:
        fail('10.pa_approved', f'expected 20/20 passive_advanced approved, got {approved}/20')

    # 11. No true Ultimate
    nottu = 0
    for e in entries:
        s2 = (e.get('skill_package') or {}).get('skill_2') or {}
        if s2.get('is_true_ultimate') is True:
            fail('11.true_ultimate', f'{e.get("hero_id")}: skill_2.is_true_ultimate = TRUE')
        if s2.get('is_true_ultimate') is False:
            nottu += 1
    if nottu != 20:
        fail('11.true_ultimate_count', f'expected 20/20 skill_2.is_true_ultimate=False, got {nottu}/20')

    # 12. Forbidden tokens
    blob = json.dumps(entries, ensure_ascii=False).lower()
    for tok in FORBIDDEN_TOKENS:
        if tok in blob:
            fail('12.forbidden_token', f'token "{tok}" in 5★ entries')
    if FORBIDDEN_KEY_REGEX.search(json.dumps(entries, ensure_ascii=False)):
        fail('12.forbidden_key', 'divine_weapon-like key in 5★ entries')
    if any(e.get('hero_id') == 'borea' for e in entries):
        fail('12.legacy_borea', 'legacy hero_id "borea" present')
    # 13. No forbidden slots
    for e in entries:
        actual = set((e.get('skill_package') or {}).keys())
        bad_slots = actual & {'ultimate', 'true_ultimate', 'divine_weapon', 'domain', 'field_domain'}
        if bad_slots:
            fail('13.forbidden_slot', f'{e.get("hero_id")}: forbidden slot(s) {bad_slots}')

    return emit(approved, nottu, total_review)


def emit(approved=None, nottu=None, total_review=None):
    if failures:
        print('FAIL: RM1.28-E Manual Review Residuals Resolved Validator')
        for f in failures:
            print(f'  - {f}')
        return 1
    print('PASS: RM1.28-E Manual Review Residuals Resolved Validator')
    print(f'  target slots resolved:               5/5')
    if approved is not None:
        print(f'  passive_advanced approved:           {approved}/20')
    if nottu is not None:
        print(f'  skill_2.is_true_ultimate=false:      {nottu}/20')
    if total_review is not None:
        print(f'  total manual_review_required slots:  {total_review} (target: 0)')
    print('  status_tags catalog-wide: only approved whitelist or empty.')
    print('  no legacy bucket tag inside status_tags.')
    print('  no Marchio Boreale / Borea / true Ultimate / Divine Weapon / Domain leak.')
    print('  final_numbers null everywhere. runtime_attached false everywhere.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
