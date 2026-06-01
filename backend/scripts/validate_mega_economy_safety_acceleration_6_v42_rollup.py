#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator Rollup v42: MEGA-ECONOMY-SAFETY-ACCELERATION-6-v42-ROLLUP
Pack: MEGA_ECONOMY_SAFETY_ACCELERATION_6_DRY_RUN_RUNTIME_INSTRUMENTATION_PACK_v42

Esegue back-to-back i 3 validator A/B/C, asserisce invarianti globali del
pack v42:
  - 5 file core MD5-locked invariati
  - 4 tuple v42 nel suite runner (count = 1 ciascuna)
  - rollup marker v42 presente e coerente
  - public_sync_tag PUBLIC_SYNC_TAG_v42_MEGA_ECONOMY_SAFETY_ACCELERATION_6 presente
  - tutti i marker v37/v38/v39/v40/v41 ancora presenti
  - server.py non modificato per v42 (nessun import dei nuovi utils nel main app)
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
    ('TRACK-A', 'validate_request_hash_runtime_enforcement_dry_run_v1.py'),
    ('TRACK-B', 'validate_economy_observability_runtime_dry_run_v1.py'),
    ('TRACK-C', 'validate_economy_safety_canary_signoff_dry_run_pilot_v1.py'),
]

ROLLUP_MARKER_REL = 'data/design/economy_safety/mega_economy_safety_acceleration_6_v42_rollup_marker_v1.json'
DOC_REL = 'docs/divine/261_MEGA_ECONOMY_SAFETY_ACCELERATION_6_v42.md'
SUITE_REL = 'backend/scripts/run_hero_skill_kit_validator_suite.py'
SERVER_REL = 'backend/server.py'

PRIOR_MARKERS_REL = [
    'data/design/economy_safety/mega_economy_safety_acceleration_1_v37_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_2_v38_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_3_v39_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_4_v40_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_5_v41_rollup_marker_v1.json',
]

SUITE_TUPLES_V42 = [
    "'PROJECT-REQUEST-HASH-RUNTIME-ENFORCEMENT-DRY-RUN'",
    "'PROJECT-ECONOMY-OBSERVABILITY-RUNTIME-DRY-RUN'",
    "'PROJECT-ECONOMY-SAFETY-CANARY-SIGNOFF-DRY-RUN-PILOT'",
    "'MEGA-ECONOMY-SAFETY-ACCELERATION-6-v42-ROLLUP'",
]

PUBLIC_SYNC_TAG = 'PUBLIC_SYNC_TAG_v42_MEGA_ECONOMY_SAFETY_ACCELERATION_6'

INVARIANTS = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env': 'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx': '45fcc9890b6b128c37088bc33aa54caf',
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


# [1] run sub-validators back-to-back
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

# [2] MD5 invariants
for rel, exp in INVARIANTS.items():
    p = repo(rel)
    if not os.path.isfile(p):
        fail(f'[2] invariant file missing: {rel}')
        continue
    with open(p, 'rb') as f:
        got = hashlib.md5(f.read()).hexdigest()
    if got != exp:
        fail(f'[2] invariant MD5 mismatch on {rel}: expected {exp}, got {got}')

# [3] rollup marker v42
if not os.path.isfile(repo(ROLLUP_MARKER_REL)):
    fail(f'[3] v42 rollup marker missing: {ROLLUP_MARKER_REL}')
else:
    marker = load_json(ROLLUP_MARKER_REL)
    for key, exp in [
        ('runtime_activation', False), ('db_writes', 0),
        ('live_apply_allowed', False), ('live_commit_allowed', False),
        ('live_claim_allowed', False), ('reward_grant_enabled', False),
        ('bp_delta_runtime_enabled', False),
        ('all_8_operation_families_instrumented_with_request_hash_dry_run', True),
        ('all_8_operation_families_instrumented_with_observability_dry_run', True),
        ('endpoint_paths_unchanged', True), ('feature_flags_unchanged', True),
        ('default_503_behavior_unchanged', True),
        ('public_sync_tag', PUBLIC_SYNC_TAG),
    ]:
        if marker.get(key) != exp:
            fail(f'[3] v42 rollup marker {key} must be {exp!r}')
    for track in ('track_a', 'track_b', 'track_c', 'rollup'):
        if not isinstance(marker.get(track), dict):
            fail(f'[3] v42 rollup marker missing {track} object')

# [4] prior rollup markers presenti
for rel in PRIOR_MARKERS_REL:
    if not os.path.isfile(repo(rel)):
        fail(f'[4] prior rollup marker missing: {rel}')

# [5] suite runner: 4 tuple v42 each exactly once + PUBLIC_SYNC_TAG diag
if not os.path.isfile(repo(SUITE_REL)):
    fail(f'[5] suite runner missing: {SUITE_REL}')
else:
    sr = read_text(SUITE_REL)
    for tup in SUITE_TUPLES_V42:
        cnt = sr.count(tup)
        if cnt != 1:
            fail(f'[5] suite runner must contain exactly 1 occurrence of {tup}, got {cnt}')
    if PUBLIC_SYNC_TAG not in sr:
        fail(f'[5] suite runner missing public sync tag: {PUBLIC_SYNC_TAG}')

# [6] doc 261 presente
if not os.path.isfile(repo(DOC_REL)):
    fail(f'[6] doc missing: {DOC_REL}')

# [7] server.py: no v42 wiring (utility imported only by routes, not server)
sv = read_text(SERVER_REL)
forbidden_server_imports = [
    'economy_request_hash_dry_run',
    'economy_observability_dry_run',
]
for needle in forbidden_server_imports:
    if needle in sv:
        fail(f'[7] server.py must not import v42 utils: {needle}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] MEGA_ECONOMY_SAFETY_ACCELERATION_6_v42_ROLLUP validator')
    sys.exit(1)

print('[PASS] MEGA_ECONOMY_SAFETY_ACCELERATION_6_v42_ROLLUP validator')
sys.exit(0)
