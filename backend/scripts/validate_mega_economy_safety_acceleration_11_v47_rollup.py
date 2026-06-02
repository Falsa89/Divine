#!/usr/bin/env python3
"""Validator: MEGA-ECONOMY-SAFETY-ACCELERATION-11-v47-ROLLUP."""
from __future__ import annotations
import os, sys, json, hashlib, subprocess

ROOT = '/app'
SUITE_RUNNER = os.path.join(ROOT, 'backend/scripts/run_hero_skill_kit_validator_suite.py')
ROUTES = [
    'backend/routes/gem_socket_commit_safety_preview.py',
    'backend/routes/material_raid_claim_safety_preview.py',
    'backend/routes/gear_forge_fusion_safety_preview.py',
    'backend/routes/rune_scroll_talisman_safety_preview.py',
    'backend/routes/artifact_upgrade_safety_preview.py',
    'backend/routes/divine_weapon_upgrade_safety_preview.py',
    'backend/routes/battle_pass_claim_safety_preview.py',
    'backend/routes/mail_claim_safety_preview.py',
]
REQUIRED_TUPLES = [
    "'PROJECT-ALERT-HISTORY-RING-BUFFER-DRY-RUN'",
    "'PROJECT-ROLLBACK-RUNBOOK-REHEARSAL-MATRIX'",
    "'PROJECT-PRE-LIVE-AUDIT-TRACEABILITY-BUNDLE'",
    "'MEGA-ECONOMY-SAFETY-ACCELERATION-11-v47-ROLLUP'",
]
PUBLIC_SYNC_TAG = 'PUBLIC_SYNC_TAG_v47_MEGA_ECONOMY_SAFETY_ACCELERATION_11'
MD5_INVARIANTS = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env': 'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx': '45fcc9890b6b128c37088bc33aa54caf',
}
DEPENDENT = [
    'validate_alert_history_ring_buffer_dry_run_v1.py',
    'validate_rollback_runbook_rehearsal_matrix_v1.py',
    'validate_pre_live_audit_traceability_bundle_v1.py',
]

FAILS = []
def fail(m): FAILS.append(m)

# 1. MD5
for rel, expected in MD5_INVARIANTS.items():
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p): fail(f'[1] missing {rel}'); continue
    h = hashlib.md5(open(p, 'rb').read()).hexdigest()
    if h != expected: fail(f'[1] MD5 mismatch {rel}')

# 2. Suite tuples + tag
if not os.path.exists(SUITE_RUNNER): fail('[2] missing suite runner')
else:
    sr = open(SUITE_RUNNER).read()
    for t in REQUIRED_TUPLES:
        if sr.count(t) != 1: fail(f'[2] suite must have exactly 1 of {t} got {sr.count(t)}')
    if PUBLIC_SYNC_TAG not in sr: fail(f'[2] suite missing tag {PUBLIC_SYNC_TAG}')

# 3. Wire-up
for rel in ROUTES:
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p): fail(f'[3] missing route {rel}'); continue
    s = open(p).read()
    if '_V47_DRY_RUN_AVAILABLE' not in s: fail(f'[3] {rel}: missing v47 import flag')
    if '"alert_history_dry_run"' not in s: fail(f'[3] {rel}: missing /config alert_history_dry_run')
    if '"alert_history_record_dry_run"' not in s: fail(f'[3] {rel}: missing POST alert_history_record_dry_run')
    if '"alert_history_snapshot"' not in s: fail(f'[3] {rel}: missing /peek-buffer alert_history_snapshot')

# 4. Dependent validators
for v in DEPENDENT:
    vp = os.path.join(ROOT, 'backend/scripts', v)
    if not os.path.exists(vp): fail(f'[4] missing validator {v}'); continue
    r = subprocess.run([sys.executable, vp], capture_output=True, text=True)
    if r.returncode != 0:
        fail(f'[4] dependent validator {v} returned {r.returncode}')
        print(r.stdout[-500:]); print(r.stderr[-500:])

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] MEGA_ECONOMY_SAFETY_ACCELERATION_11_v47_ROLLUP validator')
    sys.exit(1)
print('[PASS] MEGA_ECONOMY_SAFETY_ACCELERATION_11_v47_ROLLUP validator')
sys.exit(0)
