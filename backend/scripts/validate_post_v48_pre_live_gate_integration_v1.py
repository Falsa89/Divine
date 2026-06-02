#!/usr/bin/env python3
"""Validator: PROJECT-POST-V48-PRE-LIVE-GATE-INTEGRATION (v49 Track D)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/economy_safety/post_v48_pre_live_gate_integration_v1.json')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/post_v48_pre_live_gate_integration_marker_v1.json')
REQUIRED_CONNECTS = {'v48_final_go_no_go_consolidation','v48_live_apply_decision_log_dry_run','v48_audit_bundle_checksum_dry_run_marker','v49_ephemeral_test_db_pre_flight_matrix','v49_live_simulation_smoke_scenarios'}
REQUIRED_TRANSITIONS = {'staging_db_provisioned_ephemeral_or_isolated','persistent_audit_sink_available','live_ledger_implemented_design_then_validated','rollback_dry_run_in_staging_passed','real_qa_canary_group_with_opt_in_users','production_monitoring_sink_configured','manual_user_approval_recorded_in_decision_log'}

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    for k, v in (
        ('contract_version', 'post_v48_pre_live_gate_integration_v1'),
        ('dry_run_only', True),
        ('v49_does_not_change_go_status', True),
        ('v49_adds_ephemeral_simulation_evidence', True),
        ('global_go', False), ('canary_go', False), ('live_go', False),
        ('safe_to_continue_dry_run', True),
        ('safe_to_enable_canary', False), ('safe_to_enable_live', False),
        ('live_apply_allowed', False),
        ('db_writes', 0), ('real_db_writes', 0),
        ('production_db_touched', False),
    ):
        if d.get(k) != v: fail(f'design {k} != {v} (got {d.get(k)})')
    connects = set((d.get('connects') or {}).keys())
    m1 = REQUIRED_CONNECTS - connects
    if m1: fail(f'design connects missing: {sorted(m1)}')
    for k, p in (d.get('connects') or {}).items():
        if not os.path.exists(os.path.join(ROOT, p)): fail(f'design connect ref missing: {k} -> {p}')
    transitions = set(d.get('future_transition_requirements') or [])
    m2 = REQUIRED_TRANSITIONS - transitions
    if m2: fail(f'design future_transition_requirements missing: {sorted(m2)}')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('v49_does_not_change_go_status', True),
        ('v49_adds_ephemeral_simulation_evidence', True),
        ('global_go', False), ('canary_go', False), ('live_go', False),
        ('safe_to_continue_dry_run', True),
        ('safe_to_enable_canary', False), ('safe_to_enable_live', False),
        ('live_apply_allowed', False),
        ('db_writes', 0),
        ('production_db_touched', False),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v49_MEGA_ECONOMY_SAFETY_ACCELERATION_13'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-POST-V48-PRE-LIVE-GATE-INTEGRATION validator')
    sys.exit(1)
print('[PASS] PROJECT-POST-V48-PRE-LIVE-GATE-INTEGRATION validator')
sys.exit(0)
