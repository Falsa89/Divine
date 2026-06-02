#!/usr/bin/env python3
"""Validator: PROJECT-SIGNOFF-PROMOTION-REHEARSAL-MATRIX (v46 Track B)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/economy_safety/signoff_promotion_rehearsal_matrix_v1.json')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/signoff_promotion_rehearsal_matrix_marker_v1.json')

EXPECTED_FAMILIES = [
    'gem_socket_commit','material_raid_claim','gear_forge_fusion_commit','rune_scroll_talisman_commit',
    'artifact_upgrade_commit','divine_weapon_upgrade_commit','battle_pass_reward_claim','mail_reward_claim',
]
EXPECTED_STATES = {'pending','dry_run_ready','qa_ready','canary_rehearsal_ready','live_ready_blocked'}
REQUIRED_EVIDENCE = {
    'validators_passing','suite_zero_required_fail','md5_invariants_intact','default_503_with_flag_off',
    'dry_run_smoke_passed','replay_conflict_detection_dry_run','alert_thresholds_dry_run','rollback_runbook_present',
}

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    if d.get('contract_version') != 'signoff_promotion_rehearsal_matrix_v1': fail('design contract_version mismatch')
    if d.get('dry_run_only') is not True: fail('design dry_run_only != True')
    if d.get('actual_promotion_performed') is not False: fail('design actual_promotion_performed != False')
    if d.get('canary_enabled') is not False: fail('design canary_enabled != False')
    if d.get('live_enabled') is not False: fail('design live_enabled != False')
    if d.get('live_flip_allowed') is not False: fail('design live_flip_allowed != False')
    if d.get('db_writes') != 0: fail('design db_writes != 0')
    states = set(d.get('states') or [])
    if states != EXPECTED_STATES: fail(f'design states mismatch: {states} vs {EXPECTED_STATES}')
    fams = d.get('operation_families') or []
    if len(fams) != 8: fail(f'design must list 8 families, got {len(fams)}')
    names = [f.get('operation_family') for f in fams]
    for n in EXPECTED_FAMILIES:
        if n not in names: fail(f'design missing family: {n}')
    for f in fams:
        fn = f.get('operation_family')
        if f.get('current_state') != 'pending': fail(f'{fn}: current_state != pending')
        if f.get('target_state_after_rehearsal') != 'dry_run_ready': fail(f'{fn}: target_state_after_rehearsal != dry_run_ready')
        if f.get('actual_promotion_performed') is not False: fail(f'{fn}: actual_promotion_performed != False')
        if f.get('canary_enabled') is not False: fail(f'{fn}: canary_enabled != False')
        if f.get('live_enabled') is not False: fail(f'{fn}: live_enabled != False')
        if f.get('live_flip_allowed') is not False: fail(f'{fn}: live_flip_allowed != False')
        if f.get('db_writes') != 0: fail(f'{fn}: db_writes != 0')
        if f.get('owner_signoff') != 'pending': fail(f'{fn}: owner_signoff != pending')
        if f.get('qa_signoff') != 'pending': fail(f'{fn}: qa_signoff != pending')
        if f.get('game_director_signoff') != 'pending': fail(f'{fn}: game_director_signoff != pending')
        evid = set((f.get('evidence_checklist') or {}).keys())
        missing = REQUIRED_EVIDENCE - evid
        if missing: fail(f'{fn}: missing evidence_checklist keys {sorted(missing)}')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    if m.get('actual_promotion_performed') is not False: fail('marker actual_promotion_performed != False')
    if m.get('canary_enabled') is not False: fail('marker canary_enabled != False')
    if m.get('live_enabled') is not False: fail('marker live_enabled != False')
    if m.get('live_flip_allowed') is not False: fail('marker live_flip_allowed != False')
    if m.get('db_writes') != 0: fail('marker db_writes != 0')
    if m.get('public_sync_tag') != 'PUBLIC_SYNC_TAG_v46_MEGA_ECONOMY_SAFETY_ACCELERATION_10': fail('marker public_sync_tag mismatch')
    if m.get('operation_families_count') != 8: fail('marker operation_families_count != 8')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-SIGNOFF-PROMOTION-REHEARSAL-MATRIX validator')
    sys.exit(1)
print('[PASS] PROJECT-SIGNOFF-PROMOTION-REHEARSAL-MATRIX validator')
sys.exit(0)
