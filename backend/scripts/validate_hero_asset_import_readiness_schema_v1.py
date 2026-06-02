#!/usr/bin/env python3
"""Validator: PROJECT-HERO-ASSET-IMPORT-READINESS-SCHEMA (v51 Track D).

Must PASS even when no real hero asset files exist yet in the repo.
Validates schema structure + report scaffold + marker.
"""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
SCHEMA = os.path.join(ROOT, 'data/design/assets/hero_asset_import_readiness_schema_v1.json')
REPORT = os.path.join(ROOT, 'data/design/assets/hero_asset_import_readiness_report_v1.json')
MARKER = os.path.join(ROOT, 'data/design/assets/hero_asset_import_readiness_marker_v1.json')

REQUIRED_SLOTS = {
    'hero_id', 'rarity', 'faction', 'element', 'role',
    'splash', 'portrait', 'card', 'detail', 'fullscreen',
    'combat_base',
    'idle_sheet', 'attack_sheet', 'skill_sheet', 'hit_sheet', 'death_sheet',
    'battle_animations_json',
    'source_reference_notes', 'chroma_status', 'alpha_cleanup_status',
}
REQUIRED_CATEGORIES = {
    'ready_to_import', 'missing_non_blocking_metadata',
    'missing_required_asset', 'needs_manual_review', 'rejected_wrong_contract',
}

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(SCHEMA): fail(f'missing schema: {SCHEMA}')
else:
    s = json.load(open(SCHEMA))
    if s.get('contract_version') != 'hero_asset_import_readiness_schema_v1':
        fail('schema contract_version mismatch')
    if s.get('design_only') is not True: fail('schema design_only must be true')
    if s.get('no_assets_imported_in_v51') is not True: fail('no_assets_imported_in_v51 must be true')
    if s.get('frontend_assets_heroes_changed') is not False: fail('frontend_assets_heroes_changed must be false')
    if s.get('hero_contracts_changed') is not False: fail('hero_contracts_changed must be false')
    if s.get('character_bible_changed') is not False: fail('character_bible_changed must be false')
    if s.get('final_numbers_changed') is not False: fail('final_numbers_changed must be false')
    slots = set(s.get('required_asset_slots') or [])
    miss = REQUIRED_SLOTS - slots
    if miss: fail(f'schema required_asset_slots missing: {sorted(miss)}')
    cats = set(s.get('readiness_categories') or [])
    miss_c = REQUIRED_CATEGORIES - cats
    if miss_c: fail(f'schema readiness_categories missing: {sorted(miss_c)}')
    specs = s.get('required_field_specs') or {}
    if not specs: fail('schema required_field_specs empty')
    if 'hero_id' not in specs or specs['hero_id'].get('required') is not True:
        fail('hero_id field spec required')
    if 'battle_animations_json' not in specs or specs['battle_animations_json'].get('required') is not True:
        fail('battle_animations_json field spec required')

if not os.path.exists(REPORT): fail(f'missing report: {REPORT}')
else:
    r = json.load(open(REPORT))
    if r.get('contract_version') != 'hero_asset_import_readiness_report_v1':
        fail('report contract_version mismatch')
    if r.get('design_only') is not True: fail('report design_only must be true')
    if r.get('assets_imported_in_v51') is not False: fail('report assets_imported_in_v51 must be false')
    if r.get('validator_must_not_fail_when_assets_missing') is not True:
        fail('report must explicitly allow zero-scaffold pass')
    if r.get('validator_must_pass_with_zero_scaffold') is not True:
        fail('report must explicitly allow zero-scaffold pass')
    if r.get('target_hero_count_estimate') != 40:
        fail(f'report target_hero_count_estimate != 40 (got {r.get("target_hero_count_estimate")})')
    if not isinstance(r.get('hero_entries_scaffold'), list):
        fail('hero_entries_scaffold must be a list (can be empty)')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('contract_version', 'hero_asset_import_readiness_schema_v1'),
        ('track', 'D'),
        ('target_hero_count_estimate', 40),
        ('assets_imported_in_v51', False),
        ('frontend_assets_heroes_changed', False),
        ('hero_contracts_changed', False),
        ('character_bible_changed', False),
        ('final_numbers_changed', False),
        ('db_writes', 0),
        ('filesystem_writes', 0),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v51_MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-HERO-ASSET-IMPORT-READINESS-SCHEMA validator')
    sys.exit(1)
print('[PASS] PROJECT-HERO-ASSET-IMPORT-READINESS-SCHEMA validator')
sys.exit(0)
