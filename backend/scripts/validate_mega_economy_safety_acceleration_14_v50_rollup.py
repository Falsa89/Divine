#!/usr/bin/env python3
"""Validator: MEGA-ECONOMY-SAFETY-ACCELERATION-14-v50-ROLLUP."""
from __future__ import annotations
import os, sys, hashlib, subprocess, json

ROOT = '/app'
SUITE_RUNNER = os.path.join(ROOT, 'backend/scripts/run_hero_skill_kit_validator_suite.py')
ROLLUP_MARKER = os.path.join(ROOT, 'data/design/economy_safety/mega_economy_safety_acceleration_14_v50_rollup_marker_v1.json')

REQUIRED_TUPLES = [
    "'PROJECT-EPHEMERAL-SIMULATION-INVARIANT-REPORT-DRY-RUN'",
    "'PROJECT-STAGING-DB-BLUEPRINT-DESIGN-ONLY'",
    "'PROJECT-LIVE-LEDGER-DESIGN-ONLY'",
    "'PROJECT-MANUAL-USER-APPROVAL-HANDSHAKE-DRY-RUN'",
    "'MEGA-ECONOMY-SAFETY-ACCELERATION-14-v50-ROLLUP'",
]
PUBLIC_SYNC_TAG = 'PUBLIC_SYNC_TAG_v50_MEGA_ECONOMY_SAFETY_ACCELERATION_14'
MD5_INVARIANTS = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env': 'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx': '45fcc9890b6b128c37088bc33aa54caf',
}
DEPENDENT = [
    'validate_ephemeral_simulation_invariant_report_dry_run_v1.py',
    'validate_staging_db_blueprint_v1.py',
    'validate_live_ledger_design_only_v1.py',
    'validate_manual_user_approval_handshake_dry_run_v1.py',
]

FAILS = []
def fail(m): FAILS.append(m)

# [1] MD5 invariants — 5 core files
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

# [4] Rollup marker invariants
if not os.path.exists(ROLLUP_MARKER): fail(f'[4] missing rollup marker: {ROLLUP_MARKER}')
else:
    m = json.load(open(ROLLUP_MARKER))
    for k, v in (
        ('marker_version', 'mega_economy_safety_acceleration_14_v50_rollup_marker_v1'),
        ('pack', 'MEGA_ECONOMY_SAFETY_ACCELERATION_14_EPHEMERAL_SIMULATION_INVARIANT_REPORT_AND_STAGING_DB_BLUEPRINT_PACK_v50'),
        ('public_sync_tag', PUBLIC_SYNC_TAG),
        ('db_writes', 0),
        ('real_db_writes', 0),
        ('production_db_touched', False),
        ('mongo_url_used', False),
        ('pymongo_used', False),
        ('motor_used', False),
        ('env_read', False),
        ('filesystem_writes', 0),
        ('live_apply_allowed', False),
        ('live_enforcement_enabled', False),
        ('preview_request_blocked', False),
        ('persisted', False),
        ('server_py_changed', False),
        ('frontend_changed', False),
        ('battle_engine_changed', False),
        ('character_bible_changed', False),
        ('final_numbers_changed', False),
        ('endpoint_paths_changed', False),
        ('feature_flags_changed', False),
        ('default_503_changed', False),
        ('safety_flags_changed', False),
        ('validator_weakening', False),
        ('fake_pass', False),
    ):
        if m.get(k) != v: fail(f'[4] rollup marker {k} != {v} (got {m.get(k)})')
    if m.get('tracks') != ['A', 'B', 'C', 'D', 'E']: fail(f'[4] rollup marker tracks != [A,B,C,D,E] (got {m.get("tracks")})')
    if m.get('suite_tuples') != [
        'PROJECT-EPHEMERAL-SIMULATION-INVARIANT-REPORT-DRY-RUN',
        'PROJECT-STAGING-DB-BLUEPRINT-DESIGN-ONLY',
        'PROJECT-LIVE-LEDGER-DESIGN-ONLY',
        'PROJECT-MANUAL-USER-APPROVAL-HANDSHAKE-DRY-RUN',
        'MEGA-ECONOMY-SAFETY-ACCELERATION-14-v50-ROLLUP',
    ]:
        fail(f'[4] rollup marker suite_tuples mismatch (got {m.get("suite_tuples")})')
    md5_block = m.get('md5_invariants') or {}
    for rel, expected in MD5_INVARIANTS.items():
        if md5_block.get(rel) != expected:
            fail(f'[4] rollup marker md5_invariants {rel} != {expected} (got {md5_block.get(rel)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] MEGA_ECONOMY_SAFETY_ACCELERATION_14_v50_ROLLUP validator')
    sys.exit(1)
print('[PASS] MEGA_ECONOMY_SAFETY_ACCELERATION_14_v50_ROLLUP validator')
sys.exit(0)
