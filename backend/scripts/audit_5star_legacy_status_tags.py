#!/usr/bin/env python3
"""
RM1.28-C — 5★ Legacy Status Tags Audit & Normalization Plan Generator
─────────────────────────────────────────────────────────────────────────
READ-ONLY on existing 5★ catalog.
WRITES one design-only artifact (the normalization plan JSON).

Scope:
  Inspect every 5★ entry's non-passive_advanced slots
  (basic, passive_base, skill_1, skill_2) and collect every
  `status_tag` that is NOT in the approved status core whitelist.

Output:
  • stdout: human-readable PASS/INFO report (always exit 0 unless an
    actual structural error is found).
  • file:   /app/data/design/hero_skill_kits/
            hero_skill_kits_5star_legacy_status_tags_normalization_plan_v1.json

NEVER:
  • mutates the 5★ catalog
  • mutates the 6★ catalog
  • touches battle_engine / combat / HP bar / gacha / roster / Character
    Bible / Divine Weapon catalog / Borea activation
  • writes to MongoDB
"""
from __future__ import annotations
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/app/data/design/hero_skill_kits')
FULL_CATALOG = BASE / 'hero_skill_kits_5star_full_v1.json'
PA_SOURCE = BASE / 'hero_skill_kits_5star_passive_advanced_source_v1.json'
PLAN_OUT = BASE / 'hero_skill_kits_5star_legacy_status_tags_normalization_plan_v1.json'

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

LEGACY_SLOTS = ('basic', 'passive_base', 'skill_1', 'skill_2')

# Classification rules — explicit, conservative. safe_auto_fix=false unless trivial.
TAG_RULES = {
    'damage':            ('A.category_tag_keep_as_design_metadata',
                          'demote_to_design_taxonomy_field',     False, []),
    'buff':              ('A.category_tag_keep_as_design_metadata',
                          'demote_to_design_taxonomy_field',     False, []),
    'debuff':            ('A.category_tag_keep_as_design_metadata',
                          'demote_to_design_taxonomy_field',     False, []),
    'control':           ('A.category_tag_keep_as_design_metadata',
                          'demote_to_design_taxonomy_field',     False, []),
    'heal':              ('A.category_tag_keep_as_design_metadata',
                          'manual_context_mapping',               False,
                          ['healing_up', 'regeneration', 'effect_kind:direct_heal']),
    'shield':            ('B.likely_status_mapping_needed',
                          'manual_context_mapping',               False,
                          ['physical_shield', 'magical_shield', 'hybrid_shield']),
    'dot':               ('B.likely_status_mapping_needed',
                          'manual_context_mapping',               False,
                          ['burn', 'bleed', 'poison', 'curse', 'frostbite', 'shock']),
    'hot':               ('B.likely_status_mapping_needed',
                          'manual_context_mapping',               False,
                          ['regeneration', 'healing_up']),
    'trigger':           ('C.trigger_or_rule_tag_not_status',
                          'move_to_trigger_or_rule_field',        False, []),
    'conditional_bonus': ('C.trigger_or_rule_tag_not_status',
                          'move_to_trigger_or_rule_field',        False, []),
    'aura_debuff':       ('D.ambiguous_needs_manual_review',
                          'manual_review_required',               False,
                          ['vulnerability', 'def_down', 'speed_down', 'effect_accuracy_up']),
    'debuff_aura':       ('D.ambiguous_needs_manual_review',
                          'manual_review_required',               False,
                          ['vulnerability', 'def_down', 'speed_down', 'effect_accuracy_up']),
}

# Anything that would be forbidden_or_invalid (E bucket)
FORBIDDEN_TOKEN_TAGS = {
    'marchio_boreale', 'true_ultimate', 'ultimate_signature_upgrade',
    'divine_weapon', 'arma_divina', 'domain_effect_apply',
}

structural_failures: list[str] = []


def fail(msg):
    structural_failures.append(msg)


def load(path):
    if not path.exists():
        fail(f'missing file {path}')
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        fail(f'invalid JSON in {path}: {e}')
        return {}


