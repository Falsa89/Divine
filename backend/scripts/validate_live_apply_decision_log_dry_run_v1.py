#!/usr/bin/env python3
"""Validator: PROJECT-LIVE-APPLY-DECISION-LOG-DRY-RUN (v48 Track C)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/economy_safety/live_apply_decision_log_dry_run_v1.json')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/live_apply_decision_log_dry_run_marker_v1.json')
EXPECTED = ['gem_socket_commit','material_raid_claim','gear_forge_fusion_commit','rune_scroll_talisman_commit','artifact_upgrade_commit','divine_weapon_upgrade_commit','battle_pass_reward_claim','mail_reward_claim']

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    if d.get('contract_version') != 'live_apply_decision_log_dry_run_v1': fail('design contract_version mismatch')
    if d.get('dry_run_only') is not True: fail('design dry_run_only != True')
    if d.get('schema_only') is not True: fail('design schema_only != True')
    if d.get('actual_decisions_persisted') is not False: fail('design actual_decisions_persisted != False')
    if d.get('future_live_decision_requires_manual_user_approval') is not True: fail('design requires_manual_user_approval != True')
    if d.get('canary_allowed') is not False: fail('design canary_allowed != False')
    if d.get('live_allowed') is not False: fail('design live_allowed != False')
    if d.get('db_writes') != 0: fail('design db_writes != 0')
    sch = d.get('entry_schema') or {}
    if not isinstance(sch.get('required_fields'), list) or len(sch.get('required_fields')) < 7: fail('entry_schema.required_fields too short')
    if not isinstance(sch.get('decision_enum'), list) or 'no_go_signoff_pending' not in sch.get('decision_enum'): fail('decision_enum missing no_go_signoff_pending')
    if not isinstance(sch.get('approver_enum'), list) or 'system_dry_run' not in sch.get('approver_enum'): fail('approver_enum missing system_dry_run')
    entries = d.get('entries') or []
    if len(entries) != 8: fail(f'must list 8 entries, got {len(entries)}')
    names = [e.get('operation_family') for e in entries]
    for n in EXPECTED:
        if n not in names: fail(f'missing entry family: {n}')
    for e in entries:
        fn = e.get('operation_family')
        if e.get('current_decision') != 'no_go_signoff_pending': fail(f'{fn}: current_decision != no_go_signoff_pending')
        if e.get('approver') != 'system_dry_run': fail(f'{fn}: approver != system_dry_run')
        if e.get('db_writes') != 0: fail(f'{fn}: db_writes != 0')
        if e.get('live_apply_allowed') is not False: fail(f'{fn}: live_apply_allowed != False')
        if e.get('canary_allowed') is not False: fail(f'{fn}: canary_allowed != False')
        if e.get('live_allowed') is not False: fail(f'{fn}: live_allowed != False')
        if e.get('requires_manual_user_approval') is not True: fail(f'{fn}: requires_manual_user_approval != True')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    if m.get('schema_only') is not True: fail('marker schema_only != True')
    if m.get('actual_decisions_persisted') is not False: fail('marker actual_decisions_persisted != False')
    if m.get('canary_allowed') is not False: fail('marker canary_allowed != False')
    if m.get('live_allowed') is not False: fail('marker live_allowed != False')
    if m.get('db_writes') != 0: fail('marker db_writes != 0')
    if m.get('public_sync_tag') != 'PUBLIC_SYNC_TAG_v48_MEGA_ECONOMY_SAFETY_ACCELERATION_12': fail('marker public_sync_tag mismatch')
    if m.get('operation_families_count') != 8: fail('marker operation_families_count != 8')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-LIVE-APPLY-DECISION-LOG-DRY-RUN validator')
    sys.exit(1)
print('[PASS] PROJECT-LIVE-APPLY-DECISION-LOG-DRY-RUN validator')
sys.exit(0)
