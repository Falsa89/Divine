#!/usr/bin/env python3
"""
RM1.28-D — 5★ Legacy Status Tags Controlled Normalization Patch
─────────────────────────────────────────────────────────────────────────
Applies the conservative design-only normalization approved by RM1.28-C
to non-passive_advanced slots of /app/data/design/hero_skill_kits/
hero_skill_kits_5star_full_v1.json.

Idempotent. NO DB writes. NO runtime hookups. NO mutation outside the
inspected slots. passive_advanced is preserved EXACTLY as-is.

Bucket rules:
  A (damage/buff/debuff/control/heal) → move to slot.design_taxonomy_tags
  B (dot/hot/shield)                  → context map only if obvious,
                                         else move to design_taxonomy_tags
                                         + normalization_notes +
                                         manual_review_required=true
  C (trigger/conditional_bonus)       → trigger / rule_tags
  D (aura_debuff/debuff_aura)         → manual_review_required=true,
                                         move tag to normalization_notes
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/app/data/design/hero_skill_kits')
FULL_CATALOG = BASE / 'hero_skill_kits_5star_full_v1.json'
PLAN = BASE / 'hero_skill_kits_5star_legacy_status_tags_normalization_plan_v1.json'

LEGACY_SLOTS = ('basic', 'passive_base', 'skill_1', 'skill_2')

APPROVED_STATUS_WHITELIST = {
    'stun', 'freeze', 'silence', 'blind', 'taunt', 'slow', 'speed_down', 'speed_up',
    'burn', 'bleed', 'poison', 'curse', 'frostbite', 'shock', 'atk_up', 'def_up',
    'crit_up', 'crit_damage_up', 'vulnerability', 'def_down', 'effect_accuracy_up',
    'magic_damage_up', 'physical_shield', 'magical_shield', 'hybrid_shield',
    'damage_reduction', 'guard', 'immunity', 'healing_up', 'healing_reduction',
    'healing_block', 'regeneration', 'cleanse', 'revive', 'revive_pending',
    'death_protection', 'mark', 'berserk', 'domain_effect',
}

BUCKET_A = {'damage', 'buff', 'debuff', 'control', 'heal'}
BUCKET_B = {'dot', 'hot', 'shield'}
BUCKET_C = {'trigger', 'conditional_bonus'}
BUCKET_D = {'aura_debuff', 'debuff_aura'}

# Bucket B obvious context mappings (hero_id, slot, legacy_tag) -> concrete_status
# Only filled when hero identity makes mapping safe. Anything not here goes to
# manual_review_required.
OBVIOUS_MAPPINGS: dict[tuple[str, str, str], str] = {
    # dot → concrete DoT status
    ('creature_lernaean_hydra',   'skill_1', 'dot'): 'poison',
    ('cursed_pestilence_herald',  'skill_1', 'dot'): 'poison',
    ('demonic_gehenna_witch',     'skill_1', 'dot'): 'burn',
    ('yokai_oni_kunoichi',        'skill_1', 'dot'): 'bleed',
    # egyptian_claw_of_sekhmet skill_1 has both burn (already in tags) and bleed
    # candidates; ambiguous → manual_review (intentionally not mapped here).

    # hot → regeneration on phoenix passive (continuous HoT identity)
    ('creature_crimson_phoenix',  'passive_base', 'hot'): 'regeneration',
    # phoenix.skill_1 'hot' is ambiguous (direct heal vs over-time) → manual_review
    # (intentionally not mapped here).

    # shield on angelic_bastion_angel → physical_shield (tank/bastion identity)
    ('angelic_bastion_angel',     'skill_1', 'shield'): 'physical_shield',
    ('angelic_bastion_angel',     'skill_2', 'shield'): 'physical_shield',
}

# Bucket C → field placement
BUCKET_C_FIELD = {
    'trigger':           'trigger_tags',
    'conditional_bonus': 'rule_tags',
}


def ensure_list(d: dict, key: str) -> list:
    v = d.get(key)
    if not isinstance(v, list):
        d[key] = []
    return d[key]


def add_unique(lst: list, item):
    if item not in lst:
        lst.append(item)


def normalize_slot(hero_id: str, slot_name: str, slot: dict, stats: dict) -> bool:
    """In-place normalization of one slot. Returns True if modified."""
    if slot_name == 'passive_advanced':
        return False
    if not isinstance(slot, dict):
        return False
    tags = list(slot.get('status_tags') or [])
    if not tags:
        return False

    new_status_tags: list[str] = []
    design_taxonomy_tags = ensure_list(slot, 'design_taxonomy_tags')
    rule_tags = ensure_list(slot, 'rule_tags')
    trigger_tags = ensure_list(slot, 'trigger_tags')
    notes = ensure_list(slot, 'normalization_notes')
    manual_review = bool(slot.get('manual_review_required', False))

    modified = False
    for t in tags:
        if t in APPROVED_STATUS_WHITELIST:
            new_status_tags.append(t)
        elif t in BUCKET_A:
            add_unique(design_taxonomy_tags, t)
            stats['bucket_A_moved'] += 1
            modified = True
        elif t in BUCKET_B:
            target = OBVIOUS_MAPPINGS.get((hero_id, slot_name, t))
            if target is not None:
                if target not in new_status_tags:
                    new_status_tags.append(target)
                add_unique(notes,
                           f'legacy_tag "{t}" → mapped to "{target}" per RM1.28-D '
                           f'(obvious identity match)')
                stats['bucket_B_mapped'] += 1
                modified = True
            else:
                add_unique(design_taxonomy_tags, t)
                add_unique(notes,
                           f'legacy_tag "{t}" preserved as design_taxonomy_tag · '
                           f'manual_review_required (Bucket B ambiguous)')
                manual_review = True
                stats['bucket_B_review'] += 1
                modified = True
        elif t in BUCKET_C:
            target_field = BUCKET_C_FIELD.get(t, 'rule_tags')
            target_list = trigger_tags if target_field == 'trigger_tags' else rule_tags
            add_unique(target_list, t)
            add_unique(notes,
                       f'legacy_tag "{t}" moved to {target_field} per RM1.28-D')
            stats['bucket_C_moved'] += 1
            modified = True
        elif t in BUCKET_D:
            add_unique(notes,
                       f'legacy_tag "{t}" removed from status_tags · '
                       f'manual_review_required (Bucket D ambiguous aura/debuff)')
            manual_review = True
            stats['bucket_D_review'] += 1
            modified = True
        else:
            # Unknown legacy tag (should not happen given audit was complete)
            add_unique(design_taxonomy_tags, t)
            add_unique(notes,
                       f'legacy_tag "{t}" preserved as design_taxonomy_tag · '
                       f'unknown bucket, manual_review_required')
            manual_review = True
            stats['bucket_unknown'] += 1
            modified = True

    if not modified:
        # Even if status_tags only contained whitelisted statuses, do not touch
        return False

    # Always preserve relative order/dedupe of new_status_tags
    seen = set()
    deduped = []
    for t in new_status_tags:
        if t not in seen:
            seen.add(t)
            deduped.append(t)
    slot['status_tags'] = deduped

    if manual_review:
        slot['manual_review_required'] = True
    else:
        # If we have notes for this slot but no manual_review_required toggle
        # was set during the modification, ensure the field exists with False
        if 'manual_review_required' not in slot:
            slot['manual_review_required'] = False

    # Strip empty new arrays we just initialized (idempotency)
    for k in ('design_taxonomy_tags', 'rule_tags', 'trigger_tags', 'normalization_notes'):
        if isinstance(slot.get(k), list) and not slot[k]:
            del slot[k]

    # Annotate normalization timestamp + task origin
    nmeta = slot.get('normalization_metadata') or {}
    nmeta.setdefault('task_origin', 'RM1.28-D')
    nmeta.setdefault('first_normalized_at_utc',
                     datetime.now(timezone.utc).isoformat())
    nmeta['last_normalized_at_utc'] = datetime.now(timezone.utc).isoformat()
    slot['normalization_metadata'] = nmeta
    return True


def main() -> int:
    if not FULL_CATALOG.exists():
        print(f'FAIL: missing {FULL_CATALOG}')
        return 1
    if not PLAN.exists():
        print(f'FAIL: missing RM1.28-C plan: {PLAN}')
        return 1

    data = json.loads(FULL_CATALOG.read_text(encoding='utf-8'))
    entries = data.get('entries', []) or []
    if len(entries) != 20:
        print(f'FAIL: expected 20 entries, got {len(entries)}')
        return 1

    stats = {
        'slots_modified': 0,
        'bucket_A_moved': 0,
        'bucket_B_mapped': 0,
        'bucket_B_review': 0,
        'bucket_C_moved': 0,
        'bucket_D_review': 0,
        'bucket_unknown': 0,
    }
    manual_review_entries: list[dict] = []
    for entry in entries:
        hid = entry.get('hero_id')
        sp = entry.get('skill_package') or {}
        for slot_name in LEGACY_SLOTS:
            slot = sp.get(slot_name)
            if slot is None:
                continue
            modified = normalize_slot(hid, slot_name, slot, stats)
            if modified:
                stats['slots_modified'] += 1
                if slot.get('manual_review_required'):
                    manual_review_entries.append({
                        'hero_id': hid,
                        'slot': slot_name,
                        'status_tags': list(slot.get('status_tags') or []),
                        'design_taxonomy_tags': list(slot.get('design_taxonomy_tags') or []),
                        'normalization_notes': list(slot.get('normalization_notes') or []),
                    })

    # Bump catalog notes (idempotent)
    notes = data.get('notes')
    marker = ('RM1.28-D: 5★ legacy status_tags normalized into '
              'design_taxonomy_tags/rule_tags/trigger_tags/normalization_notes '
              'per RM1.28-C plan. passive_advanced preserved.')
    if isinstance(notes, list):
        if marker not in notes:
            notes.append(marker)
            data['notes'] = notes
    elif isinstance(notes, str):
        if marker not in notes:
            data['notes'] = (notes + ' ' + marker).strip()
    else:
        data['notes'] = marker

    # Bump stats block
    stats_block = data.get('stats') or {}
    if isinstance(stats_block, dict):
        stats_block['legacy_status_tags_normalized_by_rm128d'] = True
        stats_block['rm128d_stats'] = stats
        data['stats'] = stats_block

    FULL_CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    print('RM1.28-D normalization complete:')
    print(f'  slots_modified:    {stats["slots_modified"]}')
    print(f'  Bucket A moved:    {stats["bucket_A_moved"]}')
    print(f'  Bucket B mapped:   {stats["bucket_B_mapped"]}')
    print(f'  Bucket B review:   {stats["bucket_B_review"]}')
    print(f'  Bucket C moved:    {stats["bucket_C_moved"]}')
    print(f'  Bucket D review:   {stats["bucket_D_review"]}')
    print(f'  unknown (review):  {stats["bucket_unknown"]}')
    print(f'  manual_review entries: {len(manual_review_entries)}')
    for m in manual_review_entries:
        print(f'    {m["hero_id"]:<32}.{m["slot"]:<15} status_tags={m["status_tags"]}'
              f' taxonomy={m["design_taxonomy_tags"]} notes={m["normalization_notes"]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
