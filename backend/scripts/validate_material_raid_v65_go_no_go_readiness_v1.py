#!/usr/bin/env python3
"""v64 Track E — v65 Go/No-Go Readiness Report validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
R=os.path.join(ROOT,'data/design/economy/material_raid_first_controlled_live_staging_claim_readiness_report_v1.json')
MK=os.path.join(ROOT,'data/design/economy/material_raid_v65_go_no_go_readiness_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/383_MATERIAL_RAID_v65_GO_NO_GO_READINESS.md')
F=[]
def f(m): F.append(m)
for p in (R,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(R):
    d=json.load(open(R))
    for k,v in (('target_future_pack','v65'),
                ('current_verdict','READY_FOR_MANUAL_REVIEW_NOT_APPROVED'),
                ('live_claim_approved',False),('db_writes_approved',False),
                ('reward_grant_approved',False),('manual_approval_required',True),
                ('approval_phrase_required',True),('checksum_required',True),
                ('allowlist_required',True),('db_writes',0)):
        if d.get(k)!=v: f(f'readiness {k}!={v} (got {d.get(k)})')
    req=d.get('required_before_v65') or []
    for needed in ('all_v64_validators_pass','observation_critical_findings_zero',
                   'duplicate_conflict_scenario_rejects','over_cap_scenario_rejects',
                   'rollback_preview_available','ledger_dry_run_matches_schema',
                   'md5_invariants_unchanged','explicit_user_approval_phrase'):
        if needed not in req: f(f'readiness required_before_v65 missing: {needed}')
    sc=d.get('recommended_v65_scope') or {}
    for k,v in (('material_raid_only',True),('material_only_reward',True),
                ('users','1_to_5_allowlisted'),('max_claim_per_user',1),
                ('max_total_claims',10),('premium_currency_allowed',False)):
        if sc.get(k)!=v: f(f'readiness recommended_v65_scope {k}!={v}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-MATERIAL-RAID-v65-GO-NO-GO-READINESS'); sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-v65-GO-NO-GO-READINESS'); sys.exit(0)
