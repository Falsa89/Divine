#!/usr/bin/env python3
"""v63 Track E — Dry-Run Request/Response Contract (target v64) validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
C=os.path.join(ROOT,'data/design/economy/material_raid_claim_dry_run_request_response_contract_v1.json')
O=os.path.join(ROOT,'data/design/economy/material_raid_claim_dry_run_observation_plan_v1.json')
MK=os.path.join(ROOT,'data/design/economy/material_raid_dry_run_contract_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/376_MATERIAL_RAID_DRY_RUN_REQUEST_RESPONSE_CONTRACT.md')
F=[]
def f(m): F.append(m)
for p in (C,O,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(C):
    d=json.load(open(C))
    for k,v in (('dry_run_only',True),('live_apply_allowed',False),
                ('db_writes',0),('future_v64_target',True)):
        if d.get(k)!=v: f(f'dryrun {k}!={v} (got {d.get(k)})')
    req=d.get('request_fields') or []
    for k in ('user_id','server_id','material_raid_run_id','idempotency_key',
              'reward_preview_payload','payload_hash','reward_hash','dry_run_nonce'):
        if k not in req: f(f'dryrun request_fields missing {k}')
    res=d.get('response_fields') or []
    for k in ('dry_run_status','would_create_ledger','would_grant_rewards',
              'duplicate_status','rollback_token_preview','observation_window_ref','errors'):
        if k not in res: f(f'dryrun response_fields missing {k}')
    inv=d.get('response_invariants') or {}
    if inv.get('would_grant_rewards') is not False: f('dryrun would_grant_rewards invariant must be false')
    if inv.get('no_real_ledger_write') is not True: f('dryrun no_real_ledger_write invariant must be true')
    if inv.get('no_db_writes') is not True: f('dryrun no_db_writes invariant must be true')
if os.path.exists(O):
    o=json.load(open(O))
    if o.get('future_v64_target') is not True: f('observation future_v64_target must be true')
    if o.get('db_writes')!=0: f('observation db_writes!=0')
    mets=o.get('observation_metrics') or []
    if len(mets)<5: f('observation_metrics too few')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-MATERIAL-RAID-DRY-RUN-REQUEST-RESPONSE-CONTRACT'); sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-DRY-RUN-REQUEST-RESPONSE-CONTRACT'); sys.exit(0)
