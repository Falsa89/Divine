#!/usr/bin/env python3
"""Validator: MEGA-RELEASE-ACCELERATION-6-v57-ROLLUP."""
from __future__ import annotations
import os, sys, hashlib, subprocess, json

ROOT = '/app'
SUITE_RUNNER = os.path.join(ROOT, 'backend/scripts/run_hero_skill_kit_validator_suite.py')
ROLLUP_MARKER = os.path.join(ROOT, 'data/design/release_acceleration/mega_release_acceleration_6_v57_rollup_marker_v1.json')

REQUIRED_TUPLES = [
    "'PROJECT-BOSS-VISUAL-PREVIEW-ROUTE-CONTRACT'",
    "'PROJECT-BOSS-VISUAL-PREVIEW-SCREEN'",
    "'PROJECT-GENERIC-ROUTER-BOSS-DETAIL'",
    "'PROJECT-BOSS-VISUAL-PREVIEW-ROUTE-SMOKE-MATRIX'",
    "'PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT-v2'",
    "'MEGA-RELEASE-ACCELERATION-6-v57-ROLLUP'",
]
PUBLIC_SYNC_TAG = 'PUBLIC_SYNC_TAG_v57_MEGA_RELEASE_ACCELERATION_6_BOSS_VISUAL_PREVIEW_ROUTE'
MD5_INVARIANTS = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env': 'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx': '45fcc9890b6b128c37088bc33aa54caf',
}
PREFERRED_UNCHANGED = {
    'frontend/app/combat.tsx': 'fc792a05b2ada6e677d80400732ae5c3',
    'frontend/app/story.tsx': '8520627b4e63f86821d73d8d3880bac3',
    'backend/server.py': '055df030553f4791e8cac14254f1b148',
}
DEPENDENT = [
    'validate_boss_visual_preview_route_contract_v1.py',
    'validate_boss_visual_preview_screen_v1.py',
    'validate_generic_router_boss_detail_v1.py',
    'validate_boss_visual_preview_route_smoke_matrix_v1.py',
    'validate_visual_preview_runtime_shell_progress_report_v2.py',
]
REQUIRED_DOCS = [
    'docs/divine/332_BOSS_VISUAL_PREVIEW_ROUTE_CONTRACT.md',
    'docs/divine/333_BOSS_VISUAL_PREVIEW_SCREEN.md',
    'docs/divine/334_GENERIC_ROUTER_BOSS_DETAIL_ENHANCEMENT.md',
    'docs/divine/335_BOSS_VISUAL_PREVIEW_QA_SMOKE.md',
    'docs/divine/336_VISUAL_PREVIEW_RUNTIME_SHELL_PROGRESS_REPORT_v2.md',
    'docs/divine/337_MEGA_RELEASE_ACCELERATION_6_BOSS_VISUAL_PREVIEW_ROUTE_v57.md',
]

FAILS = []
def fail(m): FAILS.append(m)

for rel, expected in MD5_INVARIANTS.items():
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p): fail(f'[1] missing {rel}'); continue
    h = hashlib.md5(open(p, 'rb').read()).hexdigest()
    if h != expected: fail(f'[1] MD5 mismatch {rel}: got {h}')
for rel, expected in PREFERRED_UNCHANGED.items():
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p): fail(f'[1b] missing {rel}'); continue
    h = hashlib.md5(open(p, 'rb').read()).hexdigest()
    if h != expected: fail(f'[1b] preferred-unchanged MD5 drift {rel}: got {h}')

if not os.path.exists(SUITE_RUNNER): fail('[2] missing suite runner')
else:
    sr = open(SUITE_RUNNER).read()
    for t in REQUIRED_TUPLES:
        if sr.count(t) != 1: fail(f'[2] suite must have exactly 1 of {t} got {sr.count(t)}')
    if PUBLIC_SYNC_TAG not in sr: fail(f'[2] suite missing tag {PUBLIC_SYNC_TAG}')

