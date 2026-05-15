#!/usr/bin/env python3
"""
RM1.28-E — 5★ Manual Review Residual Mapping (targeted patch)
─────────────────────────────────────────────────────────────────────────
Resolves the 5 manual_review_required residual slots left by RM1.28-D
based on each slot's `design_summary` text.

Idempotent. Read-only on every other slot.
NO DB writes. NO runtime hookup. NO touch outside the 5 target slots.

Decisions (all derived from each slot's design_summary):

  1. celtic_mist_banshee.passive_base
     summary: "Aumenta effect_accuracy e riduce speed nemica."
     → add status_tags: effect_accuracy_up, speed_down
     → close manual_review

  2. cursed_pestilence_herald.passive_base
     summary: "Nemici con DoT ricevono meno cure."
     → add status_tags: healing_reduction
     → close manual_review

  3. creature_crimson_phoenix.skill_1
     summary: "Danno fuoco e HoT su sé stessa."
     → add status_tags: regeneration (HoT = healing over time on self)
     → close manual_review

  4. creature_lernaean_hydra.skill_2
     summary: "Colpisce 3 nemici e ottiene HoT."
     → add status_tags: regeneration (HoT on self after damage)
     → close manual_review

  5. egyptian_claw_of_sekhmet.skill_1
     summary: "Danno forte e burn al bersaglio."
     → add status_tags: burn (legacy "dot" was alias for the explicit burn)
     → close manual_review
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

FULL_CATALOG = Path('/app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json')

APPROVED_STATUS_WHITELIST = {
    'stun', 'freeze', 'silence', 'blind', 'taunt', 'slow', 'speed_down', 'speed_up',
    'burn', 'bleed', 'poison', 'curse', 'frostbite', 'shock', 'atk_up', 'def_up',
    'crit_up', 'crit_damage_up', 'vulnerability', 'def_down', 'effect_accuracy_up',
    'magic_damage_up', 'physical_shield', 'magical_shield', 'hybrid_shield',
    'damage_reduction', 'guard', 'immunity', 'healing_up', 'healing_reduction',
    'healing_block', 'regeneration', 'cleanse', 'revive', 'revive_pending',
    'death_protection', 'mark', 'berserk',
}

# (hero_id, slot, [statuses to add to status_tags], decision_note)
TARGET_PATCHES = [
    (
        'celtic_mist_banshee', 'passive_base',
        ['effect_accuracy_up', 'speed_down'],
        'design_summary explicitly states "Aumenta effect_accuracy e riduce '
        'speed nemica" — RM1.28-E maps legacy "aura_debuff" to '
        'effect_accuracy_up (self) + speed_down (enemies).',
    ),
    (
        'cursed_pestilence_herald', 'passive_base',
        ['healing_reduction'],
        'design_summary explicitly states "Nemici con DoT ricevono meno cure" — '
        'RM1.28-E maps legacy "debuff_aura" to healing_reduction targeting '
        'enemies with DoT.',
    ),
    (
        'creature_crimson_phoenix', 'skill_1',
        ['regeneration'],
        'design_summary explicitly states "Danno fuoco e HoT su sé stessa" — '
        'RM1.28-E maps legacy "hot" to regeneration on self (HoT semantics).',
    ),
    (
        'creature_lernaean_hydra', 'skill_2',
        ['regeneration'],
        'design_summary explicitly states "Colpisce 3 nemici e ottiene HoT" — '
        'RM1.28-E maps legacy "hot" to regeneration on self after damage.',
    ),
    (
        'egyptian_claw_of_sekhmet', 'skill_1',
        ['burn'],
        'design_summary explicitly states "Danno forte e burn al bersaglio" — '
        'RM1.28-E maps legacy "dot" to burn (legacy alias for the explicit '
        'burn already present in summary).',
    ),
]

# Legacy taxonomy tags that should be cleaned from design_taxonomy_tags
# once they have been resolved into concrete statuses.
LEGACY_TO_REMOVE_FROM_TAXONOMY = {'dot', 'hot'}


def add_unique(lst, item):
    if item not in lst:
        lst.append(item)


def patch_slot(slot: dict, hid: str, slot_name: str,
               add_statuses: list[str], decision_note: str,
               stats: dict) -> bool:
    # Sanity
    if slot.get('manual_review_required') is not True:
        # Already resolved (idempotency)
        stats['already_resolved'] += 1
        return False

    # Add concrete approved statuses
    tags = list(slot.get('status_tags') or [])
    for st in add_statuses:
        if st not in APPROVED_STATUS_WHITELIST:
            raise ValueError(f'attempted to add non-whitelist status "{st}" to {hid}.{slot_name}')
        add_unique(tags, st)
    slot['status_tags'] = tags

    # Optionally clean up legacy taxonomy entries that were resolved
    tax = list(slot.get('design_taxonomy_tags') or [])
    removed = [t for t in tax if t in LEGACY_TO_REMOVE_FROM_TAXONOMY]
    tax = [t for t in tax if t not in LEGACY_TO_REMOVE_FROM_TAXONOMY]
    if tax:
        slot['design_taxonomy_tags'] = tax
    elif 'design_taxonomy_tags' in slot:
        # Keep field but allow empty list; remove if empty to keep file tidy
        if not tax:
            del slot['design_taxonomy_tags']

    # Append clearer note
    notes = list(slot.get('normalization_notes') or [])
    add_unique(notes, f'RM1.28-E: {decision_note}')
    if removed:
        add_unique(notes,
                   f'RM1.28-E: removed legacy taxonomy entries {removed} '
                   f'after resolution to concrete status_tags={add_statuses}.')
    slot['normalization_notes'] = notes

    # Close manual review
    slot['manual_review_required'] = False

    # Update normalization_metadata
    nmeta = slot.get('normalization_metadata') or {}
    rm_e_block = {
        'resolved_at_utc': datetime.now(timezone.utc).isoformat(),
        'resolved_by': 'RM1.28-E',
        'added_status_tags': list(add_statuses),
        'removed_from_taxonomy': removed,
        'decision_note': decision_note,
    }
    history = nmeta.get('rm128e_resolution_history') or []
    # Idempotency: don't append duplicate identical resolution blocks
    if not any(h.get('decision_note') == decision_note for h in history):
        history.append(rm_e_block)
    nmeta['rm128e_resolution_history'] = history
    nmeta['last_normalized_at_utc'] = datetime.now(timezone.utc).isoformat()
    slot['normalization_metadata'] = nmeta
    return True


def main() -> int:
    if not FULL_CATALOG.exists():
        print(f'FAIL: missing {FULL_CATALOG}')
        return 1
    data = json.loads(FULL_CATALOG.read_text(encoding='utf-8'))
    entries = data.get('entries', []) or []

    # Find all currently-flagged manual_review_required slots (sanity scan)
    review_slots_before = []
    for e in entries:
        sp = e.get('skill_package') or {}
        for slot_name, slot in sp.items():
            if isinstance(slot, dict) and slot.get('manual_review_required') is True:
                review_slots_before.append((e['hero_id'], slot_name))

    expected = {(h, s) for (h, s, *_rest) in TARGET_PATCHES}
    unexpected = set(review_slots_before) - expected
    missing_targets = expected - set(review_slots_before)
    if unexpected:
        print(f'STOP: unexpected manual_review slots found (NOT in RM1.28-E target list): {sorted(unexpected)}')
        # We do not patch anything if the catalog has drifted; reporting only.
        return 1
    if missing_targets:
        # Could be all already resolved (idempotent re-run).
        # Only stop if we cannot find them at all.
        for hid, slot_name in missing_targets:
            e = next((x for x in entries if x.get('hero_id') == hid), None)
            if e is None or slot_name not in (e.get('skill_package') or {}):
                print(f'STOP: target slot missing: {hid}.{slot_name}')
                return 1

    stats = {'resolved_now': 0, 'already_resolved': 0}
    for hid, slot_name, add_statuses, decision_note in TARGET_PATCHES:
        e = next(x for x in entries if x['hero_id'] == hid)
        slot = e['skill_package'][slot_name]
        if patch_slot(slot, hid, slot_name, add_statuses, decision_note, stats):
            stats['resolved_now'] += 1

    # Update catalog-level notes (idempotent)
    notes = data.get('notes')
    marker = ('RM1.28-E: resolved 5 manual_review residual slots '
              '(banshee.passive_base, pestilence_herald.passive_base, '
              'crimson_phoenix.skill_1, lernaean_hydra.skill_2, '
              'claw_of_sekhmet.skill_1).')
    if isinstance(notes, list):
        if marker not in notes:
            notes.append(marker)
            data['notes'] = notes
    elif isinstance(notes, str):
        if marker not in notes:
            data['notes'] = (notes + ' ' + marker).strip()
    else:
        data['notes'] = marker

    stats_block = data.get('stats') or {}
    if isinstance(stats_block, dict):
        stats_block['rm128e_residuals_resolved'] = True
        stats_block['rm128e_stats'] = stats
        data['stats'] = stats_block

    FULL_CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    # Re-scan to confirm
    data2 = json.loads(FULL_CATALOG.read_text(encoding='utf-8'))
    review_after = []
    for e in data2.get('entries', []) or []:
        sp = e.get('skill_package') or {}
        for slot_name, slot in sp.items():
            if isinstance(slot, dict) and slot.get('manual_review_required') is True:
                review_after.append((e['hero_id'], slot_name))

    print('RM1.28-E resolution applied:')
    print(f'  manual_review BEFORE: {len(review_slots_before)} slots ({sorted(review_slots_before)})')
    print(f'  resolved now:         {stats["resolved_now"]}')
    print(f'  already resolved:     {stats["already_resolved"]}')
    print(f'  manual_review AFTER:  {len(review_after)} slots ({sorted(review_after)})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
