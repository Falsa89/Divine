#!/usr/bin/env python3
"""v64 Track F — Staging Dry-Run + Canary QA Matrix + Progress v9 validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
M=os.path.join(ROOT,'data/design/qa/material_raid_staging_dry_run_canary_simulation_qa_matrix_v1.json')
R=os.path.join(ROOT,'data/design/release_acceleration/material_raid_claim_safety_progress_report_v9.json')
MK=os.path.join(ROOT,'data/design/qa/material_raid_staging_dry_run_canary_qa_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/384_MATERIAL_RAID_STAGING_DRY_RUN_CANARY_QA.md')
F=[]
def f(m): F.append(m)
for p in (M,R,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(M):
    d=json.load(open(M))
    ch=d.get('checks') or []
    if len(ch)<15: f('qa matrix has too few checks')
    sev=d.get('severity_summary') or {}
    if (sev.get('P0') or 0) < 10: f('qa matrix has too few P0 checks')
    must_names={'simulator_script_exists','simulator_imports_no_db_libraries',
                'scenario_fixture_exists','all_scenarios_covered','replay_result_exists',
                'ledger_dry_run_output_exists','rollback_simulation_exists',
                'observation_result_exists','v65_readiness_report_exists',
                'no_backend_route_change','no_server_py_change','no_battle_engine_change',
                'no_db_write','no_reward_grant','no_live_claim','no_claim_button',
                'no_frontend_tsx_touched','md5_invariants_intact'}
    got_names={c.get('name') for c in ch}
    miss=must_names - got_names
    if miss: f(f'qa matrix missing checks: {sorted(miss)}')
    if d.get('db_writes')!=0: f('qa matrix db_writes!=0')
if os.path.exists(R):
    r=json.load(open(R))
    for k,v in (('material_raid_claim_safety','blueprint_ready_v63'),
                ('material_raid_staging_dry_run','simulated_ready_v64'),
                ('material_raid_canary_simulation','simulated_ready_v64'),
                ('material_raid_live_claim',False),
                ('material_raid_reward_grant',False),
                ('material_raid_db_writes',0),
                ('v65_readiness','READY_FOR_MANUAL_REVIEW_NOT_APPROVED')):
        if r.get(k)!=v: f(f'progress v9 {k}!={v} (got {r.get(k)})')
    nx=r.get('next_recommended') or []
    if 'material_raid_first_controlled_live_staging_claim_v65' not in nx:
        f('progress v9 missing v65 next_recommended')
    na=r.get('not_approved') or []
    for n in ('live_claim','reward_grant','db_writes','backend_route_enablement',
              'inventory_mutation','premium_currency_mutation','battle_engine_runtime'):
        if n not in na: f(f'progress v9 not_approved missing {n}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-MATERIAL-RAID-STAGING-DRY-RUN-CANARY-QA'); sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-STAGING-DRY-RUN-CANARY-QA'); sys.exit(0)
