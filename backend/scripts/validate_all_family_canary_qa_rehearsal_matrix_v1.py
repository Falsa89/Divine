#!/usr/bin/env python3
"""Validator: PROJECT-ALL-FAMILY-CANARY-QA-REHEARSAL-MATRIX (v45 Track C).

Verifies:
- design JSON exists with all 8 operation families
- signoff_state=pending, canary/live/mutation/reward all disabled, db_writes=0
- live_flip_allowed=false; kill_switch_test_plan present per family
- rehearsal_scenarios list contains the 9 required scenario names
"""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/economy_safety/all_family_canary_qa_rehearsal_matrix_v1.json')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/all_family_canary_qa_rehearsal_matrix_marker_v1.json')

EXPECTED_FAMILIES = [
    'gem_socket_commit', 'material_raid_claim', 'gear_forge_fusion_commit',
    'rune_scroll_talisman_commit', 'artifact_upgrade_commit', 'divine_weapon_upgrade_commit',
    'battle_pass_reward_claim', 'mail_reward_claim',
]
REQUIRED_SCENARIOS = {
    'happy_path_dry_run', 'duplicate_same_hash', 'duplicate_diff_hash',
    'missing_idempotency_key', 'expected_version_mismatch', 'unauthorized_user',
    'feature_flag_disabled', 'simulated_rollback_trigger', 'observability_alert_trigger_dry_run',
}

FAILS = []

def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    if d.get('contract_version') != 'all_family_canary_qa_rehearsal_matrix_v1': fail('design contract_version mismatch')
    if d.get('dry_run_only') is not True: fail('design dry_run_only != True')
    if d.get('signoff_state') != 'pending': fail('design signoff_state must be pending')
    if d.get('canary_enabled') is not False: fail('design canary_enabled must be false')
    if d.get('canary_percentage') != 0: fail('design canary_percentage must be 0')
    if d.get('live_enabled') is not False: fail('design live_enabled must be false')
    if d.get('live_flip_allowed') is not False: fail('design live_flip_allowed must be false')
    if d.get('db_writes') != 0: fail('design db_writes must be 0')
    if d.get('reward_grant_enabled') is not False: fail('design reward_grant_enabled must be false')
    if d.get('mutation_enabled') is not False: fail('design mutation_enabled must be false')
    fams = d.get('operation_families') or []
    names = [f.get('operation_family') for f in fams]
    for n in EXPECTED_FAMILIES:
        if n not in names: fail(f'design missing family: {n}')
    if len(fams) != 8: fail(f'design must list 8 families, got {len(fams)}')
    for f in fams:
        fn = f.get('operation_family')
        if f.get('signoff_state') != 'pending': fail(f'{fn}: signoff_state must be pending')
        if f.get('canary_enabled') is not False: fail(f'{fn}: canary_enabled must be false')
        if f.get('canary_percentage') != 0: fail(f'{fn}: canary_percentage must be 0')
        if f.get('live_enabled') is not False: fail(f'{fn}: live_enabled must be false')
        if f.get('db_writes') != 0: fail(f'{fn}: db_writes must be 0')
        if f.get('reward_grant_enabled') is not False: fail(f'{fn}: reward_grant_enabled must be false')
        if f.get('mutation_enabled') is not False: fail(f'{fn}: mutation_enabled must be false')
        if f.get('live_flip_allowed') is not False: fail(f'{fn}: live_flip_allowed must be false')
        if not isinstance(f.get('kill_switch_test_plan'), dict): fail(f'{fn}: kill_switch_test_plan missing')
        if not isinstance(f.get('rollback_template_execution_steps'), list) or not f.get('rollback_template_execution_steps'): fail(f'{fn}: rollback_template_execution_steps empty')
        scenarios = {s.get('name') for s in (f.get('rehearsal_scenarios') or [])}
        missing = REQUIRED_SCENARIOS - scenarios
        if missing: fail(f'{fn}: missing scenarios {sorted(missing)}')
        pf = f.get('pass_fail_criteria') or {}
        if pf.get('db_writes_must_be') != 0: fail(f'{fn}: pf db_writes_must_be != 0')
        if pf.get('live_enforcement_must_be') is not False: fail(f'{fn}: pf live_enforcement_must_be != False')
        if pf.get('preview_request_must_not_be_blocked') is not True: fail(f'{fn}: pf preview_request_must_not_be_blocked != True')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    if m.get('signoff_state') != 'pending': fail('marker signoff_state must be pending')
    if m.get('canary_enabled') is not False: fail('marker canary_enabled must be false')
    if m.get('live_enabled') is not False: fail('marker live_enabled must be false')
    if m.get('live_flip_allowed') is not False: fail('marker live_flip_allowed must be false')
    if m.get('db_writes') != 0: fail('marker db_writes must be 0')
    if m.get('public_sync_tag') != 'PUBLIC_SYNC_TAG_v45_MEGA_ECONOMY_SAFETY_ACCELERATION_9': fail('marker public_sync_tag mismatch')
    if m.get('operation_families_count') != 8: fail('marker operation_families_count != 8')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-ALL-FAMILY-CANARY-QA-REHEARSAL-MATRIX validator')
    sys.exit(1)
print('[PASS] PROJECT-ALL-FAMILY-CANARY-QA-REHEARSAL-MATRIX validator')
sys.exit(0)
