#!/usr/bin/env python3
"""Validator: MEGA-ECONOMY-SAFETY-ACCELERATION-13-v49-ROLLUP."""
from __future__ import annotations
import os, sys, hashlib, subprocess

ROOT = '/app'
SUITE_RUNNER = os.path.join(ROOT, 'backend/scripts/run_hero_skill_kit_validator_suite.py')
REQUIRED_TUPLES = [
    "'PROJECT-EPHEMERAL-TEST-DB-LIVE-SIMULATION-DRY-RUN'",
    "'PROJECT-EPHEMERAL-TEST-DB-PRE-FLIGHT-MATRIX'",
    "'PROJECT-LIVE-SIMULATION-SMOKE-SCENARIOS'",
    "'PROJECT-POST-V48-PRE-LIVE-GATE-INTEGRATION'",
    "'MEGA-ECONOMY-SAFETY-ACCELERATION-13-v49-ROLLUP'",
]
PUBLIC_SYNC_TAG = 'PUBLIC_SYNC_TAG_v49_MEGA_ECONOMY_SAFETY_ACCELERATION_13'
MD5_INVARIANTS = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env': 'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx': '45fcc9890b6b128c37088bc33aa54caf',
}
DEPENDENT = [
    'validate_ephemeral_test_db_live_simulation_dry_run_v1.py',
    'validate_ephemeral_test_db_pre_flight_matrix_v1.py',
    'validate_live_simulation_smoke_scenarios_v1.py',
    'validate_post_v48_pre_live_gate_integration_v1.py',
]

FAILS = []
def fail(m): FAILS.append(m)

for rel, expected in MD5_INVARIANTS.items():
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p): fail(f'[1] missing {rel}'); continue
    h = hashlib.md5(open(p, 'rb').read()).hexdigest()
    if h != expected: fail(f'[1] MD5 mismatch {rel}: got {h}')

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

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] MEGA_ECONOMY_SAFETY_ACCELERATION_13_v49_ROLLUP validator')
    sys.exit(1)
print('[PASS] MEGA_ECONOMY_SAFETY_ACCELERATION_13_v49_ROLLUP validator')
sys.exit(0)
