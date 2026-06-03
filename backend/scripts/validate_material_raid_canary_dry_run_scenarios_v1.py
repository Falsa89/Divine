#!/usr/bin/env python3
"""v64 Track B — Canary Fixture + Scenario Matrix validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
FX=os.path.join(ROOT,'data/design/economy/material_raid_claim_canary_dry_run_fixture_v1.json')
SC=os.path.join(ROOT,'data/design/economy/material_raid_claim_dry_run_scenario_matrix_v1.json')
MK=os.path.join(ROOT,'data/design/economy/material_raid_canary_dry_run_scenarios_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/380_MATERIAL_RAID_CANARY_DRY_RUN_SCENARIOS.md')
F=[]
def f(m): F.append(m)
for p in (FX,SC,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(FX):
    d=json.load(open(FX))
    lim=d.get('limits') or {}
    if lim.get('max_users_first_wave')!=5: f('fixture max_users_first_wave!=5')
    if lim.get('max_total_claims_first_wave')!=10: f('fixture max_total!=10')
    if lim.get('max_claims_per_user')!=1: f('fixture max_claims_per_user!=1')
    if lim.get('premium_currency_allowed') is not False: f('fixture premium_currency_allowed!=false')
    if lim.get('material_only') is not True: f('fixture material_only!=true')
    ul=d.get('users_allowlist_fictional') or []
    if len(ul) < 5: f('fixture allowlist too small')
    for u in ul:
        if not u.startswith('test_user_'): f(f'fixture non-placeholder user {u}')
    if d.get('db_writes')!=0: f('fixture db_writes!=0')
if os.path.exists(SC):
    s=json.load(open(SC))
    cats=s.get('scenarios_descriptive_categories') or []
    for needed in ('first valid claim','duplicate same payload','duplicate conflicting payload',
                   'missing idempotency key','over per-user cap','over total canary cap',
                   'reward hash mismatch','rollback token preview',
                   'observation threshold warning','observation threshold critical'):
        if needed not in cats: f(f'scenario_matrix missing category: {needed}')
    scs=s.get('scenarios') or []
    if len(scs)<6: f('scenario matrix has too few executable scenarios')
    needed_decisions={'first_claim_would_stage','duplicate_same_payload_would_return_existing',
                      'duplicate_conflict_would_reject','missing_idempotency_key_would_reject',
                      'over_canary_cap_would_reject'}
    got_decisions={x.get('expected_decision') for x in scs}
    miss=needed_decisions - got_decisions
    if miss: f(f'scenario matrix missing decisions: {sorted(miss)}')
    if s.get('db_writes')!=0: f('scenario matrix db_writes!=0')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-MATERIAL-RAID-CANARY-DRY-RUN-SCENARIOS'); sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-CANARY-DRY-RUN-SCENARIOS'); sys.exit(0)
