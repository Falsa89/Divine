#!/usr/bin/env python3
"""Validator: PROJECT-ROLLBACK-RUNBOOK-REHEARSAL-MATRIX (v47 Track C)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/economy_safety/rollback_runbook_rehearsal_matrix_v1.json')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/rollback_runbook_rehearsal_matrix_marker_v1.json')

EXPECTED_FAMILIES = [
    'gem_socket_commit','material_raid_claim','gear_forge_fusion_commit','rune_scroll_talisman_commit',
    'artifact_upgrade_commit','divine_weapon_upgrade_commit','battle_pass_reward_claim','mail_reward_claim',
]
REQUIRED_SCENARIOS = {
    'kill_switch_toggle_rehearsal','verify_default_503','verify_db_writes_zero',
    'capture_aggregation_snapshot','capture_alert_evaluation','capture_go_no_go_snapshot',
    'owner_notification_dry_run','rollback_blocked_if_live_ledger_absent',
}

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    if d.get('contract_version') != 'rollback_runbook_rehearsal_matrix_v1': fail('design contract_version mismatch')
    if d.get('dry_run_only') is not True: fail('design dry_run_only != True')
    if d.get('live_rollback_enabled') is not False: fail('design live_rollback_enabled != False')
    if d.get('actual_rollback_performed') is not False: fail('design actual_rollback_performed != False')
    if d.get('db_writes') != 0: fail('design db_writes != 0')
    if d.get('reward_reversal_enabled') is not False: fail('design reward_reversal_enabled != False')
    if d.get('mutation_reversal_enabled') is not False: fail('design mutation_reversal_enabled != False')
    declared = set(d.get('rehearsal_scenarios') or [])
    missing = REQUIRED_SCENARIOS - declared
    if missing: fail(f'design top-level scenarios missing: {sorted(missing)}')
    fams = d.get('operation_families') or []
    if len(fams) != 8: fail(f'design must list 8 families, got {len(fams)}')
    names = [f.get('operation_family') for f in fams]
    for n in EXPECTED_FAMILIES:
        if n not in names: fail(f'design missing family: {n}')
    for f in fams:
        fn = f.get('operation_family')
        if f.get('rollback_rehearsal_state') != 'pending': fail(f'{fn}: rollback_rehearsal_state != pending')
        if f.get('live_rollback_enabled') is not False: fail(f'{fn}: live_rollback_enabled != False')
        if f.get('actual_rollback_performed') is not False: fail(f'{fn}: actual_rollback_performed != False')
        if f.get('db_writes') != 0: fail(f'{fn}: db_writes != 0')
        if f.get('reward_reversal_enabled') is not False: fail(f'{fn}: reward_reversal_enabled != False')
        if f.get('mutation_reversal_enabled') is not False: fail(f'{fn}: mutation_reversal_enabled != False')
        steps = f.get('steps') or []
        if len(steps) != 8: fail(f'{fn}: expected 8 steps, got {len(steps)}')
        step_names = {s.get('step') for s in steps}
        missing_s = REQUIRED_SCENARIOS - step_names
        if missing_s: fail(f'{fn}: missing steps {sorted(missing_s)}')
        for s in steps:
            if s.get('db_writes') != 0: fail(f'{fn}: step {s.get("step")} db_writes != 0')
        orders = [s.get('order') for s in steps]
        if sorted(orders) != list(range(1, 9)): fail(f'{fn}: steps order not 1..8')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    if m.get('operation_families_count') != 8: fail('marker operation_families_count != 8')
    if m.get('live_rollback_enabled') is not False: fail('marker live_rollback_enabled != False')
    if m.get('actual_rollback_performed') is not False: fail('marker actual_rollback_performed != False')
    if m.get('db_writes') != 0: fail('marker db_writes != 0')
    if m.get('public_sync_tag') != 'PUBLIC_SYNC_TAG_v47_MEGA_ECONOMY_SAFETY_ACCELERATION_11': fail('marker public_sync_tag mismatch')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-ROLLBACK-RUNBOOK-REHEARSAL-MATRIX validator')
    sys.exit(1)
print('[PASS] PROJECT-ROLLBACK-RUNBOOK-REHEARSAL-MATRIX validator')
sys.exit(0)
