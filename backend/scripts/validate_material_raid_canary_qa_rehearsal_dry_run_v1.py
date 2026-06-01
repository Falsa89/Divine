#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import json, os, sys
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
DES_REL = 'data/design/economy_safety/material_raid_canary_qa_rehearsal_dry_run_v1.json'
MARKER_REL = 'data/design/economy_safety/material_raid_canary_qa_rehearsal_dry_run_marker_v1.json'
DOC_REL = 'docs/divine/268_MATERIAL_RAID_CANARY_QA_REHEARSAL_DRY_RUN.md'
FAILURES = []
def fail(m): FAILURES.append(m)
def repo(p): return os.path.join(REPO_ROOT, p)
for rel in (DES_REL, MARKER_REL, DOC_REL):
    if not os.path.isfile(repo(rel)): fail(f'[1] missing: {rel}')
if FAILURES:
    [print('FAIL:', f) for f in FAILURES]; print('[FAIL] PROJECT-MATERIAL-RAID-CANARY-QA-REHEARSAL-DRY-RUN validator'); sys.exit(1)
d = json.load(open(repo(DES_REL)))
for k, exp in [('runtime_activation',False),('db_writes',0),('mode','DESIGN_CONTRACT_AUDIT_ONLY'),('operation_family','material_raid_claim'),('signoff_state','pending'),('canary_enabled',False),('canary_percentage',0),('live_enabled',False),('reward_grant_enabled',False),('material_grant_enabled',False),('premium_currency_use_enabled',False),('bp_delta_runtime_enabled',False)]:
    if d.get(k) != exp: fail(f'[2] design.{k} must be {exp!r}')
scenarios = d.get('rehearsal_scenarios') or []
if len(scenarios) != 7: fail(f'[2] must have 7 scenarios, got {len(scenarios)}')
ids = {s.get('id') for s in scenarios}
for needed in ('SCN_HAPPY_PATH','SCN_DUPLICATE_SAME_HASH','SCN_DUPLICATE_DIFF_HASH','SCN_VERSION_MISMATCH','SCN_UNAUTHORIZED','SCN_FLAG_DISABLED','SCN_ROLLBACK_TRIGGER'):
    if needed not in ids: fail(f'[2] missing scenario {needed}')
for s in scenarios:
    exp = s.get('expected') or {}
    if 'db_writes' in exp and exp['db_writes'] != 0: fail(f'[2] {s.get("id")} db_writes must be 0')
approvers = set(d.get('approval_required_from') or [])
for a in ('game_director','technical_producer','qa_owner','rollback_owner'):
    if a not in approvers: fail(f'[2] missing approver {a}')
if d.get('kill_switch_default_state') != 'engaged_kill': fail('[2] kill_switch_default_state must be engaged_kill')
gi = d.get('global_invariants') or {}
for k, exp in [('signoff_state_must_be_pending_in_this_pack',True),('canary_must_remain_disabled_in_this_pack',True),('live_must_remain_disabled_in_this_pack',True),('reward_grant_must_remain_disabled_in_this_pack',True),('material_grant_must_remain_disabled_in_this_pack',True),('db_writes',0)]:
    if gi.get(k) != exp: fail(f'[2] global_invariants.{k} must be {exp!r}')
m = json.load(open(repo(MARKER_REL)))
for k, exp in [('runtime_activation',False),('db_writes',0),('operation_family','material_raid_claim'),('signoff_state','pending'),('canary_enabled',False),('canary_percentage',0),('live_enabled',False),('reward_grant_enabled',False),('material_grant_enabled',False),('rehearsal_scenarios_count',7)]:
    if m.get(k) != exp: fail(f'[3] marker.{k} must be {exp!r}')
if FAILURES:
    [print('FAIL:', f) for f in FAILURES]; print('[FAIL] PROJECT-MATERIAL-RAID-CANARY-QA-REHEARSAL-DRY-RUN validator'); sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-CANARY-QA-REHEARSAL-DRY-RUN validator'); sys.exit(0)
