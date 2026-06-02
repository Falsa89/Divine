#!/usr/bin/env python3
"""Validator: PROJECT-EXPO-WATCHER-ENOSPC-DIAGNOSTIC (v48 Track D)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/economy_safety/expo_watcher_enospc_diagnostic_v1.json')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/expo_watcher_enospc_diagnostic_marker_v1.json')
REQUIRED_AFFECTED = {
    'OPS-A: audit_start_expo_wrapper_resilience.py',
    'OPS-B: audit_ops_start_expo_persistence.py',
    'OPS-C: audit_ops_start_expo_autorestore.py',
    'OPS-C-WIRING: audit_ops_start_expo_boot_wiring.py',
    'AF2-N-V26-FRONTEND-SMOKE: audit_affinity_gifts_frontend_smoke_v26.py',
    'ULTRA-COMBO-V26: validate_ultra_combo_v26_broad_readiness_plan.py',
}
REQUIRED_DO_NOT = {'do_not_weaken_validators', 'do_not_fake_PASS', 'do_not_modify_server_py', 'do_not_modify_frontend', 'do_not_modify_battle_engine', 'do_not_modify_md5_locked_files', 'do_not_skip_OPS_or_v26_in_suite_runner', 'do_not_call_sysctl_write_at_runtime'}

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    if d.get('contract_version') != 'expo_watcher_enospc_diagnostic_v1': fail('design contract_version mismatch')
    if d.get('dry_run_only') is not True: fail('design dry_run_only != True')
    if d.get('classification') != 'environmental_optional_fail_not_v47_regression': fail('design classification mismatch')
    if d.get('v47_validator_status') != 'all_v47_validators_PASS': fail('design v47_validator_status must record PASS')
    if d.get('md5_invariants_status') != '5_of_5_intact': fail('design md5_invariants_status mismatch')
    if d.get('server_py_status') != 'unchanged': fail('design server_py_status != unchanged')
    if d.get('frontend_status') != 'unchanged': fail('design frontend_status != unchanged')
    if d.get('db_writes') != 0: fail('design db_writes != 0')
    if d.get('live_apply_allowed') is not False: fail('design live_apply_allowed != False')
    aff = set(d.get('affected_validators') or [])
    miss = REQUIRED_AFFECTED - aff
    if miss: fail(f'design missing affected_validators: {sorted(miss)}')
    do_not = set(d.get('do_not') or [])
    miss_dn = REQUIRED_DO_NOT - do_not
    if miss_dn: fail(f'design missing do_not: {sorted(miss_dn)}')
    if d.get('public_sync_tag') != 'PUBLIC_SYNC_TAG_v48_MEGA_ECONOMY_SAFETY_ACCELERATION_12': fail('design public_sync_tag mismatch')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    if m.get('classification') != 'environmental_optional_fail_not_v47_regression': fail('marker classification mismatch')
    if m.get('validator_weakening') is not False: fail('marker validator_weakening != False')
    if m.get('fake_pass') is not False: fail('marker fake_pass != False')
    if m.get('db_writes') != 0: fail('marker db_writes != 0')
    if m.get('public_sync_tag') != 'PUBLIC_SYNC_TAG_v48_MEGA_ECONOMY_SAFETY_ACCELERATION_12': fail('marker public_sync_tag mismatch')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-EXPO-WATCHER-ENOSPC-DIAGNOSTIC validator')
    sys.exit(1)
print('[PASS] PROJECT-EXPO-WATCHER-ENOSPC-DIAGNOSTIC validator')
sys.exit(0)
