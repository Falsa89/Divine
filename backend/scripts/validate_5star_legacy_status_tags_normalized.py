#!/usr/bin/env python3
"""
RM1.28-D — Post-Patch Validator for 5★ Legacy Status Tags Normalization

Read-only. Validates the desired post-normalization state of:
  /app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json

Hard checks:
  • 20/20 5★ entries.
  • 20/20 canonical IDs, no forbidden non-canonical IDs.
  • status_tags in non-passive_advanced slots: only approved core whitelist
    (or empty). No legacy category tags.
  • design_taxonomy_tags / rule_tags / trigger_tags / normalization_notes
    where applicable.
  • passive_advanced preserved: design_status=approved_source_completed,
    source_status=approved_rm128a, status_tags only whitelist.
  • Catalog-level runtime flags: runtime_attached=false,
    balance_values_finalized=false, do_not_treat_as_live_kit=true.
  • Per-slot final_numbers=null. passive_advanced.runtime_attached=false.
  • skill_2.is_true_ultimate=false on 20/20.
  • No Marchio Boreale / Borea / true Ultimate / Divine Weapon / Domain
    leak in 5★.

Exit 0 on PASS, 1 on FAIL.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

BASE = Path('/app/data/design/hero_skill_kits')
FULL_CATALOG = BASE / 'hero_skill_kits_5star_full_v1.json'

CANONICAL_5STAR = {
    'angelic_bastion_angel', 'celtic_mist_banshee', 'creature_crimson_phoenix',
    'creature_lernaean_hydra', 'cursed_pestilence_herald', 'demonic_gehenna_witch',
    'egyptian_bastet', 'egyptian_claw_of_sekhmet', 'greek_atalanta', 'greek_circe',
    'greek_medusa', 'greek_nemean_lioness', 'greek_nike', 'japanese_miko_of_raijin',
    'norse_dawn_valkyrie', 'norse_eir', 'norse_rime_jotunn', 'norse_volva_of_fate',
    'yokai_oni_kunoichi', 'yokai_yuki_onna',
}

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


def load(path):
    if not path.exists():
        fail('IO', f'missing file {path}')
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        fail('IO', f'invalid JSON {path}: {e}')
        return {}


def main():
    data = load(FULL_CATALOG)
    if failures:
        return emit()

    entries = data.get('entries', []) or []
    if len(entries) != 20:
        fail('1.entries', f'expected 20, got {len(entries)}')

    # Catalog-level flags
    if data.get('runtime_attached') is not False:
        fail('2.catalog_flags', 'runtime_attached != false')
    if data.get('balance_values_finalized') is not False:
        fail('2.catalog_flags', 'balance_values_finalized != false')
    if data.get('do_not_treat_as_live_kit') is not True:
        fail('2.catalog_flags', 'do_not_treat_as_live_kit != true')

    hero_ids = set()
    moved_to_taxonomy = 0
    moved_to_rule = 0
    moved_to_trigger = 0
    manual_review_slots = 0
    bucket_b_mapped_examples: list[str] = []
    for e in entries:
        hid = e.get('hero_id')
        hero_ids.add(hid)
        sp = e.get('skill_package') or {}

        # passive_advanced preservation
        pa = sp.get('passive_advanced') or {}
        if pa.get('design_status') != 'approved_source_completed':
            fail('3.passive_advanced', f'{hid}: design_status != approved_source_completed')
        if pa.get('source_status') != 'approved_rm128a':
            fail('3.passive_advanced', f'{hid}: source_status != approved_rm128a')
        if pa.get('runtime_attached') is not False:
            fail('3.passive_advanced', f'{hid}: runtime_attached != false')
        if pa.get('final_numbers') is not None:
            fail('3.passive_advanced', f'{hid}: final_numbers != null')
        for t in (pa.get('status_tags') or []):
            if t not in APPROVED_STATUS_WHITELIST:
                fail('3.passive_advanced', f'{hid}.passive_advanced: status_tag "{t}" not in whitelist')

        # skill_2.is_true_ultimate must remain False
        s2 = sp.get('skill_2') or {}
        if s2.get('is_true_ultimate') is True:
            fail('4.no_true_ultimate', f'{hid}: skill_2.is_true_ultimate = TRUE')

        # Slot integrity
        actual_slots = set(sp.keys())
        if actual_slots & {'ultimate', 'true_ultimate', 'divine_weapon', 'domain', 'field_domain'}:
            fail('5.forbidden_slots', f'{hid}: forbidden slots present')

        # Per non-passive_advanced slot: status_tags only whitelist, no legacy
        for slot_name in LEGACY_SLOTS:
            slot = sp.get(slot_name)
            if not isinstance(slot, dict):
                continue
            if slot.get('final_numbers') is not None:
                fail('6.final_numbers', f'{hid}.{slot_name}: final_numbers != null')
            tags = slot.get('status_tags') or []
            for t in tags:
                if t in LEGACY_TAGS_ALL:
                    fail('7.legacy_tag_in_status_tags',
                         f'{hid}.{slot_name}.status_tags: legacy "{t}" still present')
                elif t not in APPROVED_STATUS_WHITELIST:
                    fail('8.unknown_status_tag',
                         f'{hid}.{slot_name}.status_tags: "{t}" not in whitelist')

            # Track normalization placement
            for t in (slot.get('design_taxonomy_tags') or []):
                if t in LEGACY_TAGS_ALL or t == 'shield':
                    moved_to_taxonomy += 1
            if isinstance(slot.get('rule_tags'), list) and slot['rule_tags']:
                moved_to_rule += len(slot['rule_tags'])
            if isinstance(slot.get('trigger_tags'), list) and slot['trigger_tags']:
                moved_to_trigger += len(slot['trigger_tags'])
            if slot.get('manual_review_required') is True:
                manual_review_slots += 1
            # Idempotency / new fields validity
            for fld in ('design_taxonomy_tags', 'rule_tags', 'trigger_tags', 'normalization_notes'):
                v = slot.get(fld)
                if v is not None and not isinstance(v, list):
                    fail('9.field_type', f'{hid}.{slot_name}.{fld} not a list')

    # Hero IDs
    if hero_ids != CANONICAL_5STAR:
        miss = CANONICAL_5STAR - hero_ids
        extra = hero_ids - CANONICAL_5STAR
        if miss:
            fail('10.canonical', f'missing canonical IDs: {sorted(miss)}')
        if extra:
            fail('10.canonical', f'non-canonical IDs: {sorted(extra)}')
    if hero_ids & FORBIDDEN_IDS:
        fail('10.canonical', f'forbidden IDs present: {sorted(hero_ids & FORBIDDEN_IDS)}')

    # Borea / Marchio / true Ultimate / DW / Domain leak
    blob = json.dumps(entries, ensure_ascii=False).lower()
    for tok in FORBIDDEN_TOKENS:
        if tok in blob:
            fail('11.borea_dw_leak', f'forbidden token "{tok}" in 5★ entries')
    if FORBIDDEN_KEY_REGEX.search(json.dumps(entries, ensure_ascii=False)):
        fail('11.borea_dw_leak', 'forbidden divine_weapon-like key in 5★ entries')
    # Legacy borea must not appear as standalone hero_id
    if any(e.get('hero_id') == 'borea' for e in entries):
        fail('11.borea_dw_leak', 'legacy hero_id "borea" in 5★ entries')

    return emit(entries, moved_to_taxonomy, moved_to_rule, moved_to_trigger, manual_review_slots)


def emit(entries=None, mt=0, mr=0, mtr=0, mrv=0):
    if failures:
        print('FAIL: RM1.28-D 5★ Legacy Status Tags Normalized Validator')
        for f in failures:
            print(f'  - {f}')
        return 1
    print('PASS: RM1.28-D 5★ Legacy Status Tags Normalized Validator')
    if entries is not None:
        approved_pa = sum(1 for e in entries
                          if (e.get('skill_package') or {}).get('passive_advanced', {}).get('design_status') == 'approved_source_completed')
        nottu = sum(1 for e in entries
                    if (e.get('skill_package') or {}).get('skill_2', {}).get('is_true_ultimate') is False)
        print(f'  5★ entries:                          {len(entries)}')
        print(f'  passive_advanced approved:           {approved_pa}/20')
        print(f'  skill_2.is_true_ultimate=false:      {nottu}/20')
        print(f'  Bucket A/B-review/B-mapped moves to design_taxonomy_tags: {mt}')
        print(f'  Bucket C moved to rule_tags entries:                      {mr}')
        print(f'  Bucket C moved to trigger_tags entries:                   {mtr}')
        print(f'  Slots flagged manual_review_required:                     {mrv}')
        print('  status_tags in non-passive_advanced slots: only approved whitelist or empty.')
        print('  no legacy category/bucket tag left inside status_tags.')
        print('  no Marchio Boreale / Borea / true Ultimate / Divine Weapon / Domain leak.')
        print('  final_numbers null everywhere. runtime_attached false everywhere.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
