#!/usr/bin/env python3
"""Validator: PROJECT-EPHEMERAL-TEST-DB-PRE-FLIGHT-MATRIX (v49 Track B)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/economy_safety/ephemeral_test_db_live_simulation_pre_flight_matrix_v1.json')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/ephemeral_test_db_live_simulation_pre_flight_matrix_marker_v1.json')
EXPECTED = ['gem_socket_commit','material_raid_claim','gear_forge_fusion_commit','rune_scroll_talisman_commit','artifact_upgrade_commit','divine_weapon_upgrade_commit','battle_pass_reward_claim','mail_reward_claim']

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    for k, v in (
        ('contract_version', 'ephemeral_test_db_live_simulation_pre_flight_matrix_v1'),
        ('dry_run_only', True),
        ('real_db_connection_allowed', False),
        ('mongo_url_allowed', False),
        ('pymongo_allowed', False),
        ('motor_allowed', False),
        ('env_read_allowed', False),
        ('filesystem_writes_allowed', False),
        ('production_db_touched', False),
        ('ephemeral_db_required', True),
        ('rollback_simulation_required', True),
        ('live_enabled', False),
        ('safe_to_enable_live', False),
        ('db_writes', 0),
        ('real_db_writes', 0),
    ):
        if d.get(k) != v: fail(f'design {k} != {v} (got {d.get(k)})')
    fams = d.get('operation_families') or []
    if len(fams) != 8: fail(f'design must list 8 families, got {len(fams)}')
    names = [f.get('operation_family') for f in fams]
    for n in EXPECTED:
        if n not in names: fail(f'design missing family: {n}')
    for f in fams:
        fn = f.get('operation_family')
        for k, v in (
            ('real_db_connection_allowed', False),
            ('mongo_url_allowed', False),
            ('production_db_touched', False),
            ('ephemeral_db_required', True),
            ('rollback_simulation_required', True),
            ('live_enabled', False),
            ('safe_to_enable_live', False),
            ('real_db_writes', 0),
        ):
            if f.get(k) != v: fail(f'{fn}: {k} != {v} (got {f.get(k)})')
        cols = f.get('required_collections') or []
        if 'idempotency_ledger' not in cols: fail(f'{fn}: missing idempotency_ledger in required_collections')
        if 'audit_log' not in cols: fail(f'{fn}: missing audit_log in required_collections')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('operation_families_count', 8),
        ('real_db_connection_allowed', False),
        ('mongo_url_allowed', False),
        ('production_db_touched', False),
        ('ephemeral_db_required', True),
        ('rollback_simulation_required', True),
        ('live_enabled', False),
        ('safe_to_enable_live', False),
        ('db_writes', 0),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v49_MEGA_ECONOMY_SAFETY_ACCELERATION_13'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-EPHEMERAL-TEST-DB-PRE-FLIGHT-MATRIX validator')
    sys.exit(1)
print('[PASS] PROJECT-EPHEMERAL-TEST-DB-PRE-FLIGHT-MATRIX validator')
sys.exit(0)
