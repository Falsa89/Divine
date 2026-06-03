#!/usr/bin/env python3
"""Validator: PROJECT-HERO-ASSET-IMPORT-MANIFEST-PREVIEW (v54 Track C)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
RULES = os.path.join(ROOT, 'data/design/assets/hero_asset_import_manifest_rules_v1.json')
MANIFEST = os.path.join(ROOT, 'data/design/assets/hero_asset_import_manifest_preview_v1.json')
SCANNER = os.path.join(ROOT, 'backend/scripts/build_hero_asset_import_manifest_preview.py')
MARKER = os.path.join(ROOT, 'data/design/assets/hero_asset_import_manifest_preview_marker_v1.json')
TAG = 'PUBLIC_SYNC_TAG_v54_MEGA_RELEASE_ACCELERATION_MASTER_BATCH_EXECUTION_PLAN'

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(SCANNER): fail('missing scanner script')
else:
    src = open(SCANNER).read()
    # No forbidden imports / mutation
    for forb in ('shutil.copy', 'shutil.move', 'os.rename', 'os.makedirs(HEROES_DIR', 'open(.*frontend/assets/heroes.*, .w'):
        # simple substring search for the literal
        if forb in src:
            fail(f'scanner contains forbidden token: {forb}')
    for forb in ('import pymongo', 'from pymongo', 'import motor', 'from motor', 'import redis', 'from redis', 'MONGO_URL'):
        if forb in src: fail(f'scanner forbidden import: {forb}')

if not os.path.exists(RULES): fail('missing rules')
else:
    r = json.load(open(RULES))
    if r.get('public_sync_tag') != TAG: fail('rules public_sync_tag mismatch')
    if r.get('mode') != 'read_only_scan': fail('rules mode != read_only_scan')
    if r.get('no_asset_copy') is not True: fail('rules no_asset_copy != true')
    if r.get('no_asset_import') is not True: fail('rules no_asset_import != true')
    if r.get('character_bible_changed') is not False: fail('rules character_bible_changed != false')
    if r.get('final_numbers_changed') is not False: fail('rules final_numbers_changed != false')
    req = set(r.get('required_slots') or [])
    expected_req = {'splash','portrait','card','detail','fullscreen','combat_base'}
    if req != expected_req: fail(f'rules required_slots mismatch: {sorted(req)}')
    opt = set(r.get('optional_slots') or [])
    expected_opt_subset = {'idle_sheet','attack_sheet','skill_sheet','hit_sheet','death_sheet','battle_animations_json','metadata'}
    if not expected_opt_subset.issubset(opt): fail(f'rules optional_slots missing: {sorted(expected_opt_subset - opt)}')
    states = set(r.get('readiness_states') or [])
    expected_states = {'ready_to_import','missing_required_asset','missing_optional_asset','needs_manual_review','rejected_wrong_contract'}
    if states != expected_states: fail(f'rules readiness_states mismatch: {sorted(states)}')

if not os.path.exists(MANIFEST): fail('missing manifest (run scanner first)')
else:
    m = json.load(open(MANIFEST))
    if m.get('public_sync_tag') != TAG: fail('manifest public_sync_tag mismatch')
    if m.get('mode') != 'read_only_scan': fail('manifest mode != read_only_scan')
    if m.get('no_asset_copy') is not True: fail('manifest no_asset_copy != true')
    if m.get('frontend_assets_heroes_mutation') is not False: fail('manifest frontend_assets_heroes_mutation != false')
    s = m.get('summary') or {}
    for k in ('total_heroes_scanned','ready_to_import','missing_required_asset','missing_optional_asset','needs_manual_review','rejected_wrong_contract'):
        if k not in s: fail(f'manifest summary missing {k}')
    if not isinstance(m.get('heroes'), list): fail('manifest heroes not list')

if not os.path.exists(MARKER): fail('missing marker')
else:
    mk = json.load(open(MARKER))
    for k, v in (
        ('marker_version','hero_asset_import_manifest_preview_marker_v1'),
        ('track','C'),
        ('public_sync_tag',TAG),
        ('mode','read_only_scan'),
        ('no_asset_copy',True),
        ('no_asset_import',True),
        ('frontend_assets_heroes_mutation',False),
        ('character_bible_changed',False),
        ('final_numbers_changed',False),
        ('db_writes',0),
        ('validator_weakening',False),
        ('fake_pass',False),
    ):
        if mk.get(k) != v: fail(f'marker {k} != {v} (got {mk.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-HERO-ASSET-IMPORT-MANIFEST-PREVIEW validator')
    sys.exit(1)
print('[PASS] PROJECT-HERO-ASSET-IMPORT-MANIFEST-PREVIEW validator')
sys.exit(0)
