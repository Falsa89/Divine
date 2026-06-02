#!/usr/bin/env python3
"""Validator: PROJECT-FINAL-GO-NO-GO-CONSOLIDATION (v48 Track B)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/economy_safety/final_go_no_go_consolidation_v1.json')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/final_go_no_go_consolidation_marker_v1.json')

EXPECTED = ['gem_socket_commit','material_raid_claim','gear_forge_fusion_commit','rune_scroll_talisman_commit','artifact_upgrade_commit','divine_weapon_upgrade_commit','battle_pass_reward_claim','mail_reward_claim']
REQUIRED_GLOBAL_BLOCKERS = {'signoff_pending', 'no_live_ledger', 'no_persistent_audit_sink', 'no_rollback_dry_run_in_staging', 'no_real_qa_canary_group', 'no_production_monitoring_sink', 'requires_staging_or_local_live_simulation_with_ephemeral_test_db'}
REQUIRED_CONSOLIDATES = {'v46_go_no_go_snapshot', 'v46_signoff_promotion_rehearsal_matrix', 'v47_pre_live_audit_traceability_bundle', 'v47_rollback_runbook_rehearsal_matrix', 'v45_all_family_canary_qa_rehearsal_matrix'}

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    if d.get('contract_version') != 'final_go_no_go_consolidation_v1': fail('design contract_version mismatch')
    if d.get('dry_run_only') is not True: fail('design dry_run_only != True')
    if d.get('global_go') is not False: fail('design global_go != False')
    if d.get('canary_go') is not False: fail('design canary_go != False')
    if d.get('live_go') is not False: fail('design live_go != False')
    if d.get('safe_to_continue_dry_run') is not True: fail('design safe_to_continue_dry_run != True')
    if d.get('safe_to_enable_canary') is not False: fail('design safe_to_enable_canary != False')
    if d.get('safe_to_enable_live') is not False: fail('design safe_to_enable_live != False')
    if d.get('live_apply_allowed') is not False: fail('design live_apply_allowed != False')
    if d.get('db_writes') != 0: fail('design db_writes != 0')
    if d.get('next_required_phase') != 'staging_or_local_live_simulation_with_ephemeral_test_db': fail('design next_required_phase mismatch')
    consolidates = set((d.get('consolidates') or {}).keys())
    missing = REQUIRED_CONSOLIDATES - consolidates
    if missing: fail(f'design consolidates missing: {sorted(missing)}')
    # Verify the referenced files exist
    for k, p in (d.get('consolidates') or {}).items():
        if not os.path.exists(os.path.join(ROOT, p)): fail(f'design consolidate ref missing: {k} -> {p}')
    fams = d.get('operation_families') or []
    if len(fams) != 8: fail(f'design must list 8 families, got {len(fams)}')
    names = [f.get('operation_family') for f in fams]
    for n in EXPECTED:
        if n not in names: fail(f'design missing family {n}')
    for f in fams:
        fn = f.get('operation_family')
        if f.get('go') is not False: fail(f'{fn}: go != False')
        if f.get('canary_go') is not False: fail(f'{fn}: canary_go != False')
        if f.get('live_go') is not False: fail(f'{fn}: live_go != False')
        if f.get('safe_to_enable_canary') is not False: fail(f'{fn}: safe_to_enable_canary != False')
        if f.get('safe_to_enable_live') is not False: fail(f'{fn}: safe_to_enable_live != False')
        if f.get('db_writes') != 0: fail(f'{fn}: db_writes != 0')
        if f.get('signoff_state') != 'pending': fail(f'{fn}: signoff_state != pending')
        if f.get('rollback_rehearsal_state') != 'pending': fail(f'{fn}: rollback_rehearsal_state != pending')
        if not isinstance(f.get('reasons'), list) or not f.get('reasons'): fail(f'{fn}: reasons empty')
    blockers = set(d.get('global_blockers') or [])
    miss = REQUIRED_GLOBAL_BLOCKERS - blockers
    if miss: fail(f'design missing global_blockers: {sorted(miss)}')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    if m.get('global_go') is not False: fail('marker global_go != False')
    if m.get('safe_to_enable_live') is not False: fail('marker safe_to_enable_live != False')
    if m.get('db_writes') != 0: fail('marker db_writes != 0')
    if m.get('public_sync_tag') != 'PUBLIC_SYNC_TAG_v48_MEGA_ECONOMY_SAFETY_ACCELERATION_12': fail('marker public_sync_tag mismatch')
    if m.get('operation_families_count') != 8: fail('marker operation_families_count != 8')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-FINAL-GO-NO-GO-CONSOLIDATION validator')
    sys.exit(1)
print('[PASS] PROJECT-FINAL-GO-NO-GO-CONSOLIDATION validator')
sys.exit(0)
