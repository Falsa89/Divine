#!/usr/bin/env python3
"""
RM1.30-B — 6★ Effect Tags Taxonomy One-Shot Audit Script
─────────────────────────────────────────────────────────────────────────
Read-only audit + classification of every tag found in the 6★ Hero Skill
Kit catalog across all tag-list-bearing fields:

  status_tags, status_interactions, effect_tags, core_effect_tags,
  theme_tags, vfx_tags, design_taxonomy_tags, rule_tags, trigger_tags,
  core_status_ids

Classifies each tag into 7 buckets:
  A. approved_status_core
  B. unique_personal_status (marchio_boreale on greek_borea only)
  C. design_taxonomy_tag
  D. rule_or_trigger_tag
  E. vfx_or_presentation_tag
  F. forbidden_or_invalid
  G. unknown_needs_manual_review

The decision gate determines whether a controlled taxonomy-only patch
to hero_skill_kits_6star_borea_v1.json is needed (Case B) or NOT
(Case A — already taxonomy-separated).

NO mutation. NO DB write. NO runtime hook. Read-only.

Exit 0 on PASS (audit completes cleanly), 1 on FAIL (forbidden findings
or non-Borea Marchio Boreale leak).
"""
from __future__ import annotations
import json
import sys
from collections import Counter
from pathlib import Path

HSK_6STAR = Path('/app/data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json')
DW_CATALOG = Path('/app/data/design/divine_weapons/divine_weapons_catalog_v1.json')

# ── Canonical scope (RM1.27 / RM1.28 / RM1.29 / RM1.30-A) ─────────────
EXPECTED_LAUNCH_BASE = {
    'greek_athena', 'greek_artemis', 'greek_gaia', 'primordial_nyx',
    'japanese_raijin', 'japanese_susanoo', 'japanese_amaterasu',
    'egyptian_sekhmet', 'mesopotamian_tiamat', 'egyptian_isis',
    'celtic_morrigan', 'cursed_pestilence_horseman',
}
EXPECTED_EXTRA_PREMIUM = {'greek_borea'}
EXPECTED_ALL = EXPECTED_LAUNCH_BASE | EXPECTED_EXTRA_PREMIUM
FORBIDDEN_HERO_IDS = {'borea', 'primordial_gaia', 'greek_boreas', 'olympian_borea'}

# ── Tag taxonomy ──────────────────────────────────────────────────────
APPROVED_CORE_STATUS = {
    'stun', 'freeze', 'silence', 'blind', 'taunt',
    'slow', 'speed_down', 'speed_up',
    'burn', 'bleed', 'poison', 'curse', 'frostbite', 'shock',
    'atk_up', 'def_up', 'crit_up', 'crit_damage_up',
    'vulnerability', 'def_down', 'effect_accuracy_up', 'magic_damage_up',
    'physical_shield', 'magical_shield', 'hybrid_shield',
    'damage_reduction', 'guard', 'immunity',
    'healing_up', 'healing_reduction', 'healing_block',
    'regeneration', 'cleanse', 'revive', 'revive_pending', 'death_protection',
    'mark', 'berserk', 'domain_effect',
}
UNIQUE_PERSONAL = {'marchio_boreale': 'greek_borea'}

TAGGED_FIELDS = (
    # Possible status fields
    'status_tags', 'status_interactions', 'core_status_ids',
    # Possible taxonomy fields
    'effect_tags', 'core_effect_tags', 'theme_tags', 'vfx_tags',
    'design_taxonomy_tags', 'rule_tags', 'trigger_tags',
)
STATUS_FIELDS = {'status_tags', 'status_interactions', 'core_status_ids'}
TAXONOMY_FIELDS = {'effect_tags', 'core_effect_tags', 'theme_tags', 'vfx_tags',
                   'design_taxonomy_tags', 'rule_tags', 'trigger_tags'}

# Heuristic lexicons for refining taxonomy classification
TRIGGER_HINTS = (
    'on_kill', 'on_low_hp', 'on_death', 'if_', 'trigger',
    'conditional', 'cooldown', 'stack_rule', 'reactive_',
)
VFX_HINTS = (
    'omen_charges', 'flare', '_arrow', 'storm_drum', 'frost_wind',
    'aegis_light', 'solar', 'abyss', 'raven', 'screen_',
    'summon_visual', 'secondary_wave',
)