def main():
    full = load(FULL_CATALOG)
    src = load(PA_SOURCE)
    if structural_failures:
        for f in structural_failures:
            print('STRUCTURAL FAIL:', f)
        return 1

    full_entries = full.get('entries', []) or []
    src_entries = src.get('entries', []) or []

    # 1. Sanity (read-only)
    full_ids = [e.get('hero_id') for e in full_entries]
    full_id_set = set(full_ids)
    if len(full_entries) != 20:
        fail(f'expected 20 5★ entries, got {len(full_entries)}')
    if full_id_set != CANONICAL_5STAR:
        fail(f'5★ catalog hero_id mismatch: missing={sorted(CANONICAL_5STAR-full_id_set)} extra={sorted(full_id_set-CANONICAL_5STAR)}')
    forbidden_in_catalog = full_id_set & FORBIDDEN_IDS
    if forbidden_in_catalog:
        fail(f'forbidden non-canonical IDs in 5★ catalog: {sorted(forbidden_in_catalog)}')
    # Borea/marchio leak check
    rec_blob = json.dumps(full_entries, ensure_ascii=False).lower()
    for tok in ('marchio_boreale', 'greek_borea', '"borea"'):
        if tok in rec_blob:
            fail(f'5★ catalog contains forbidden token: {tok}')
    if len(src_entries) != 20:
        fail(f'expected 20 PA source entries, got {len(src_entries)}')

    if structural_failures:
        for f in structural_failures:
            print('STRUCTURAL FAIL:', f)
        return 1

    # 2. Scan legacy tags
    freq = defaultdict(int)
    affected = defaultdict(lambda: {'heroes': set(), 'hero_slot_pairs': []})
    inspected_slots = 0
    total_tags_scanned = 0
    whitelist_tag_count = 0
    legacy_tag_count = 0
    forbidden_tag_hits = []
    pa_clean = 0
    for e in full_entries:
        hid = e.get('hero_id')
        sp = e.get('skill_package') or {}
        # passive_advanced cleanliness check
        pa = sp.get('passive_advanced') or {}
        pa_tags = (pa.get('status_tags') or []) + (pa.get('status_interactions') or [])
        if all(t in APPROVED_STATUS_WHITELIST for t in pa_tags) and pa.get('design_status') == 'approved_source_completed':
            pa_clean += 1
        for slot in LEGACY_SLOTS:
            s = sp.get(slot) or {}
            if not isinstance(s, dict):
                continue
            inspected_slots += 1
            for t in (s.get('status_tags') or []):
                total_tags_scanned += 1
                if t in APPROVED_STATUS_WHITELIST:
                    whitelist_tag_count += 1
                else:
                    legacy_tag_count += 1
                    freq[t] += 1
                    affected[t]['heroes'].add(hid)
                    affected[t]['hero_slot_pairs'].append({'hero_id': hid, 'slot': slot})
                if t in FORBIDDEN_TOKEN_TAGS:
                    forbidden_tag_hits.append({'hero_id': hid, 'slot': slot, 'tag': t})

    if forbidden_tag_hits:
        for h in forbidden_tag_hits:
            fail(f'forbidden tag "{h["tag"]}" found in {h["hero_id"]}.{h["slot"]}')
        for f in structural_failures:
            print('STRUCTURAL FAIL:', f)
        return 1

    # 3. Classify
    classification_counts = defaultdict(int)
    per_tag_plan = []
    sorted_tags = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    for tag, n in sorted_tags:
        rule = TAG_RULES.get(tag, ('D.ambiguous_needs_manual_review',
                                   'manual_review_required', False, []))
        classification, recommended_action, safe_auto_fix, candidate_mappings = rule
        classification_counts[classification] += 1
        per_tag_plan.append({
            'legacy_tag': tag,
            'frequency': n,
            'affected_heroes': sorted(affected[tag]['heroes']),
            'affected_slots': sorted({p['slot'] for p in affected[tag]['hero_slot_pairs']}),
            'affected_hero_slot_pairs': affected[tag]['hero_slot_pairs'],
            'classification': classification,
            'recommended_action': recommended_action,
            'safe_auto_fix': safe_auto_fix,
            'candidate_mappings': candidate_mappings,
            'notes': (
                'Inspect hero kit identity and existing skill description before mapping. '
                'Do NOT auto-fix unless mapping is trivial and absolutely safe. '
                'Numbers/chance/duration unaffected. final_numbers stays null.'
            ),
        })

    # 4. Per-hero summary
    per_hero_summary = []
    for e in full_entries:
        hid = e.get('hero_id')
        sp = e.get('skill_package') or {}
        hero_findings = {}
        for slot in LEGACY_SLOTS:
            s = sp.get(slot) or {}
            tags = s.get('status_tags') or []
            legacy = [t for t in tags if t not in APPROVED_STATUS_WHITELIST]
            if legacy:
                hero_findings[slot] = legacy
        per_hero_summary.append({
            'hero_id': hid,
            'element': e.get('element'),
            'role': e.get('role'),
            'legacy_tags_by_slot': hero_findings,
            'total_legacy_tags': sum(len(v) for v in hero_findings.values()),
        })
    per_hero_summary.sort(key=lambda x: -x['total_legacy_tags'])

    # 5. Print human-readable report
    print('PASS: RM1.28-C 5★ Legacy Status Tags Audit (read-only)')
    print(f'  total 5★ entries scanned:        {len(full_entries)}')
    print(f'  inspected slots (basic/passive_base/skill_1/skill_2): {inspected_slots}')
    print(f'  total status_tags scanned:       {total_tags_scanned}')
    print(f'  in approved whitelist:           {whitelist_tag_count}')
    print(f'  legacy / non-whitelist:          {legacy_tag_count}')
    print(f'  distinct legacy tags:            {len(freq)}')
    print(f'  passive_advanced clean (RM1.28-A): {pa_clean}/20')
    print(f'  Borea/marchio_boreale leak:      none')
    print(f'  forbidden non-canonical IDs:     none')
    print()
    print(f'  Legacy tag frequency:')
    for tag, n in sorted_tags:
        rule = TAG_RULES.get(tag, ('D.ambiguous_needs_manual_review',
                                   'manual_review_required', False, []))
        print(f'    {tag:<22} {n:>3}x   [{rule[0]}]   action={rule[1]}   auto_fix={rule[2]}')
    print()
    print(f'  Classification distribution:')
    for c, n in sorted(classification_counts.items()):
        print(f'    {c:<48} {n} distinct legacy tags')

    # 6. Build & write design-only plan JSON
    plan = {
        'plan_id': 'hero_skill_kits_5star_legacy_status_tags_normalization_plan_v1',
        'task_origin': 'RM1.28-C',
        'version': 'v1',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'scope': '5star_launch_base',
        'inspected_slots': list(LEGACY_SLOTS),
        'excluded_slots': ['passive_advanced'],
        'approved_status_core_whitelist': sorted(APPROVED_STATUS_WHITELIST),
        'canonical_5star_hero_ids': sorted(CANONICAL_5STAR),
        'forbidden_non_canonical_ids': sorted(FORBIDDEN_IDS),
        'forbidden_token_tags': sorted(FORBIDDEN_TOKEN_TAGS),
        'audit_stats': {
            'total_5star_entries': len(full_entries),
            'inspected_slots_count': inspected_slots,
            'total_status_tags_scanned': total_tags_scanned,
            'whitelist_tag_count': whitelist_tag_count,
            'legacy_tag_count': legacy_tag_count,
            'distinct_legacy_tags': len(freq),
            'passive_advanced_clean_count': pa_clean,
            'borea_leak_detected': False,
            'marchio_boreale_in_5star_detected': False,
            'forbidden_id_present': False,
        },
        'classification_buckets': {
            'A.category_tag_keep_as_design_metadata': 'Generic taxonomy tags (damage/buff/debuff/control/heal). Demote to a non-status design taxonomy field. They are not status effects.',
            'B.likely_status_mapping_needed': 'Concrete but ambiguous tags (dot/hot/shield) that imply a real status effect but need hero/skill context.',
            'C.trigger_or_rule_tag_not_status': 'Tags that are triggers/rules (trigger/conditional_bonus) and should not be inside status_tags.',
            'D.ambiguous_needs_manual_review': 'Tags whose runtime meaning is unclear and must be reviewed per hero.',
            'E.forbidden_or_invalid': 'Tags implying 6★/Borea/Divine Weapon/Domain/true Ultimate or non-approved special status. Hard fail.',
        },
        'per_tag_plan': per_tag_plan,
        'per_hero_summary': per_hero_summary,
        'classification_counts': dict(classification_counts),
        'recommended_next_task': {
            'id': 'RM1.28-D',
            'title': '5★ Legacy Status Tags Controlled Normalization Patch',
            'requires': [
                'explicit approval after reviewing this RM1.28-C plan',
                'manual hero/skill context mapping (no broad auto-fix)',
                'preserve passive_advanced approved_source_completed entries unchanged',
                'preserve final_numbers=null and runtime_attached=false everywhere',
                'do not introduce true Ultimate / Divine Weapon / Domain into 5★',
                'do not introduce marchio_boreale into 5★',
            ],
            'preferred_strategy': (
                'Per-hero, per-slot manual mapping using the candidate_mappings '
                'in this plan, with PR-style diff and validator regression. '
                'For bucket A (category taxonomy), move legacy tag from '
                'status_tags into a new design-only field (e.g. design_taxonomy_tags) '
                'rather than rewriting it as a status.'
            ),
            'approval_required_before_executing': True,
        },
        'safety_flags': {
            'catalog_only': True,
            'design_audit_only': True,
            'runtime_attached': False,
            'battle_runtime_attached': False,
            'db_write_allowed': False,
            'auto_fix_applied': False,
            'borea_activation_allowed': False,
            'do_not_treat_as_live_kit': True,
        },
        'notes': (
            'This is a read-only normalization plan generated by RM1.28-C. '
            'It does NOT modify hero_skill_kits_5star_full_v1.json. '
            'It does NOT modify API or UI. It does NOT activate runtime. '
            'It must be explicitly approved before any normalization patch '
            'is executed (RM1.28-D).'
        ),
    }
    PLAN_OUT.parent.mkdir(parents=True, exist_ok=True)
    PLAN_OUT.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
    print()
    print(f'  WROTE plan file: {PLAN_OUT}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
