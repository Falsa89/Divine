#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import hashlib, json, os, subprocess, sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
SCRIPTS = os.path.join(REPO_ROOT,'backend','scripts')
TRACK_VALS = [
    ('TRACK-A','validate_client_idem_key_replay_detection_dry_run_v1.py'),
    ('TRACK-B','validate_observability_buffer_peek_dry_run_v1.py'),
    ('TRACK-C','validate_material_raid_canary_qa_rehearsal_dry_run_v1.py'),
]
ROLLUP_MARKER_REL = 'data/design/economy_safety/mega_economy_safety_acceleration_8_v44_rollup_marker_v1.json'
DOC_REL = 'docs/divine/269_MEGA_ECONOMY_SAFETY_ACCELERATION_8_v44.md'
SUITE_REL = 'backend/scripts/run_hero_skill_kit_validator_suite.py'
SERVER_REL = 'backend/server.py'
PRIOR_MARKERS = [
    'data/design/economy_safety/mega_economy_safety_acceleration_1_v37_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_2_v38_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_3_v39_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_4_v40_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_5_v41_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_6_v42_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_7_v43_rollup_marker_v1.json',
]
SUITE_TUPLES_V44 = [
    "'PROJECT-CLIENT-IDEM-KEY-REPLAY-DETECTION-DRY-RUN'",
    "'PROJECT-OBSERVABILITY-BUFFER-PEEK-DRY-RUN'",
    "'PROJECT-MATERIAL-RAID-CANARY-QA-REHEARSAL-DRY-RUN'",
    "'MEGA-ECONOMY-SAFETY-ACCELERATION-8-v44-ROLLUP'",
]
PUBLIC_SYNC_TAG = 'PUBLIC_SYNC_TAG_v44_MEGA_ECONOMY_SAFETY_ACCELERATION_8'
INVARIANTS = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env': 'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx': '45fcc9890b6b128c37088bc33aa54caf',
}
V42_V43_UTILS_MD5 = {
    'backend/utils/economy_request_hash_dry_run.py': '83c41e2a6ba8f73062bd8d1c60340b1b',
    'backend/utils/economy_observability_dry_run.py': '539384b1c08c02a01f07116ca92948d0',
}
FAILURES = []
def fail(m): FAILURES.append(m)
def repo(p): return os.path.join(REPO_ROOT,p)
def rt(rel): return open(repo(rel),'r',encoding='utf-8').read()
def md5(rel):
    with open(repo(rel),'rb') as f: return hashlib.md5(f.read()).hexdigest()
for lbl,n in TRACK_VALS:
    p = os.path.join(SCRIPTS,n)
    if not os.path.isfile(p): fail(f'[1][{lbl}] missing {n}'); continue
    pr = subprocess.run([sys.executable,p],capture_output=True,text=True,timeout=120)
    if pr.returncode != 0:
        tail = (pr.stdout or pr.stderr or '').strip().splitlines()
        fail(f'[1][{lbl}] FAIL: ' + ' | '.join(tail[-3:]))
for rel,exp in INVARIANTS.items():
    if not os.path.isfile(repo(rel)): fail(f'[2] missing {rel}'); continue
    g = md5(rel)
    if g != exp: fail(f'[2] MD5 mismatch {rel}: {g} != {exp}')
for rel,exp in V42_V43_UTILS_MD5.items():
    if not os.path.isfile(repo(rel)): fail(f'[2b] missing {rel}'); continue
    g = md5(rel)
    if g != exp: fail(f'[2b] util MD5 changed {rel}: {g} != {exp}')
if not os.path.isfile(repo(ROLLUP_MARKER_REL)):
    fail('[3] v44 rollup marker missing')
else:
    m = json.load(open(repo(ROLLUP_MARKER_REL)))
    for k, exp in [('runtime_activation',False),('db_writes',0),('live_apply_allowed',False),('live_commit_allowed',False),('live_claim_allowed',False),('reward_grant_enabled',False),('bp_delta_runtime_enabled',False),('redis_enabled',False),('persistent_ledger_enabled',False),('filesystem_writes_enabled',False),('preview_request_blocked',False),('all_8_operation_families_instrumented_with_client_key_replay_detection_dry_run',True),('all_8_operation_families_instrumented_with_observability_buffer_peek_dry_run',True),('existing_endpoint_paths_unchanged',True),('feature_flags_unchanged',True),('default_503_behavior_unchanged',True),('safety_flags_unchanged',True),('server_py_unchanged',True),('public_sync_tag',PUBLIC_SYNC_TAG)]:
        if m.get(k) != exp: fail(f'[3] rollup marker {k} != {exp!r}')
for rel in PRIOR_MARKERS:
    if not os.path.isfile(repo(rel)): fail(f'[4] prior marker missing {rel}')
if not os.path.isfile(repo(SUITE_REL)):
    fail('[5] suite missing')
else:
    sr = rt(SUITE_REL)
    for tup in SUITE_TUPLES_V44:
        cnt = sr.count(tup)
        if cnt != 1: fail(f'[5] suite must have exactly 1 of {tup} got {cnt}')
    if PUBLIC_SYNC_TAG not in sr: fail(f'[5] suite missing public sync tag')
if not os.path.isfile(repo(DOC_REL)): fail('[6] doc 269 missing')
sv = rt(SERVER_REL)
for needle in ('economy_client_idem_key_replay_detection_dry_run','economy_observability_buffer_peek_dry_run'):
    if needle in sv: fail(f'[7] server.py must not import {needle}')
if FAILURES:
    [print('FAIL:', f) for f in FAILURES]; print('[FAIL] MEGA_ECONOMY_SAFETY_ACCELERATION_8_v44_ROLLUP validator'); sys.exit(1)
print('[PASS] MEGA_ECONOMY_SAFETY_ACCELERATION_8_v44_ROLLUP validator'); sys.exit(0)
