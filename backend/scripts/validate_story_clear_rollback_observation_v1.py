#!/usr/bin/env python3
"""v67 Track E — Story Clear Rollback + Observation Simulation validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
RB=os.path.join(ROOT,'data/design/story/story_clear_rollback_simulation_result_v1.json')
OB=os.path.join(ROOT,'data/design/story/story_clear_observation_window_simulation_result_v1.json')
MK=os.path.join(ROOT,'data/design/story/story_clear_rollback_observation_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/403_STORY_CLEAR_ROLLBACK_OBSERVATION_SIMULATION.md')
F=[]
def f(m): F.append(m)
for p in (RB,OB,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(RB):
    d=json.load(open(RB))
    for k,v in (('rollback_execution_real',False),('rollback_preview_only',True),
                ('progress_rollback_preview_created',True),
                ('reward_rollback_preview_created',True),
                ('reward_reversal_executed',False),
                ('inventory_mutation',False),('db_writes',0)):
        if d.get(k)!=v: f(f'rollback {k}!={v}')
    steps=d.get('simulated_rollback_steps_executed') or []
    if len(steps)<3: f('rollback steps too few')
if os.path.exists(OB):
    o=json.load(open(OB))
    if o.get('simulated_window_minutes')!=30: f('observation window!=30')
    if (o.get('metrics_count') or 0) < 8: f('observation metrics_count<8')
    m=o.get('observation_metrics_simulated') or {}
    for k in ('clear_attempts_total','clear_success_preview_total',
              'duplicate_same_payload_total','duplicate_conflict_total',
              'missing_key_reject_total','hash_mismatch_reject_total',
              'reward_grant_total','permanent_progress_write_total',
              'db_write_total','error_total'):
        if k not in m: f(f'observation metric missing {k}')
    if m.get('reward_grant_total')!=0: f('observation reward_grant_total!=0')
    if m.get('permanent_progress_write_total')!=0: f('observation permanent_progress_write_total!=0')
    if m.get('db_write_total')!=0: f('observation db_write_total!=0')
    crit=o.get('simulated_critical_count')
    if crit is None: f('observation simulated_critical_count missing')
    if crit==0 and o.get('go_signal') is not True:
        f('observation go_signal must be true when critical=0')
    if isinstance(crit,int) and crit>0 and o.get('go_signal') is True:
        f('observation go_signal must be false when critical>0')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-STORY-CLEAR-ROLLBACK-OBSERVATION'); sys.exit(1)
print('[PASS] PROJECT-STORY-CLEAR-ROLLBACK-OBSERVATION'); sys.exit(0)
