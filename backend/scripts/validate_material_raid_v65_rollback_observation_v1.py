#!/usr/bin/env python3
"""v65 Track E — Rollback Execution Plan + Observation Window Result validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
R=os.path.join(ROOT,'data/design/economy/material_raid_v65_rollback_execution_plan_v1.json')
O=os.path.join(ROOT,'data/design/economy/material_raid_v65_observation_window_result_v1.json')
MK=os.path.join(ROOT,'data/design/economy/material_raid_v65_rollback_observation_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/389_MATERIAL_RAID_v65_ROLLBACK_OBSERVATION_WINDOW.md')
F=[]
def f(m): F.append(m)
for p in (R,O,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(R):
    d=json.load(open(R))
    if d.get('rollback_token_required') is not True: f('rollback rollback_token_required!=true')
    if d.get('rollback_required_if_applied') is not True: f('rollback rollback_required_if_applied!=true')
    if d.get('no_destructive_broad_rollback') is not True: f('rollback no_destructive_broad_rollback!=true')
    steps=d.get('rollback_steps_manual') or []
    if len(steps)<3: f('rollback steps too few')
    covers=d.get('rollback_covers') or []
    needed=['ledger_rows_staging','idempotency_keys_staging','material_only_reward_staging_grants']
    for n in needed:
        if n not in covers: f(f'rollback covers missing {n}')
if os.path.exists(O):
    d=json.load(open(O))
    if d.get('observation_window_minutes')!=30: f('observation window_minutes!=30')
    met=d.get('metrics') or {}
    needed_metrics=['claim_attempts_total','claim_success_total','claim_reject_total',
                    'duplicate_same_payload_total','duplicate_conflict_total',
                    'over_cap_reject_total','reward_grant_total','db_write_total',
                    'rollback_required_total','unauthorized_user_reject_total','error_total']
    for m in needed_metrics:
        if m not in met: f(f'observation metrics missing {m}')
    crit=d.get('critical_findings_count')
    if crit is None: f('observation missing critical_findings_count')
    if crit==0 and d.get('go_signal') is not True:
        f('observation go_signal must be true when critical=0')
    if isinstance(crit,int) and crit>0 and d.get('go_signal') is True:
        f('observation go_signal must be false when critical>0')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-MATERIAL-RAID-v65-ROLLBACK-OBSERVATION'); sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-v65-ROLLBACK-OBSERVATION'); sys.exit(0)
