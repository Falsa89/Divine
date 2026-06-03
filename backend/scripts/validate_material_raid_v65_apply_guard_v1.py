#!/usr/bin/env python3
"""v65 Track B — Staging Claim Apply Guard + Allowlist Contract validator.

Also checks that the v65 runner script obeys the strict-import policy.
"""
from __future__ import annotations
import os, sys, json, re, ast
ROOT='/app'
G=os.path.join(ROOT,'data/design/economy/material_raid_v65_staging_claim_apply_guard_v1.json')
A=os.path.join(ROOT,'data/design/economy/material_raid_v65_canary_allowlist_contract_v1.json')
MK=os.path.join(ROOT,'data/design/economy/material_raid_v65_apply_guard_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/387_MATERIAL_RAID_v65_STAGING_CLAIM_APPLY_GUARD.md')
SCRIPT=os.path.join(ROOT,'backend/scripts/material_raid_first_controlled_live_staging_claim_v65.py')
F=[]
def f(m): F.append(m)
for p in (G,A,MK,DOC,SCRIPT):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(G):
    d=json.load(open(G))
    for k,v in (('canary_allowlist_required',True),('allowlist_users_max',5),
                ('allowlist_test_only',True),('reject_non_allowlisted',True),
                ('reject_missing_idempotency_key',True),
                ('reject_duplicate_conflict',True),
                ('reject_over_user_cap',True),('reject_over_total_cap',True),
                ('total_claim_cap',10),('per_user_claim_cap',1),
                ('reward_scope','material_only')):
        if d.get(k)!=v: f(f'guard {k}!={v}')
if os.path.exists(A):
    d=json.load(open(A))
    for k,v in (('canary_allowlist_required',True),('allowlist_test_only',True),
                ('allowlist_users_max',5),('per_user_claim_cap',1),
                ('total_claim_cap',10),('reward_scope','material_only'),
                ('premium_currency_allowed',False),('reject_non_allowlisted',True)):
        if d.get(k)!=v: f(f'allowlist {k}!={v}')
    ul=d.get('allowlist_users') or []
    for u in ul:
        if not u.startswith('test_user_'): f(f'allowlist non-placeholder user: {u}')
    if len(ul)>5: f('allowlist exceeds 5 users')
if os.path.exists(SCRIPT):
    src=open(SCRIPT).read()
    try:
        tree=ast.parse(src)
    except SyntaxError as e:
        f(f'script syntax error: {e}'); tree=None
    if tree is not None:
        forbidden={'pymongo','motor','redis','server','battle_engine'}
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                for a in node.names:
                    if a.name.split('.')[0] in forbidden:
                        f(f'script forbidden import: {a.name}')
            elif isinstance(node,ast.ImportFrom):
                if (node.module or '').split('.')[0] in forbidden:
                    f(f'script forbidden from-import: {node.module}')
    if '--apply' not in src: f('script missing --apply flag')
    if 'STAGING_MONGO_URL' not in src: f('script does not check STAGING_MONGO_URL')
    if 'MATERIAL_RAID_V65_STAGING_APPLY_PHRASE' not in src:
        f('script does not check approval phrase env var')
    if 'MATERIAL_RAID_V65_STAGING_APPLY_CHECKSUM' not in src:
        f('script does not check approval checksum env var')
    if '.staging_ready' not in src: f('script does not check staging marker')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-MATERIAL-RAID-v65-APPLY-GUARD'); sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-v65-APPLY-GUARD'); sys.exit(0)
