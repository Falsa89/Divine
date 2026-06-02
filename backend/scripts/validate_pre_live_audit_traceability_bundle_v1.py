#!/usr/bin/env python3
"""Validator: PROJECT-PRE-LIVE-AUDIT-TRACEABILITY-BUNDLE (v47 Track D)."""
from __future__ import annotations
import os, sys, json, hashlib

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/economy_safety/pre_live_audit_traceability_bundle_v1.json')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/pre_live_audit_traceability_bundle_marker_v1.json')

EXPECTED_FAMILIES = [
    'gem_socket_commit','material_raid_claim','gear_forge_fusion_commit','rune_scroll_talisman_commit',
    'artifact_upgrade_commit','divine_weapon_upgrade_commit','battle_pass_reward_claim','mail_reward_claim',
]
MD5_EXPECTED = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env': 'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx': '45fcc9890b6b128c37088bc33aa54caf',
}
REQUIRED_GLOBAL_BLOCKERS = {'signoff_pending', 'no_live_ledger', 'no_persistent_audit_sink', 'no_rollback_dry_run_in_staging', 'no_real_qa_canary_group', 'no_production_monitoring_sink'}

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    if d.get('contract_version') != 'pre_live_audit_traceability_bundle_v1': fail('design contract_version mismatch')
    if d.get('dry_run_only') is not True: fail('design dry_run_only != True')
    if d.get('global_go') is not False: fail('design global_go != False')
    if d.get('canary_enable_allowed') is not False: fail('design canary_enable_allowed != False')
    if d.get('live_enable_allowed') is not False: fail('design live_enable_allowed != False')
    if d.get('safe_to_continue_dry_run') is not True: fail('design safe_to_continue_dry_run != True')
    if d.get('safe_to_enable_live') is not False: fail('design safe_to_enable_live != False')
    if d.get('db_writes') != 0: fail('design db_writes != 0')
    md = d.get('md5_invariants') or {}
    for k, v in MD5_EXPECTED.items():
        if md.get(k) != v: fail(f'design md5 mismatch on {k}: got {md.get(k)} expected {v}')
    fams = d.get('families') or []
    if len(fams) != 8: fail(f'design must list 8 families, got {len(fams)}')
    names = [f.get('operation_family') for f in fams]
    for n in EXPECTED_FAMILIES:
        if n not in names: fail(f'design missing family: {n}')
    for f in fams:
        fn = f.get('operation_family')
        if not f.get('route'): fail(f'{fn}: missing route')
        if not f.get('feature_flag'): fail(f'{fn}: missing feature_flag')
        if not isinstance(f.get('validators'), list) or not f.get('validators'): fail(f'{fn}: empty validators')
        if not isinstance(f.get('markers'), list) or not f.get('markers'): fail(f'{fn}: empty markers')
        if not isinstance(f.get('docs'), list) or not f.get('docs'): fail(f'{fn}: empty docs')
        if not f.get('smoke_evidence'): fail(f'{fn}: missing smoke_evidence')
        if not isinstance(f.get('blockers'), list) or not f.get('blockers'): fail(f'{fn}: empty blockers')
        if f.get('go') is not False: fail(f'{fn}: go != False')
        if f.get('canary_enable_allowed') is not False: fail(f'{fn}: canary_enable_allowed != False')
        if f.get('live_enable_allowed') is not False: fail(f'{fn}: live_enable_allowed != False')
    blockers = set(d.get('blockers_global') or [])
    missing = REQUIRED_GLOBAL_BLOCKERS - blockers
    if missing: fail(f'design missing global blockers: {sorted(missing)}')

# Verify MD5 invariants live
for rel, expected in MD5_EXPECTED.items():
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p): fail(f'missing invariant file: {rel}'); continue
    h = hashlib.md5(open(p, 'rb').read()).hexdigest()
    if h != expected: fail(f'live MD5 mismatch: {rel} got {h}')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    if m.get('global_go') is not False: fail('marker global_go != False')
    if m.get('canary_enable_allowed') is not False: fail('marker canary_enable_allowed != False')
    if m.get('live_enable_allowed') is not False: fail('marker live_enable_allowed != False')
    if m.get('safe_to_enable_live') is not False: fail('marker safe_to_enable_live != False')
    if m.get('db_writes') != 0: fail('marker db_writes != 0')
    if m.get('operation_families_count') != 8: fail('marker operation_families_count != 8')
    if m.get('public_sync_tag') != 'PUBLIC_SYNC_TAG_v47_MEGA_ECONOMY_SAFETY_ACCELERATION_11': fail('marker public_sync_tag mismatch')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-PRE-LIVE-AUDIT-TRACEABILITY-BUNDLE validator')
    sys.exit(1)
print('[PASS] PROJECT-PRE-LIVE-AUDIT-TRACEABILITY-BUNDLE validator')
sys.exit(0)
