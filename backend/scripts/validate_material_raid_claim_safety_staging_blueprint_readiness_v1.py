#!/usr/bin/env python3
"""v63 Track F — QA Readiness Matrix + Progress Report v8 validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
M=os.path.join(ROOT,'data/design/qa/material_raid_claim_safety_and_staging_blueprint_readiness_matrix_v1.json')
R=os.path.join(ROOT,'data/design/release_acceleration/material_raid_claim_safety_progress_report_v8.json')
MK=os.path.join(ROOT,'data/design/qa/material_raid_claim_safety_and_staging_blueprint_readiness_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/377_MATERIAL_RAID_CLAIM_SAFETY_STAGING_BLUEPRINT_QA.md')
F=[]
def f(m): F.append(m)
for p in (M,R,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(M):
    m=json.load(open(M))
    if m.get('db_writes')!=0: f('matrix db_writes!=0')
    ts=m.get('tracks_status') or {}
    for t in ('A_preview_contract','B_idempotency_replay','C_staging_blueprint_ledger',
              'D_rollback_approval_canary','E_dry_run_contract','F_qa_readiness',
              'G_docs_markers_validators_suite'):
        if ts.get(t)!='pass': f(f'matrix track {t}!=pass')
    nx=m.get('next_recommended') or []
    if 'material_raid_staging_dry_run_and_canary_simulation_v64' not in nx:
        f('matrix next_recommended missing v64')
    if 'material_raid_first_controlled_live_staging_claim_v65' not in nx:
        f('matrix next_recommended missing v65')
if os.path.exists(R):
    r=json.load(open(R))
    for k,v in (('visual_preview_local_layer','complete'),
                ('runtime_runner_plan','design_only_v1'),
                ('material_raid_claim_safety','blueprint_ready_v63'),
                ('material_raid_staging_blueprint','design_only_v1'),
                ('material_raid_live_claim',False),
                ('material_raid_reward_grant',False),
                ('material_raid_db_writes',0)):
        if r.get(k)!=v: f(f'progress {k}!={v} (got {r.get(k)})')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-MATERIAL-RAID-CLAIM-SAFETY-STAGING-BLUEPRINT-READINESS'); sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-CLAIM-SAFETY-STAGING-BLUEPRINT-READINESS'); sys.exit(0)
