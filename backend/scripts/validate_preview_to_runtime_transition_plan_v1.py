#!/usr/bin/env python3
"""v62 Track B validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
PACK='MEGA_RELEASE_ACCELERATION_11_PREVIEW_TO_RUNTIME_RUNNER_PLAN_AND_FULL_COVERAGE_ROLLUP_SUPER_PACK_v62'
TAG='PUBLIC_SYNC_TAG_v62_MEGA_RELEASE_ACCELERATION_11_PREVIEW_TO_RUNTIME_RUNNER_PLAN'
PLAN=os.path.join(ROOT,'data/design/release_acceleration/preview_to_runtime_transition_plan_v1.json')
MARKER=os.path.join(ROOT,'data/design/release_acceleration/preview_to_runtime_transition_plan_marker_v1.json')
F=[]
def f(m): F.append(m)
if not os.path.exists(PLAN): f('missing plan')
else:
    p=json.load(open(PLAN))
    if p.get('version')!='preview_to_runtime_transition_plan_v1': f('plan.version')
    if p.get('pack')!=PACK: f('plan.pack')
    if p.get('public_sync_tag')!=TAG: f('plan.tag')
    if p.get('design_only') is not True: f('plan.design_only')
    if p.get('activation_now') is not False: f('plan.activation_now')
    seq=p.get('sequence') or []
    if len(seq)!=8: f(f'plan.sequence count!=8: {len(seq)}')
    for s in ('preview/local coverage complete','payload contract v1 approved','runtime shell skeleton approved',
              'one-mode sandbox adapter approved','one-mode backend dry-run approved','one-mode staging result approved',
              'reward/claim policy approved','canary/manual checksum approved'):
        if s not in seq: f(f'plan.sequence missing {s}')
    rec=p.get('recommended_first_runtime_candidate') or []
    for x in ('material_raid','training'):
        if x not in rec: f(f'plan.recommended_first_runtime_candidate missing {x}')
    dis=p.get('disallowed_first_runtime_candidate') or []
    for x in ('arena ranked','event currency','gacha/shop/VIP/BP'):
        if x not in dis: f(f'plan.disallowed missing {x}')
    stop=p.get('stop_conditions') or []
    for x in ('md5 invariant drift','runtime route enabled without approval','DB write detected',
              'reward grant detected','battle_engine change detected','missing rollback','missing smoke','validator weakening'):
        if x not in stop: f(f'plan.stop_conditions missing {x}')
if not os.path.exists(MARKER): f('missing marker')
else:
    mk=json.load(open(MARKER))
    if mk.get('marker_version')!='preview_to_runtime_transition_plan_marker_v1': f('marker.version')
    for k,v in (('pack',PACK),('public_sync_tag',TAG),('design_only',True),
                ('activation_now',False),('db_writes',0),
                ('validator_weakening',False),('fake_pass',False)):
        if mk.get(k)!=v: f(f'marker.{k}!={v}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-PREVIEW-TO-RUNTIME-TRANSITION-PLAN'); sys.exit(1)
print('[PASS] PROJECT-PREVIEW-TO-RUNTIME-TRANSITION-PLAN'); sys.exit(0)
