#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rollup validator: MEGA_ECONOMY_SAFETY_ACCELERATION_1_GEM_SOCKET_AND_MATERIAL_RAID_HARDENING_PACK_v37
Phase: MEGA_BATCH_ECONOMY_SAFETY_ACCELERATION_1
Mode:  PREVIEW-ONLY (Track A + Track B) + DESIGN-CONTRACT-AUDIT-ONLY (Track C)

Esegue back-to-back i 3 validator (Track A, Track B, Track C) e asserisce
invarianti globali:
  - 5 file core MD5-locked
  - tuple v37 conteggio = 1 ciascuna nel suite runner
  - rollup marker presente e coerente
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
    ('TRACK-A', 'validate_project_gem_socket_commit_safety_hardening_v1.py'),
    ('TRACK-B', 'validate_project_material_raid_claim_safety_hardening_v1.py'),
    ('TRACK-C', 'validate_project_economy_idempotency_and_atomic_commit_contract_v1.py'),
]

ROLLUP_MARKER_REL = 'data/design/economy_safety/mega_economy_safety_acceleration_1_v37_rollup_marker_v1.json'
DOC_REL = 'docs/divine/241_MEGA_ECONOMY_SAFETY_ACCELERATION_1_v37.md'
SUITE_REL = 'backend/scripts/run_hero_skill_kit_validator_suite.py'

SUITE_TUPLES_V37 = [
    "'PROJECT-GEM-SOCKET-COMMIT-SAFETY-HARDENING'",
    "'PROJECT-MATERIAL-RAID-CLAIM-SAFETY-HARDENING'",
    "'PROJECT-ECONOMY-IDEMPOTENCY-AND-ATOMIC-COMMIT-CONTRACT'",
    "'MEGA-ECONOMY-SAFETY-ACCELERATION-1-v37-ROLLUP'",
]

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


# [1] esegui i 3 validator back-to-back
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

# [2] MD5 invariants sui 5 file core
for rel, exp in INVARIANTS.items():
    p = repo(rel)
    if not os.path.isfile(p):
        fail(f'[2] invariant file missing: {rel}')
        continue
    with open(p, 'rb') as f:
        got = hashlib.md5(f.read()).hexdigest()
    if got != exp:
        fail(f'[2] invariant MD5 mismatch on {rel}: expected {exp}, got {got}')

# [3] rollup marker presente e coerente
if not os.path.isfile(repo(ROLLUP_MARKER_REL)):
    fail(f'[3] rollup marker missing: {ROLLUP_MARKER_REL}')
else:
    marker = load_json(ROLLUP_MARKER_REL)
    if marker.get('runtime_activation') is not False:
        fail('[3] rollup marker runtime_activation must be false')
    if marker.get('db_writes') != 0:
        fail('[3] rollup marker db_writes must be 0')
    for track in ('track_a', 'track_b', 'track_c', 'rollup'):
        if not isinstance(marker.get(track), dict):
            fail(f'[3] rollup marker missing {track} object')

# [4] suite runner: 4 tuple v37, ciascuna count=1
if not os.path.isfile(repo(SUITE_REL)):
    fail(f'[4] suite runner missing: {SUITE_REL}')
else:
    sr = read_text(SUITE_REL)
    for tup in SUITE_TUPLES_V37:
        cnt = sr.count(tup)
        if cnt != 1:
            fail(f'[4] suite runner must contain exactly 1 occurrence of {tup}, got {cnt}')

# [5] doc 241 presente
if not os.path.isfile(repo(DOC_REL)):
    fail(f'[5] doc missing: {DOC_REL}')

# Final
if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] MEGA_ECONOMY_SAFETY_ACCELERATION_1_v37_ROLLUP validator')
    sys.exit(1)

print('[PASS] MEGA_ECONOMY_SAFETY_ACCELERATION_1_v37_ROLLUP validator')
sys.exit(0)
