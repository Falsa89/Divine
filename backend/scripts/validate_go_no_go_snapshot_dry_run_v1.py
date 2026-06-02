#!/usr/bin/env python3
"""Validator: PROJECT-GO-NO-GO-SNAPSHOT-DRY-RUN (v46 Track C)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/economy_safety/go_no_go_snapshot_dry_run_v1.json')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/go_no_go_snapshot_dry_run_marker_v1.json')

EXPECTED_FAMILIES = [
    'gem_socket_commit','material_raid_claim','gear_forge_fusion_commit','rune_scroll_talisman_commit',
    'artifact_upgrade_commit','divine_weapon_upgrade_commit','battle_pass_reward_claim','mail_reward_claim',
]
REQUIRED_BLOCKERS = {
    'signoff_pending','no_live_ledger','no_persistent_audit_sink',
    'no_rollback_dry_run_in_staging','no_real_qa_canary_group','no_production_monitoring_sink',
}

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    if d.get('contract_version') != 'go_no_go_snapshot_dry_run_v1': fail('design contract_version mismatch')
    if d.get('generated_for_pack') != 'MEGA_ECONOMY_SAFETY_ACCELERATION_10_TELEMETRY_ALERTING_THRESHOLDS_AND_SIGNOFF_PROMOTION_REHEARSAL_PACK_v46': fail('design generated_for_pack mismatch')
    if d.get('global_go') is not False: fail('design global_go != False')
    if d.get('canary_go') is not False: fail('design canary_go != False')
    if d.get('live_go') is not False: fail('design live_go != False')
    if d.get('per_family_go') is not False: fail('design per_family_go != False')
    if d.get('safe_to_continue_dry_run') is not True: fail('design safe_to_continue_dry_run != True')
    if d.get('safe_to_enable_live') is not False: fail('design safe_to_enable_live != False')
    if d.get('db_writes') != 0: fail('design db_writes != 0')
    if d.get('live_apply_allowed') is not False: fail('design live_apply_allowed != False')
    if d.get('reason') != 'signoff_pending_and_live_disabled': fail('design reason mismatch')
    fams = d.get('operation_families') or []
    if len(fams) != 8: fail(f'design must list 8 families, got {len(fams)}')
    names = [f.get('operation_family') for f in fams]
    for n in EXPECTED_FAMILIES:
        if n not in names: fail(f'design missing family: {n}')
    for f in fams:
        fn = f.get('operation_family')
        if f.get('go') is not False: fail(f'{fn}: go != False')
        if f.get('canary_go') is not False: fail(f'{fn}: canary_go != False')
        if f.get('live_go') is not False: fail(f'{fn}: live_go != False')
        if f.get('db_writes') != 0: fail(f'{fn}: db_writes != 0')
        if f.get('live_apply_allowed') is not False: fail(f'{fn}: live_apply_allowed != False')
        if f.get('reason') != 'signoff_pending_and_live_disabled': fail(f'{fn}: reason mismatch')
    blockers = set(d.get('blockers') or [])
    missing = REQUIRED_BLOCKERS - blockers
    if missing: fail(f'design missing blockers: {sorted(missing)}')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    if m.get('global_go') is not False: fail('marker global_go != False')
    if m.get('canary_go') is not False: fail('marker canary_go != False')
    if m.get('live_go') is not False: fail('marker live_go != False')
    if m.get('safe_to_continue_dry_run') is not True: fail('marker safe_to_continue_dry_run != True')
    if m.get('safe_to_enable_live') is not False: fail('marker safe_to_enable_live != False')
    if m.get('db_writes') != 0: fail('marker db_writes != 0')
    if m.get('live_apply_allowed') is not False: fail('marker live_apply_allowed != False')
    if m.get('public_sync_tag') != 'PUBLIC_SYNC_TAG_v46_MEGA_ECONOMY_SAFETY_ACCELERATION_10': fail('marker public_sync_tag mismatch')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-GO-NO-GO-SNAPSHOT-DRY-RUN validator')
    sys.exit(1)
print('[PASS] PROJECT-GO-NO-GO-SNAPSHOT-DRY-RUN validator')
sys.exit(0)
