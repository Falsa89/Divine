#!/usr/bin/env python3
"""Validate RM1.25-B inert skill/status/icon/VFX metadata catalogs."""
from __future__ import annotations

import json
import os
from pathlib import Path

BASE = Path(os.environ.get('APP_ROOT', '/app'))
CATALOG_DIR = BASE / 'data' / 'design' / 'skill_status_vfx_catalogs'
REQUIRED_FILES = {
    'skill_slots': CATALOG_DIR / 'skill_slot_progression_v1.json',
    'statuses': CATALOG_DIR / 'status_effect_catalog_v1.json',
    'icons': CATALOG_DIR / 'status_icon_registry_v1.json',
    'vfx': CATALOG_DIR / 'vfx_modular_catalog_v1.json',
    'examples': CATALOG_DIR / 'skill_schema_examples_v1.json',
}

EXPECTED_ELEMENTS = ['dark', 'earth', 'fire', 'light', 'lightning', 'water', 'wind']
EXPECTED_STATUS_IDS = {
    'stun', 'freeze', 'silence', 'blind', 'taunt', 'slow', 'speed_down', 'speed_up',
    'burn', 'bleed', 'poison', 'curse', 'frostbite', 'shock',
    'atk_up', 'def_up', 'crit_up', 'crit_damage_up', 'vulnerability', 'def_down',
    'effect_accuracy_up', 'magic_damage_up',
    'physical_shield', 'magical_shield', 'hybrid_shield', 'damage_reduction', 'guard', 'immunity',
    'healing_up', 'healing_reduction', 'healing_block', 'regeneration', 'cleanse', 'revive',
    'revive_pending', 'death_protection', 'mark', 'marchio_boreale', 'berserk', 'domain_effect',
}
EXPECTED_VFX_TYPES = {
    'apply_vfx', 'projectile_vfx', 'travel_vfx', 'impact_vfx', 'persistent_status_vfx',
    'stack_gain_vfx', 'stack_decay_vfx', 'expire_vfx', 'cleanse_vfx', 'field_domain_vfx',
    'screen_edge_vfx', 'fullscreen_vfx',
}
EXPECTED_SLOTS = {
    '1': ['basic'],
    '2': ['basic', 'passive_base'],
    '3': ['basic', 'passive_base', 'skill_1'],
    '4': ['basic', 'passive_base', 'skill_1', 'passive_advanced'],
    '5': ['basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2'],
    '6': ['basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2', 'ultimate'],
}


def load_json(path: Path) -> dict:
    if not path.exists():
        raise AssertionError(f'Missing required file: {path}')
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def main() -> None:
    data = {key: load_json(path) for key, path in REQUIRED_FILES.items()}

    elements = data['statuses'].get('official_elements')
    assert elements == EXPECTED_ELEMENTS, f'official_elements mismatch: {elements}'

    slots = data['skill_slots'].get('official_skill_slots_by_native_rarity')
    assert slots == EXPECTED_SLOTS, f'skill slot progression mismatch: {slots}'

    statuses = data['statuses'].get('statuses', [])
    status_ids = [s.get('status_id') for s in statuses]
    assert len(status_ids) == len(set(status_ids)), 'Duplicate status_id found'
    assert set(status_ids) == EXPECTED_STATUS_IDS, f'status id mismatch: missing={EXPECTED_STATUS_IDS-set(status_ids)} extra={set(status_ids)-EXPECTED_STATUS_IDS}'
    assert data['statuses'].get('status_count') == 40, 'status_count must be 40'

    icons = data['icons'].get('icons', [])
    icon_by_status = {i.get('status_id'): i for i in icons}
    assert set(icon_by_status) == EXPECTED_STATUS_IDS, 'Icon registry must cover every status'
    for sid, icon in icon_by_status.items():
        assert icon.get('icon_key') == f'status_{sid}', f'icon_key mismatch for {sid}'
        for flag in ['transparent_background', 'no_text', 'no_numbers', 'no_letters', 'no_watermark', 'no_baked_stack_or_duration']:
            assert icon.get(flag) is True, f'{sid} icon must set {flag}=true'
        assert 32 in icon.get('export_sizes_px', []), f'{sid} icon missing 32px export size'

    vfx_types = set(data['vfx'].get('vfx_types', []))
    assert vfx_types == EXPECTED_VFX_TYPES, f'VFX type mismatch: {vfx_types}'
    vfx_entries = data['vfx'].get('vfx_entries', [])
    vfx_ids = {v.get('vfx_id') for v in vfx_entries}
    for status in statuses:
        sid = status['status_id']
        refs = status.get('vfx_refs', {})
        for ref_key in ['apply_vfx', 'persistent_status_vfx', 'expire_vfx', 'cleanse_vfx']:
            ref = refs.get(ref_key)
            assert ref, f'{sid} missing {ref_key}'
            assert ref in vfx_ids, f'{sid} references missing VFX id {ref}'
        assert status.get('icon_key') == f'status_{sid}', f'{sid} icon_key mismatch in status catalog'

    examples = data['examples'].get('examples', [])
    assert len(examples) >= 4, 'Expected at least 4 skill schema examples'
    for ex in examples:
        pf = ex.get('presentation_flow')
        assert isinstance(pf, dict), f'example {ex.get("example_id")} missing presentation_flow'
        assert 'source_actor_motion' in pf, f'example {ex.get("example_id")} missing source_actor_motion'
        assert 'target_impact_vfx' in pf, f'example {ex.get("example_id")} missing target_impact_vfx'
        assert 'return_motion' in pf, f'example {ex.get("example_id")} missing return_motion'

    print('PASS: RM1.25-B metadata catalogs validated')
    print(f'- official elements: {elements} ({len(elements)})')
    print(f'- core statuses: {len(statuses)}')
    print(f'- status icons: {len(icons)}')
    print(f'- vfx types: {len(vfx_types)}')
    print(f'- vfx entries: {len(vfx_entries)}')
    print(f'- skill examples: {len(examples)}')


if __name__ == '__main__':
    main()
