#!/usr/bin/env python3
"""v63 Track C — Staging DB Blueprint + Ledger Draft + Reward Boundary validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
BP=os.path.join(ROOT,'data/design/economy/material_raid_staging_db_blueprint_v1.json')
LD=os.path.join(ROOT,'data/design/economy/material_raid_claim_ledger_schema_draft_v1.json')
RB=os.path.join(ROOT,'data/design/economy/material_raid_reward_grant_boundary_contract_v1.json')
MK=os.path.join(ROOT,'data/design/economy/material_raid_staging_blueprint_ledger_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/374_MATERIAL_RAID_STAGING_DB_BLUEPRINT_AND_LEDGER_DRAFT.md')
F=[]
def f(m): F.append(m)
for p in (BP,LD,RB,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(BP):
    d=json.load(open(BP))
    for k,v in (('blueprint_only',True),('migration_created',False),
                ('migration_applied',False),('collections_created',False),
                ('indexes_created',False),('db_writes',0)):
        if d.get(k)!=v: f(f'blueprint {k}!={v} (got {d.get(k)})')
    cs=d.get('proposed_collections') or []
    for c in ('material_raid_claim_ledger_staging',
              'material_raid_claim_idempotency_keys_staging',
              'material_raid_claim_audit_events_staging'):
        if c not in cs: f(f'blueprint missing collection {c}')
if os.path.exists(LD):
    ld=json.load(open(LD))
    if ld.get('draft_only') is not True: f('ledger draft_only!=true')
    if ld.get('db_writes')!=0: f('ledger db_writes!=0')
    flds=ld.get('fields') or {}
    for needed in ('idempotency_key','user_id','server_id','material_raid_run_id',
                   'reward_table_version','payload_hash','reward_hash','status',
                   'created_at','rollback_token','compensation_state'):
        if needed not in flds: f(f'ledger missing field {needed}')
if os.path.exists(RB):
    r=json.load(open(RB))
    if r.get('reward_preview_equals_reward_grant') is not False:
        f('reward_preview must NOT equal reward_grant')
    if r.get('grant_only_after_explicit_live_approval') is not True:
        f('grant_only_after_explicit_live_approval must be true')
    if r.get('no_premium_currency_in_first_canary') is not True:
        f('no_premium_currency_in_first_canary must be true')
    if r.get('material_only_first_canary_suggested') is not True:
        f('material_only_first_canary_suggested must be true')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-MATERIAL-RAID-STAGING-BLUEPRINT-AND-LEDGER-DRAFT'); sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-STAGING-BLUEPRINT-AND-LEDGER-DRAFT'); sys.exit(0)
