#!/usr/bin/env python3
"""v64 Track D — Rollback Simulation + Observation Window Result validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
RB=os.path.join(ROOT,'data/design/economy/material_raid_claim_rollback_simulation_result_v1.json')
OB=os.path.join(ROOT,'data/design/economy/material_raid_claim_observation_window_simulation_result_v1.json')
MK=os.path.join(ROOT,'data/design/economy/material_raid_rollback_observation_simulation_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/382_MATERIAL_RAID_ROLLBACK_OBSERVATION_SIMULATION.md')
F=[]
def f(m): F.append(m)
for p in (RB,OB,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(RB):
    d=json.load(open(RB))
    for k,v in (('rollback_execution_real',False),('rollback_preview_only',True),
                ('rollback_token_preview_created',True),
                ('compensation_preview_created',True),
                ('reward_reversal_executed',False),
                ('inventory_mutation',False),('db_writes',0)):
        if d.get(k)!=v: f(f'rollback {k}!={v}')
    steps=d.get('simulated_rollback_steps_executed') or []
    if len(steps)<3: f('rollback steps too few')
if os.path.exists(OB):
    o=json.load(open(OB))
    if o.get('simulated_window_minutes')!=30: f('observation window_minutes!=30')
    if (o.get('metrics_count') or 0) < 9: f('observation metrics_count<9')
    th=o.get('thresholds_applied') or {}
    for k in ('duplicate_conflict_rate_warn_pct','duplicate_conflict_rate_crit_pct',
              'error_rate_warn_pct','error_rate_crit_pct',
              'latency_p95_warn_ms','latency_p95_crit_ms'):
        if k not in th: f(f'observation threshold missing {k}')
    crit=o.get('simulated_critical_count')
    if crit is None: f('observation simulated_critical_count missing')
    if crit==0 and o.get('go_signal') is not True: f('observation go_signal must be true when critical=0')
    if isinstance(crit,int) and crit>0 and o.get('go_signal') is True:
        f('observation go_signal must be false when critical>0')
    if o.get('db_writes')!=0: f('observation db_writes!=0')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-MATERIAL-RAID-ROLLBACK-OBSERVATION-SIMULATION'); sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-ROLLBACK-OBSERVATION-SIMULATION'); sys.exit(0)