def classify(tag: str, field: str, hero_id: str) -> str:
    if not isinstance(tag, str):
        return 'G_unknown_needs_manual_review'
    if tag in APPROVED_CORE_STATUS:
        return 'A_approved_status_core'
    if tag in UNIQUE_PERSONAL:
        if hero_id != UNIQUE_PERSONAL[tag]:
            return 'F_forbidden_or_invalid'
        return 'B_unique_personal_status'
    # Hard-forbidden tokens
    low = tag.lower()
    if low == 'borea' or low.startswith('legacy_borea') or low.startswith('primordial_gaia'):
        return 'F_forbidden_or_invalid'
    # Field-aware classification: taxonomy fields → C/D/E
    if field in TAXONOMY_FIELDS:
        if any(h in low for h in TRIGGER_HINTS):
            return 'D_rule_or_trigger_tag'
        if any(h in low for h in VFX_HINTS):
            return 'E_vfx_or_presentation_tag'
        return 'C_design_taxonomy_tag'
    # In a status field but not approved/unique → unknown manual review
    return 'G_unknown_needs_manual_review'


def main() -> int:
    if not HSK_6STAR.exists():
        print(f'FAIL: missing source file {HSK_6STAR}')
        return 1
    cat = json.loads(HSK_6STAR.read_text(encoding='utf-8'))
    dw = {}
    if DW_CATALOG.exists():
        dw = json.loads(DW_CATALOG.read_text(encoding='utf-8'))

    entries = cat.get('entries') or []
    failures: list[str] = []

    # ── Sanity: scope ────────────────────────────────────────────────
    if len(entries) != 13:
        failures.append(f'expected 13 entries, got {len(entries)}')
    hero_ids = {e.get('hero_id') for e in entries}
    if hero_ids != EXPECTED_ALL:
        miss = EXPECTED_ALL - hero_ids
        ext = hero_ids - EXPECTED_ALL
        if miss:
            failures.append(f'missing canonical hero IDs: {sorted(miss)}')
        if ext:
            failures.append(f'non-canonical hero IDs: {sorted(ext)}')
    forb = hero_ids & FORBIDDEN_HERO_IDS
    if forb:
        failures.append(f'forbidden hero IDs present: {sorted(forb)}')

    # ── Tag traversal ────────────────────────────────────────────────
    per_field_freq: dict[str, Counter] = {f: Counter() for f in TAGGED_FIELDS}
    per_bucket: dict[str, Counter] = {
        b: Counter() for b in (
            'A_approved_status_core', 'B_unique_personal_status',
            'C_design_taxonomy_tag', 'D_rule_or_trigger_tag',
            'E_vfx_or_presentation_tag', 'F_forbidden_or_invalid',
            'G_unknown_needs_manual_review',
        )
    }
    per_hero: dict[str, dict] = {}
    per_slot: Counter = Counter()
    forbidden_findings: list[str] = []
    unknown_findings: list[str] = []
    non_borea_marchio: list[str] = []
    total_slots = 0
    total_tags = 0
    status_field_total = 0
    taxonomy_field_total = 0

    for e in entries:
        hid = e.get('hero_id', '?')
        per_hero[hid] = {
            'slots': 0,
            'tags_total': 0,
            'per_bucket': Counter(),
            'per_field': Counter(),
        }
        sp = e.get('skill_package') or {}
        for slot_name, slot in sp.items():
            if not isinstance(slot, dict):
                continue
            total_slots += 1
            per_hero[hid]['slots'] += 1
            per_slot[slot_name] += 1
            for field in TAGGED_FIELDS:
                values = slot.get(field)
                if not isinstance(values, list):
                    continue
                for tag in values:
                    per_field_freq[field][tag] += 1
                    total_tags += 1
                    per_hero[hid]['tags_total'] += 1
                    per_hero[hid]['per_field'][field] += 1
                    if field in STATUS_FIELDS:
                        status_field_total += 1
                    if field in TAXONOMY_FIELDS:
                        taxonomy_field_total += 1
                    bucket = classify(tag, field, hid)
                    per_bucket[bucket][tag] += 1
                    per_hero[hid]['per_bucket'][bucket] += 1
                    if bucket == 'F_forbidden_or_invalid':
                        forbidden_findings.append(f'{hid}.{slot_name}.{field}: {tag}')
                    elif bucket == 'G_unknown_needs_manual_review':
                        unknown_findings.append(f'{hid}.{slot_name}.{field}: {tag}')
                    if tag == 'marchio_boreale' and hid != 'greek_borea':
                        non_borea_marchio.append(f'{hid}.{slot_name}.{field}')

    if forbidden_findings:
        failures.append(f'{len(forbidden_findings)} forbidden tag finding(s)')
    if non_borea_marchio:
        failures.append(f'marchio_boreale leaked into non-Borea: {non_borea_marchio}')

    # ── Decision gate ────────────────────────────────────────────────
    # CASE A (no patch needed): status_tags + status_interactions empty
    # AND every tag in status fields is approved or unique-on-owner.
    status_tags_count = per_field_freq.get('status_tags', Counter())
    status_interactions_count = per_field_freq.get('status_interactions', Counter())
    has_unknown_in_status = any(
        u.endswith('.status_tags' + ': ' + t) or '.status_tags:' in u or '.status_interactions:' in u
        for u in unknown_findings for t in [u.split(': ')[-1]]
    )
    decision = {
        'patch_needed': False,
        'decision_type': 'no_patch_needed',
        'reason': '',
        'allowed_patch_scope': 'none',
    }
    reasons: list[str] = []
    if len(status_tags_count) > 0:
        reasons.append(f'status_tags populated ({sum(status_tags_count.values())} entries) — needs inspection.')
    if len(status_interactions_count) > 0:
        reasons.append(f'status_interactions populated ({sum(status_interactions_count.values())} entries) — needs inspection.')
    if unknown_findings:
        reasons.append(f'{len(unknown_findings)} unknown tag(s) in status fields.')
    if forbidden_findings:
        reasons.append(f'{len(forbidden_findings)} forbidden tag(s) found.')

    if not reasons:
        decision['patch_needed'] = False
        decision['decision_type'] = 'no_patch_needed'
        decision['reason'] = (
            'status_tags and status_interactions are absent from every 6★ slot. '
            'All tags live in core_effect_tags (taxonomy) or core_status_ids (approved status / '
            'unique marchio_boreale on greek_borea only). 0 forbidden, 0 unknown, 0 Marchio leak.'
        )
        decision['allowed_patch_scope'] = 'none'
    else:
        decision['patch_needed'] = True
        decision['decision_type'] = 'controlled_patch_recommended'
        decision['reason'] = ' / '.join(reasons)
        decision['allowed_patch_scope'] = 'taxonomy_fields_only'

    # ── Emit ─────────────────────────────────────────────────────────
    print('RM1.30-B — 6★ Effect Tags Taxonomy Audit')
    print('=' * 60)
    print(f'Entries:                  {len(entries)} (expected 13)')
    print(f'Total slots:              {total_slots} (expected 78)')
    print(f'Total tags counted:       {total_tags}')
    print(f'Tag-list fields scanned:  {", ".join(TAGGED_FIELDS)}')
    print()
    print('Per-field totals:')
    for f in TAGGED_FIELDS:
        c = per_field_freq[f]
        print(f'  {f:25s} unique={len(c):3d}  total={sum(c.values()):4d}')
    print(f'  {"STATUS_FIELDS subtotal":25s} total={status_field_total}')
    print(f'  {"TAXONOMY_FIELDS subtotal":25s} total={taxonomy_field_total}')
    print()
    print('Per-bucket summary:')
    for b, c in per_bucket.items():
        print(f'  {b:35s} unique={len(c):3d}  total={sum(c.values()):4d}')
    print()
    print('Top 20 design taxonomy tags (Bucket C):')
    for t, n in per_bucket['C_design_taxonomy_tag'].most_common(20):
        print(f'  {n:3d}  {t}')
    print()
    print('Top rule/trigger tags (Bucket D):')
    for t, n in per_bucket['D_rule_or_trigger_tag'].most_common(20):
        print(f'  {n:3d}  {t}')
    print()
    print('Top VFX/presentation tags (Bucket E):')
    for t, n in per_bucket['E_vfx_or_presentation_tag'].most_common(20):
        print(f'  {n:3d}  {t}')
    print()
    print(f'Forbidden findings (F): {len(forbidden_findings)}')
    for f in forbidden_findings:
        print(f'  - {f}')
    print(f'Unknown findings (G):   {len(unknown_findings)}')
    for u in unknown_findings:
        print(f'  - {u}')
    print()
    print('Borea / Marchio Boreale safety:')
    print(f'  marchio_boreale total occurrences:  {sum(per_bucket["B_unique_personal_status"].values())}')
    print(f'  marchio_boreale leak in non-Borea:  {len(non_borea_marchio)}')
    print()
    print('DECISION GATE:')
    print(f'  decision_type:        {decision["decision_type"]}')
    print(f'  patch_needed:         {decision["patch_needed"]}')
    print(f'  allowed_patch_scope:  {decision["allowed_patch_scope"]}')
    print(f'  reason:               {decision["reason"]}')
    print()
    if failures:
        print('FAIL: audit found blocking issues:')
        for f in failures:
            print(f'  - {f}')
        return 1
    print('PASS: RM1.30-B audit clean.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
