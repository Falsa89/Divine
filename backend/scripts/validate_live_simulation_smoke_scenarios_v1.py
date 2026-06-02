#!/usr/bin/env python3
"""Validator: PROJECT-LIVE-SIMULATION-SMOKE-SCENARIOS (v49 Track C)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/economy_safety/live_simulation_smoke_scenarios_v1.json')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/live_simulation_smoke_scenarios_marker_v1.json')
EXPECTED = ['gem_socket_commit','material_raid_claim','gear_forge_fusion_commit','rune_scroll_talisman_commit','artifact_upgrade_commit','divine_weapon_upgrade_commit','battle_pass_reward_claim','mail_reward_claim']
REQUIRED_SCENARIOS = {'happy_path','duplicate_same_hash','duplicate_diff_hash','missing_idempotency_key','rollback_simulation','version_mismatch','unauthorized','audit_event','no_production_db_touched'}

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    if d.get('contract_version') != 'live_simulation_smoke_scenarios_v1': fail('design contract_version mismatch')
    if d.get('dry_run_only') is not True: fail('design dry_run_only != True')
    if d.get('expected_real_db_writes') != 0: fail('design expected_real_db_writes != 0')
    if d.get('expected_live_apply_allowed') is not False: fail('design expected_live_apply_allowed != False')
    if d.get('expected_production_db_touched') is not False: fail('design expected_production_db_touched != False')
    declared = set(d.get('scenarios_required') or [])
    miss = REQUIRED_SCENARIOS - declared
    if miss: fail(f'design scenarios_required missing: {sorted(miss)}')
    fams = d.get('operation_families') or []
    if len(fams) != 8: fail(f'design must list 8 families, got {len(fams)}')
    names = [f.get('operation_family') for f in fams]
    for n in EXPECTED:
        if n not in names: fail(f'design missing family: {n}')
    for f in fams:
        fn = f.get('operation_family')
        sc = set(f.get('scenarios') or [])
        m = REQUIRED_SCENARIOS - sc
        if m: fail(f'{fn}: missing scenarios {sorted(m)}')
        if f.get('expected_real_db_writes') != 0: fail(f'{fn}: expected_real_db_writes != 0')
        if f.get('expected_live_apply_allowed') is not False: fail(f'{fn}: expected_live_apply_allowed != False')
        if f.get('expected_production_db_touched') is not False: fail(f'{fn}: expected_production_db_touched != False')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    if m.get('operation_families_count') != 8: fail('marker operation_families_count != 8')
    if m.get('scenarios_per_family') != 9: fail('marker scenarios_per_family != 9')
    if m.get('expected_real_db_writes') != 0: fail('marker expected_real_db_writes != 0')
    if m.get('expected_live_apply_allowed') is not False: fail('marker expected_live_apply_allowed != False')
    if m.get('expected_production_db_touched') is not False: fail('marker expected_production_db_touched != False')
    if m.get('public_sync_tag') != 'PUBLIC_SYNC_TAG_v49_MEGA_ECONOMY_SAFETY_ACCELERATION_13': fail('marker public_sync_tag mismatch')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-LIVE-SIMULATION-SMOKE-SCENARIOS validator')
    sys.exit(1)
print('[PASS] PROJECT-LIVE-SIMULATION-SMOKE-SCENARIOS validator')
sys.exit(0)