for v in DEPENDENT:
    vp = os.path.join(ROOT, 'backend/scripts', v)
    if not os.path.exists(vp): fail(f'[3] missing validator {v}'); continue
    r = subprocess.run([sys.executable, vp], capture_output=True, text=True)
    if r.returncode != 0:
        fail(f'[3] dependent validator {v} returned {r.returncode}')
        print(r.stdout[-500:]); print(r.stderr[-500:])

for d in REQUIRED_DOCS:
    if not os.path.exists(os.path.join(ROOT, d)): fail(f'[4] missing doc {d}')

if not os.path.exists(ROLLUP_MARKER): fail(f'[5] missing rollup marker: {ROLLUP_MARKER}')
else:
    m = json.load(open(ROLLUP_MARKER))
    for k, v in (
        ('marker_version', 'mega_release_acceleration_6_v57_rollup_marker_v1'),
        ('pack', 'MEGA_RELEASE_ACCELERATION_6_BOSS_VISUAL_PREVIEW_ROUTE_PACK_v57'),
        ('public_sync_tag', PUBLIC_SYNC_TAG),
        ('server_py_changed', False),
        ('battle_engine_changed', False),
        ('combat_tsx_changed', False),
        ('story_tsx_changed', False),
        ('battle_simulate_endpoint_changed', False),
        ('story_battle_endpoint_changed', False),
        ('existing_endpoint_paths_changed', False),
        ('existing_feature_flags_changed', False),
        ('existing_default_503_changed', False),
        ('safety_flags_changed', False),
        ('guild_war_policy_changed', False),
        ('guild_war_policy_regression', False),
        ('character_bible_changed', False),
        ('final_numbers_changed', False),
        ('db_writes', 0),
        ('real_db_writes', 0),
        ('mongo_url_used', False),
        ('pymongo_used', False),
        ('motor_used', False),
        ('redis_used', False),
        ('filesystem_writes', 0),
        ('live_apply_allowed', False),
        ('reward_grant_enabled', False),
        ('reward_claim_live', False),
        ('reward_claim_enabled', False),
        ('claim_button_enabled', False),
        ('materials_granted', False),
        ('inventory_mutation', False),
        ('battle_engine_runtime_used', False),
        ('result_authoritative', False),
        ('home_menu_mandatory_routing', False),
        ('asset_copy_or_import', False),
        ('validator_weakening', False),
        ('fake_pass', False),
        ('gate_0_v56_pass', True),
        ('gate_1_v57_validators_pass', True),
    ):
        if m.get(k) != v: fail(f'[5] rollup marker {k} != {v} (got {m.get(k)})')
    if m.get('tracks') != ['A','B','C','D','E','F']:
        fail(f'[5] rollup tracks mismatch (got {m.get("tracks")})')
    expected_tuples = [
        'PROJECT-BOSS-VISUAL-PREVIEW-ROUTE-CONTRACT',
        'PROJECT-BOSS-VISUAL-PREVIEW-SCREEN',
        'PROJECT-GENERIC-ROUTER-BOSS-DETAIL',
        'PROJECT-BOSS-VISUAL-PREVIEW-ROUTE-SMOKE-MATRIX',
        'PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT-v2',
        'MEGA-RELEASE-ACCELERATION-6-v57-ROLLUP',
    ]
    if m.get('suite_tuples') != expected_tuples:
        fail(f'[5] rollup suite_tuples mismatch')
    md5_block = m.get('md5_invariants') or {}
    for rel, expected in MD5_INVARIANTS.items():
        if md5_block.get(rel) != expected:
            fail(f'[5] rollup md5_invariants {rel} != {expected} (got {md5_block.get(rel)})')
    tt = m.get('boss_state_transition') or {}
    if tt.get('from') != 'design_only_runtime_deferred' or tt.get('to') != 'preview_shell_v57':
        fail('[5] rollup boss_state_transition mismatch')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] MEGA_RELEASE_ACCELERATION_6_v57_ROLLUP validator')
    sys.exit(1)
print('[PASS] MEGA_RELEASE_ACCELERATION_6_v57_ROLLUP validator')
sys.exit(0)
