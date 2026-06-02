#!/usr/bin/env python3
"""Validator: MEGA-RELEASE-ACCELERATION-1-v51-ROLLUP."""
from __future__ import annotations
import os, sys, hashlib, subprocess, json

ROOT = '/app'
SUITE_RUNNER = os.path.join(ROOT, 'backend/scripts/run_hero_skill_kit_validator_suite.py')
ROLLUP_MARKER = os.path.join(ROOT, 'data/design/release_acceleration/mega_release_acceleration_1_v51_rollup_marker_v1.json')

REQUIRED_TUPLES = [
    "'PROJECT-MATERIAL-RAID-PLAYABLE-ALPHA-SLICE'",
    "'PROJECT-VISUAL-BATTLE-ROUTING-PLAYABLE-SLICE-AUDIT'",
    "'PROJECT-HERO-ASSET-IMPORT-READINESS-SCHEMA'",
    "'PROJECT-GUIDE-CODEX-ONBOARDING-ALPHA-FOUNDATION'",
    "'PROJECT-DEVICE-BETA-TESTER-SMOKE-MATRIX'",
    "'MEGA-RELEASE-ACCELERATION-1-v51-ROLLUP'",
]
PUBLIC_SYNC_TAG = 'PUBLIC_SYNC_TAG_v51_MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION'
MD5_INVARIANTS = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env': 'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx': '45fcc9890b6b128c37088bc33aa54caf',
}
DEPENDENT = [
    'validate_material_raid_playable_alpha_slice_v1.py',
    'validate_visual_battle_routing_playable_slice_audit_v1.py',
    'validate_hero_asset_import_readiness_schema_v1.py',
    'validate_guide_codex_onboarding_alpha_foundation_v1.py',
    'validate_device_beta_tester_smoke_matrix_v1.py',
]
REQUIRED_DOCS = [
    'docs/divine/297_DEVICE_QA_AND_BETA_TESTER_SMOKE_MATRIX.md',
    'docs/divine/298_MATERIAL_RAID_PLAYABLE_ALPHA_SLICE.md',
    'docs/divine/299_VISUAL_BATTLE_ROUTING_PLAYABLE_SLICE_AUDIT.md',
    'docs/divine/300_ASSET_IMPORT_READINESS_40_HEROES.md',
    'docs/divine/301_GUIDE_CODEX_ONBOARDING_ALPHA_FOUNDATION.md',
    'docs/divine/302_MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION_v51.md',
]

FAILS = []
def fail(m): FAILS.append(m)

# [1] MD5 invariants — 5 core files unchanged
for rel, expected in MD5_INVARIANTS.items():
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p): fail(f'[1] missing {rel}'); continue
    h = hashlib.md5(open(p, 'rb').read()).hexdigest()
    if h != expected: fail(f'[1] MD5 mismatch {rel}: got {h}')

# [2] Suite runner tuples + public sync tag
if not os.path.exists(SUITE_RUNNER): fail('[2] missing suite runner')
else:
    sr = open(SUITE_RUNNER).read()
    for t in REQUIRED_TUPLES:
        if sr.count(t) != 1: fail(f'[2] suite must have exactly 1 of {t} got {sr.count(t)}')
    if PUBLIC_SYNC_TAG not in sr: fail(f'[2] suite missing tag {PUBLIC_SYNC_TAG}')

# [3] Dependent validators must pass
for v in DEPENDENT:
    vp = os.path.join(ROOT, 'backend/scripts', v)
    if not os.path.exists(vp): fail(f'[3] missing validator {v}'); continue
    r = subprocess.run([sys.executable, vp], capture_output=True, text=True)
    if r.returncode != 0:
        fail(f'[3] dependent validator {v} returned {r.returncode}')
        print(r.stdout[-500:]); print(r.stderr[-500:])

# [4] Required docs exist
for d in REQUIRED_DOCS:
    p = os.path.join(ROOT, d)
    if not os.path.exists(p): fail(f'[4] missing doc {d}')

# [5] Rollup marker invariants
if not os.path.exists(ROLLUP_MARKER): fail(f'[5] missing rollup marker: {ROLLUP_MARKER}')
else:
    m = json.load(open(ROLLUP_MARKER))
    for k, v in (
        ('marker_version', 'mega_release_acceleration_1_v51_rollup_marker_v1'),
        ('pack', 'MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION_PACK_v51'),
        ('public_sync_tag', PUBLIC_SYNC_TAG),
        ('db_writes', 0),
        ('real_db_writes', 0),
        ('production_db_touched', False),
        ('mongo_url_used', False),
        ('pymongo_used', False),
        ('motor_used', False),
        ('redis_used', False),
        ('filesystem_writes', 0),
        ('live_apply_allowed', False),
        ('live_enforcement_enabled', False),
        ('reward_claim_live', False),
        ('materials_granted', False),
        ('inventory_mutation', False),
        ('premium_users_gems_mutated', False),
        ('mail_state_mutation', False),
        ('bp_delta_runtime_change', False),
        ('stamina_used', False),
        ('tickets_used', False),
        ('paid_attempts', False),
        ('gacha_shop_vip_bp_monetization_change', False),
        ('home_menu_mandatory_routing', False),
        ('server_py_changed', False),
        ('battle_engine_changed', False),
        ('combat_tsx_changed', False),
        ('story_tsx_changed', False),
        ('character_bible_changed', False),
        ('final_numbers_changed', False),
        ('frontend_assets_heroes_changed', False),
        ('hero_contracts_changed', False),
        ('existing_endpoint_paths_changed', False),
        ('existing_feature_flags_changed', False),
        ('existing_default_503_changed', False),
        ('safety_flags_changed', False),
        ('validator_weakening', False),
        ('fake_pass', False),
    ):
        if m.get(k) != v: fail(f'[5] rollup marker {k} != {v} (got {m.get(k)})')
    if m.get('tracks') != ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
        fail(f'[5] rollup marker tracks != [A..G] (got {m.get("tracks")})')
    if m.get('suite_tuples') != [
        'PROJECT-MATERIAL-RAID-PLAYABLE-ALPHA-SLICE',
        'PROJECT-VISUAL-BATTLE-ROUTING-PLAYABLE-SLICE-AUDIT',
        'PROJECT-HERO-ASSET-IMPORT-READINESS-SCHEMA',
        'PROJECT-GUIDE-CODEX-ONBOARDING-ALPHA-FOUNDATION',
        'PROJECT-DEVICE-BETA-TESTER-SMOKE-MATRIX',
        'MEGA-RELEASE-ACCELERATION-1-v51-ROLLUP',
    ]:
        fail(f'[5] rollup marker suite_tuples mismatch')
    md5_block = m.get('md5_invariants') or {}
    for rel, expected in MD5_INVARIANTS.items():
        if md5_block.get(rel) != expected:
            fail(f'[5] rollup marker md5_invariants {rel} != {expected} (got {md5_block.get(rel)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] MEGA_RELEASE_ACCELERATION_1_v51_ROLLUP validator')
    sys.exit(1)
print('[PASS] MEGA_RELEASE_ACCELERATION_1_v51_ROLLUP validator')
sys.exit(0)
