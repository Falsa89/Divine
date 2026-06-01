#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator Rollup: MEGA-ECONOMY-SAFETY-ACCELERATION-5-v41-ROLLUP
Pack: MEGA_ECONOMY_SAFETY_ACCELERATION_5_OBSERVABILITY_SIGNOFF_AND_REQUEST_HASH_PACK_v41

Esegue back-to-back i 3 validator Track A/B/C e asserisce invarianti
globali del pack v41:
  - 5 file core MD5-locked invariati
  - 4 tuple v41 nel suite runner (count = 1 ciascuna)
  - Rollup marker presente e coerente
  - Tutti i marker v37/v38/v39/v40 ancora presenti
  - Registry v4 ancora presente con copertura 8/8 famiglie operation
  - v41 non aggiunge nuovi router FastAPI: server.py non modificato per v41
  - Sentinelle LOUD precedenti (v38c, v39b, v40) ancora presenti in server.py
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
    ('TRACK-A', 'validate_shared_request_hash_idempotency_contract_v1.py'),
    ('TRACK-B', 'validate_economy_safety_observability_foundation_v1.py'),
    ('TRACK-C', 'validate_economy_safety_pre_signoff_bundle_v1.py'),
]

ROLLUP_MARKER_REL = 'data/design/economy_safety/mega_economy_safety_acceleration_5_v41_rollup_marker_v1.json'
DOC_REL = 'docs/divine/257_MEGA_ECONOMY_SAFETY_ACCELERATION_5_OBSERVABILITY_SIGNOFF_AND_REQUEST_HASH_PACK_v41_TRACK_D_ROLLUP.md'
SUITE_REL = 'backend/scripts/run_hero_skill_kit_validator_suite.py'
SERVER_REL = 'backend/server.py'

PRIOR_MARKERS_REL = [
    'data/design/economy_safety/mega_economy_safety_acceleration_1_v37_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_2_v38_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_3_v39_rollup_marker_v1.json',
    'data/design/economy_safety/mega_economy_safety_acceleration_4_v40_rollup_marker_v1.json',
]

REGISTRY_V4_REL = 'data/design/economy_safety/reward_claim_economy_safety_registry_v4.json'
SHARED_CONTRACT_V1_REL = 'data/design/economy_safety/economy_idempotency_and_atomic_commit_contract_v1.json'

LOUD_SENTINELS_PRIOR = [
    # v38c/v39b sentinelle sono state sostituite dalla v40 LOUD finale.
    # Verifichiamo solo la sentinella LOUD piu recente ancora presente.
    'PUBLIC_CONTENT_REGISTRATION_v40_BATTLE_PASS_AND_MAIL_CLAIM_SAFETY_LOUD',
]

SUITE_TUPLES_V41 = [
    "'PROJECT-SHARED-REQUEST-HASH-IDEMPOTENCY-CONTRACT'",
    "'PROJECT-ECONOMY-SAFETY-OBSERVABILITY-FOUNDATION'",
    "'PROJECT-ECONOMY-SAFETY-PRE-SIGNOFF-ROLLBACK-BUNDLE'",
    "'MEGA-ECONOMY-SAFETY-ACCELERATION-5-v41-ROLLUP'",
]

INVARIANTS = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env': 'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx': '45fcc9890b6b128c37088bc33aa54caf',
}

REQUIRED_OP_FAMILIES = {
    'gem_socket_commit', 'material_raid_claim',
    'gear_forge_fusion_commit', 'rune_scroll_talisman_commit',
    'artifact_upgrade_commit', 'divine_weapon_upgrade_commit',
    'battle_pass_reward_claim', 'mail_reward_claim',
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

# [3] rollup marker v41
if not os.path.isfile(repo(ROLLUP_MARKER_REL)):
    fail(f'[3] v41 rollup marker missing: {ROLLUP_MARKER_REL}')
else:
    marker = load_json(ROLLUP_MARKER_REL)
    if marker.get('runtime_activation') is not False:
        fail('[3] v41 rollup marker runtime_activation must be false')
    if marker.get('db_writes') != 0:
        fail('[3] v41 rollup marker db_writes must be 0')
    if marker.get('bp_delta_runtime_enabled') is not False:
        fail('[3] v41 rollup marker bp_delta_runtime_enabled must be false')
    for key in ('all_8_operation_families_have_preview_safety_layer',
                'all_8_operation_families_signoff_pending',
                'all_8_operation_families_canary_disabled',
                'all_8_operation_families_live_disabled'):
        if marker.get(key) is not True:
            fail(f'[3] v41 rollup marker {key} must be true')
    for track in ('track_a', 'track_b', 'track_c', 'rollup'):
        if not isinstance(marker.get(track), dict):
            fail(f'[3] v41 rollup marker missing {track} object')

# [4] prior rollup markers + registry v4 + shared contract v1
for rel in PRIOR_MARKERS_REL + [REGISTRY_V4_REL, SHARED_CONTRACT_V1_REL]:
    if not os.path.isfile(repo(rel)):
        fail(f'[4] required file from prior pack missing: {rel}')

# [5] registry v4 still 8/8 op families
if os.path.isfile(repo(REGISTRY_V4_REL)):
    reg = load_json(REGISTRY_V4_REL)
    fams = set((reg.get('operation_families') or {}).keys())
    miss = REQUIRED_OP_FAMILIES - fams
    if miss:
        fail(f'[5] registry v4 operation_families missing: {sorted(miss)}')
    gl = reg.get('global', {}) or {}
    if gl.get('all_8_operation_families_have_preview_safety_layer') is not True:
        fail('[5] registry v4 global.all_8_operation_families_have_preview_safety_layer must be true')
    if gl.get('db_writes') != 0:
        fail('[5] registry v4 global.db_writes must be 0')

# [6] suite runner: 4 tuple v41 each exactly once
if not os.path.isfile(repo(SUITE_REL)):
    fail(f'[6] suite runner missing: {SUITE_REL}')
else:
    sr = read_text(SUITE_REL)
    for tup in SUITE_TUPLES_V41:
        cnt = sr.count(tup)
        if cnt != 1:
            fail(f'[6] suite runner must contain exactly 1 occurrence of {tup}, got {cnt}')

# [7] doc 257 presente
if not os.path.isfile(repo(DOC_REL)):
    fail(f'[7] doc missing: {DOC_REL}')

# [8] server.py: prior LOUD sentinels still present (no v41 changes required)
sv = read_text(SERVER_REL)
for sent in LOUD_SENTINELS_PRIOR:
    if sent not in sv:
        fail(f'[8] server.py missing prior LOUD sentinel: {sent}')
# v41 must NOT add new include_router lines (validate no v41-specific router include)
forbidden_v41_includes = [
    'shared_request_hash_idempotency',
    'observability_foundation',
    'pre_signoff_bundle',
    'pre_signoff_rollback',
]
for needle in forbidden_v41_includes:
    if needle in sv:
        fail(f'[8] server.py must NOT include v41 runtime router: contains forbidden token {needle}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] MEGA_ECONOMY_SAFETY_ACCELERATION_5_v41_ROLLUP validator')
    sys.exit(1)

print('[PASS] MEGA_ECONOMY_SAFETY_ACCELERATION_5_v41_ROLLUP validator')
sys.exit(0)
