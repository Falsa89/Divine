#!/usr/bin/env python3
"""v64 Track A — Dry-Run Simulator validator (script integrity + result evidence).

Strict checks only target real import statements / module-level access, not
substrings inside docstrings/comments.
"""
from __future__ import annotations
import os, sys, json, re, ast

ROOT = '/app'
SIM = os.path.join(ROOT, 'backend/scripts/material_raid_claim_dry_run_simulator_v1.py')
C = os.path.join(ROOT, 'data/design/economy/material_raid_claim_dry_run_simulator_contract_v1.json')
RES = os.path.join(ROOT, 'data/design/economy/results/material_raid_claim_dry_run_simulator_result_v1.json')
MK = os.path.join(ROOT, 'data/design/economy/material_raid_claim_dry_run_simulator_marker_v1.json')
DOC = os.path.join(ROOT, 'docs/divine/379_MATERIAL_RAID_CLAIM_DRY_RUN_SIMULATOR.md')

F = []
def f(m): F.append(m)

for p in (SIM, C, RES, MK, DOC):
    if not os.path.exists(p): f(f'missing {p}')

if os.path.exists(SIM):
    src = open(SIM).read()
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        f(f'simulator syntax error: {e}')
        tree = None
    if tree is not None:
        forbidden_modules = {'pymongo', 'motor', 'redis', 'server', 'battle_engine'}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    base = a.name.split('.')[0]
                    if base in forbidden_modules:
                        f(f'simulator forbidden AST import: {a.name}')
            elif isinstance(node, ast.ImportFrom):
                base = (node.module or '').split('.')[0]
                if base in forbidden_modules:
                    f(f'simulator forbidden AST from-import: {node.module}')
    # Strip docstrings/comments before checking MONGO_URL real use.
    no_comments = re.sub(r'#[^\n]*', '', src)
    no_strings = re.sub(r'""".*?"""', '', no_comments, flags=re.DOTALL)
    no_strings = re.sub(r"'''.*?'''", '', no_strings, flags=re.DOTALL)
    if 'MONGO_URL' in no_strings:
        f('simulator reads MONGO_URL in real code')
    # Required decision labels must be present in source (substring is fine here,
    # because the simulator builds these decisions as values).
    for d in ('first_claim_would_stage',
              'duplicate_same_payload_would_return_existing',
              'duplicate_conflict_would_reject',
              'missing_idempotency_key_would_reject',
              'over_canary_cap_would_reject',
              'rollback_token_preview'):
        if d not in src:
            f(f'simulator missing decision label: {d}')

if os.path.exists(C):
    d = json.load(open(C))
    for k, v in (('design_only', True), ('dry_run_only', True),
                 ('live_apply_allowed', False), ('db_writes', 0),
                 ('real_db_writes', 0), ('mongo_url_used', False),
                 ('pymongo_used', False), ('motor_used', False),
                 ('redis_used', False), ('fake_pass', False),
                 ('validator_weakening', False)):
        if d.get(k) != v: f(f'contract {k}!={v} (got {d.get(k)})')
    inv = d.get('result_invariants') or {}
    for k, v in (('would_grant_rewards', False), ('db_writes', 0),
                 ('live_apply_allowed', False), ('collection_created', False),
                 ('indexes_created', False)):
        if inv.get(k) != v: f(f'contract result_invariants {k}!={v}')

if os.path.exists(RES):
    r = json.load(open(RES))
    if r.get('design_only') is not True: f('result design_only!=true')
    if r.get('db_writes') != 0: f('result db_writes!=0')
    if r.get('all_would_grant_rewards_false') is not True:
        f('result would_grant_rewards not all false')
    if r.get('all_match') is not True: f('result all_match!=true')
    if r.get('mongo_url_used') is not False: f('result mongo_url_used!=false')
    if r.get('pymongo_used') is not False: f('result pymongo_used!=false')
    if r.get('redis_used') is not False: f('result redis_used!=false')
    if r.get('collection_created') is not False: f('result collection_created!=false')
    if r.get('reward_grant_executed') is not False: f('result reward_grant_executed!=false')
    if (r.get('total_scenarios') or 0) < 6: f('result too few scenarios')

if F:
    for x in F: print('FAIL:', x)
    print('[FAIL] PROJECT-MATERIAL-RAID-CLAIM-DRY-RUN-SIMULATOR'); sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-CLAIM-DRY-RUN-SIMULATOR'); sys.exit(0)
