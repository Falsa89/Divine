#!/usr/bin/env python3
"""build_hero_asset_import_manifest_preview.py — v54 Track C.

Read-only scanner of frontend/assets/heroes producing a manifest preview JSON.
NO asset copy, NO mutation, NO Character Bible touch.
"""
from __future__ import annotations
import json, os, sys

ROOT = '/app'
RULES = os.path.join(ROOT, 'data/design/assets/hero_asset_import_manifest_rules_v1.json')
OUT = os.path.join(ROOT, 'data/design/assets/hero_asset_import_manifest_preview_v1.json')
HEROES_DIR = os.path.join(ROOT, 'frontend/assets/heroes')


def classify(found_required: set, found_optional: set, required: list, optional: list) -> str:
    if not required:
        return 'needs_manual_review'
    missing_req = [s for s in required if s not in found_required]
    if missing_req:
        return 'missing_required_asset'
    missing_opt = [s for s in optional if s not in found_optional]
    if missing_opt:
        return 'missing_optional_asset'
    return 'ready_to_import'


def main() -> int:
    if not os.path.exists(RULES):
        print('ERROR: missing rules JSON:', RULES); return 1
    rules = json.load(open(RULES))
    required = list(rules.get('required_slots') or [])
    optional = list(rules.get('optional_slots') or [])
    patterns = rules.get('slot_filename_patterns') or {}

    heroes = []
    scaffolded = False
    if not os.path.isdir(HEROES_DIR):
        # Scaffold instruction only — do NOT create heroes
        scaffolded = True
    else:
        for hero_id in sorted(os.listdir(HEROES_DIR)):
            hp = os.path.join(HEROES_DIR, hero_id)
            if not os.path.isdir(hp):
                continue
            files_lower = {fn.lower() for fn in os.listdir(hp)}
            found_required: set = set()
            found_optional: set = set()
            for slot, names in patterns.items():
                matched = any(n.lower() in files_lower for n in names)
                if matched:
                    if slot in required:
                        found_required.add(slot)
                    elif slot in optional:
                        found_optional.add(slot)
            state = classify(found_required, found_optional, required, optional)
            heroes.append({
                'hero_id': hero_id,
                'found_required': sorted(found_required),
                'found_optional': sorted(found_optional),
                'missing_required': sorted([s for s in required if s not in found_required]),
                'missing_optional': sorted([s for s in optional if s not in found_optional]),
                'readiness': state,
            })

    summary = {
        'total_heroes_scanned': len(heroes),
        'ready_to_import': sum(1 for h in heroes if h['readiness'] == 'ready_to_import'),
        'missing_required_asset': sum(1 for h in heroes if h['readiness'] == 'missing_required_asset'),
        'missing_optional_asset': sum(1 for h in heroes if h['readiness'] == 'missing_optional_asset'),
        'needs_manual_review': sum(1 for h in heroes if h['readiness'] == 'needs_manual_review'),
        'rejected_wrong_contract': sum(1 for h in heroes if h['readiness'] == 'rejected_wrong_contract'),
    }
    manifest = {
        'version': 'hero_asset_import_manifest_preview_v1',
        'pack': 'MEGA_RELEASE_ACCELERATION_MASTER_BATCH_EXECUTION_PLAN_PACK_v54',
        'public_sync_tag': 'PUBLIC_SYNC_TAG_v54_MEGA_RELEASE_ACCELERATION_MASTER_BATCH_EXECUTION_PLAN',
        'mode': 'read_only_scan',
        'no_asset_copy': True,
        'no_asset_import': True,
        'frontend_assets_heroes_mutation': False,
        'character_bible_changed': False,
        'final_numbers_changed': False,
        'directory_root': 'frontend/assets/heroes',
        'directory_exists': os.path.isdir(HEROES_DIR),
        'scaffolded': scaffolded,
        'rules_ref': 'data/design/assets/hero_asset_import_manifest_rules_v1.json',
        'summary': summary,
        'heroes': heroes,
        'readiness_states_known': rules.get('readiness_states'),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump(manifest, f, indent=2)
    print('OK wrote', OUT, 'scanned', len(heroes), 'heroes')
    return 0


if __name__ == '__main__':
    sys.exit(main())
