#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator Rollup v43: MEGA-ECONOMY-SAFETY-ACCELERATION-7-v43-ROLLUP
Pack: MEGA_ECONOMY_SAFETY_ACCELERATION_7_DRY_RUN_REPLAY_DETECTION_PACK_v43

Esegue back-to-back il validator Track A, e asserisce invarianti globali:
  - 5 file core MD5-locked invariati
  - 2 tuple v43 nel suite runner (count = 1 ciascuna)
  - rollup marker v43 presente e coerente
  - public_sync_tag PUBLIC_SYNC_TAG_v43_MEGA_ECONOMY_SAFETY_ACCELERATION_7 presente
  - server.py non modificato per v43
  - tutti i marker v37-v42 + v42b/v42c ancora presenti
  - v42 utils non modificati
"""
from __future__ import annotations
import hashlib
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SCRIPTS_DIR = os.path.join(REPO_ROOT, 'backend', 'scripts')

TRACK_VALIDATORS = [
    ('TRACK-A', 'validate_economy_idempotency_replay_detection_dry_run_v1.py'),
]

ROLLUP_MARKER_REL = 'data/design/economy_safety/mega_economy_safety_acceleration_7_v43_rollup_marker_v1.json'
DOC_REL = 'docs/divine/265_MEGA_ECONOMY_SAFETY_ACCELERATION_7_v43.md'
SUITE_REL = 'backend/scripts/run_hero_skill_kit_validator_suite.py'
SERVER_REL = 'backend/server.py'

PRIOR_MARKERS_REL = [
    'data/design/economy_safety/mega_economy_safety_acceleration_1_v37_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_2_v38_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_3_v39_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_4_v40_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_5_v41_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_6_v42_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_6_public_route_wireup_repair_v42b_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_6_observability_param_repair_v42c_marker_v1.json',
]

V42_UTILS_REL = [
    'backend/utils/economy_request_hash_dry_run.py',
    'backend/utils/economy_observability_dry_run.py',
]

SUITE_TUPLES_V43 = [
    "'PROJECT-ECONOMY-IDEMPOTENCY-REPLAY-DETECTION-DRY-RUN'",
    "'MEGA-ECONOMY-SAFETY-ACCELERATION-7-v43-ROLLUP'",
]

PUBLIC_SYNC_TAG = 'PUBLIC_SYNC_TAG_v43_MEGA_ECONOMY_SAFETY_ACCELERATION_7'

INVARIANTS = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env': 'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx': '45fcc9890b6b128c37088bc33aa54caf',
}

# v42 utils MD5: captured at v42 time, must remain bit-identical in v43.
V42_UTILS_MD5 = {
    'backend/utils/economy_request_hash_dry_run.py': '83c41e2a6ba8f73062bd8d1c60340b1b',
    'backend/utils/economy_observability_dry_run.py': '539384b1c08c02a01f07116ca92948d0',
}

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def repo(p: str) -> str:
    return os.path.join(REPO_ROOT, p)


def read_text(rel: str) -> str:
    return open(repo(rel), 'r', encoding='utf-8').read()


def load_json(rel: str):
    return json.load(open(repo(rel), 'r', encoding='utf-8'))


def md5_of(rel: str) -> str:
    with open(repo(rel), 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


# [1] sub-validators
for label, name in TRACK_VALIDATORS:
    path = os.path.join(SCRIPTS_DIR, name)
    if not os.path.isfile(path):
        fail(f'[1][{label}] validator missing: {name}')
        continue
    proc = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        tail = (proc.stdout or proc.stderr or '').strip().splitlines()
        tail_s = ' | '.join(tail[-3:]) if tail else '<no output>'
        fail(f'[1][{label}] validator FAIL exit={proc.returncode}: {tail_s}')

# [2] MD5 core invariants
for rel, exp in INVARIANTS.items():
    if not os.path.isfile(repo(rel)):
        fail(f'[2] invariant file missing: {rel}')
        continue
    got = md5_of(rel)
    if got != exp:
        fail(f'[2] invariant MD5 mismatch on {rel}: expected {exp}, got {got}')

# [2b] v42 utils MD5
for rel, exp in V42_UTILS_MD5.items():
    if not os.path.isfile(repo(rel)):
        fail(f'[2b] v42 util file missing: {rel}')
        continue
    got = md5_of(rel)
    if got != exp:
        fail(f'[2b] v42 util MD5 changed on {rel}: expected {exp}, got {got}')

# [3] rollup marker v43
if not os.path.isfile(repo(ROLLUP_MARKER_REL)):
    fail(f'[3] v43 rollup marker missing')
else:
    marker = load_json(ROLLUP_MARKER_REL)
    for key, exp in [
        ('runtime_activation', False), ('db_writes', 0),
        ('live_apply_allowed', False), ('live_commit_allowed', False),
        ('live_claim_allowed', False), ('reward_grant_enabled', False),
        ('bp_delta_runtime_enabled', False),
        ('redis_enabled', False), ('persistent_ledger_enabled', False),
        ('filesystem_writes_enabled', False),
        ('preview_request_blocked', False),
        ('all_8_operation_families_instrumented_with_replay_detection_dry_run', True),
        ('endpoint_paths_unchanged', True), ('feature_flags_unchanged', True),
        ('default_503_behavior_unchanged', True),
        ('safety_flags_unchanged', True),
        ('server_py_unchanged', True),
        ('public_sync_tag', PUBLIC_SYNC_TAG),
    ]:
        if marker.get(key) != exp:
            fail(f'[3] v43 rollup marker {key} must be {exp!r}')
    for track in ('track_a', 'track_b', 'rollup'):
        if not isinstance(marker.get(track), dict):
            fail(f'[3] v43 rollup marker missing {track} object')

# [4] prior markers present
for rel in PRIOR_MARKERS_REL:
    if not os.path.isfile(repo(rel)):
        fail(f'[4] prior marker missing: {rel}')

# [5] suite runner: 2 tuple v43 each exactly once + public sync tag
if not os.path.isfile(repo(SUITE_REL)):
    fail(f'[5] suite runner missing')
else:
    sr = read_text(SUITE_REL)
    for tup in SUITE_TUPLES_V43:
        cnt = sr.count(tup)
        if cnt != 1:
            fail(f'[5] suite runner must contain exactly 1 occurrence of {tup}, got {cnt}')
    if PUBLIC_SYNC_TAG not in sr:
        fail(f'[5] suite runner missing public sync tag: {PUBLIC_SYNC_TAG}')

# [6] doc 265 present
if not os.path.isfile(repo(DOC_REL)):
    fail(f'[6] doc missing: {DOC_REL}')

# [7] server.py: no v43 wiring (utility imported only by routes, not server)
sv = read_text(SERVER_REL)
if 'economy_idempotency_replay_detection_dry_run' in sv:
    fail('[7] server.py must not import the v43 utility')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] MEGA_ECONOMY_SAFETY_ACCELERATION_7_v43_ROLLUP validator')
    sys.exit(1)

print('[PASS] MEGA_ECONOMY_SAFETY_ACCELERATION_7_v43_ROLLUP validator')
sys.exit(0)
