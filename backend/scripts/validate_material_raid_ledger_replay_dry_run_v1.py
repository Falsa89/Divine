#!/usr/bin/env python3
"""v64 Track C — Ledger Dry-Run Expected Output + Replay Result validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
LE=os.path.join(ROOT,'data/design/economy/material_raid_claim_ledger_dry_run_expected_output_v1.json')
RP=os.path.join(ROOT,'data/design/economy/material_raid_claim_replay_dry_run_result_v1.json')
MK=os.path.join(ROOT,'data/design/economy/material_raid_ledger_replay_dry_run_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/381_MATERIAL_RAID_LEDGER_REPLAY_DRY_RUN_EVIDENCE.md')
F=[]
def f(m): F.append(m)
for p in (LE,RP,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(LE):
    d=json.load(open(LE))
    for k,v in (('ledger_dry_run_only',True),('collection_created',False),
                ('indexes_created',False),('db_writes',0),
                ('staged_rows_are_simulated',True),
                ('reward_grant_result','not_executed'),
                ('no_premium_currency',True),('no_inventory_mutation',True),
                ('no_wallet_mutation',True)):
        if d.get(k)!=v: f(f'ledger {k}!={v}')
    flds=d.get('expected_ledger_fields') or []
    for fld in ('idempotency_key','user_id','payload_hash','reward_hash',
                'status','created_at','rollback_token','compensation_state'):
        if fld not in flds: f(f'ledger missing expected field: {fld}')
if os.path.exists(RP):
    r=json.load(open(RP))
    m=r.get('expected_scenario_status_map') or {}
    for k,v in (('first_valid_claim','staged_pending'),
                ('duplicate_same_payload','duplicate_same_payload'),
                ('duplicate_conflict','rejected'),
                ('missing_idempotency_key','rejected'),
                ('over_per_user_cap','rejected'),
                ('over_total_canary_cap','rejected')):
        if m.get(k)!=v: f(f'replay map {k}!={v}')
    for k,v in (('staged_rows_are_simulated',True),('ledger_dry_run_only',True),
                ('collection_created',False),('reward_grant_result','not_executed')):
        if r.get(k)!=v: f(f'replay {k}!={v}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-MATERIAL-RAID-LEDGER-REPLAY-DRY-RUN-EVIDENCE'); sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-LEDGER-REPLAY-DRY-RUN-EVIDENCE'); sys.exit(0)
