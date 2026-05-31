#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rollup validator: MEGA_ECONOMY_SAFETY_ACCELERATION_3_ARTIFACT_AND_DIVINE_WEAPON_HARDENING_PACK_v39
Phase: MEGA_BATCH_ECONOMY_SAFETY_ACCELERATION_3
Mode:  PREVIEW-ONLY (Track A + Track B) + DESIGN-CONTRACT-AUDIT-ONLY (Track C registry v3)

Esegue back-to-back i 2 validator (Track A, Track B) e asserisce invarianti
globali: 5 file core MD5-locked, conteggi tuple v39 = 1, registry v3 presente
e coerente, v37/v38 shared contracts/registries ancora presenti,
backend/routes/artifacts.py intoccato (MD5 strict).
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
    ('TRACK-A', 'validate_project_artifact_upgrade_commit_safety_hardening_v1.py'),
    ('TRACK-B', 'validate_project_divine_weapon_upgrade_commit_safety_hardening_v1.py'),
]

ROLLUP_MARKER_REL = 'data/design/economy_safety/mega_economy_safety_acceleration_3_v39_rollup_marker_v1.json'
REGISTRY_V3_REL = 'data/design/economy_safety/endgame_economy_safety_registry_v3.json'
REGISTRY_V2_REL = 'data/design/economy_safety/build_system_economy_safety_registry_v2.json'
SHARED_CONTRACT_V1_REL = 'data/design/economy_safety/economy_idempotency_and_atomic_commit_contract_v1.json'
DOC_REL = 'docs/divine/249_MEGA_ECONOMY_SAFETY_ACCELERATION_3_v39.md'
SUITE_REL = 'backend/scripts/run_hero_skill_kit_validator_suite.py'
ARTIFACTS_REL = 'backend/routes/artifacts.py'
ARTIFACTS_MD5 = '893f244d85fd45cbe825996463995293'

SUITE_TUPLES_V39 = [
    "'PROJECT-ARTIFACT-UPGRADE-COMMIT-SAFETY-HARDENING'",
    "'PROJECT-DIVINE-WEAPON-UPGRADE-COMMIT-SAFETY-HARDENING'",
    "'MEGA-ECONOMY-SAFETY-ACCELERATION-3-v39-ROLLUP'",
]

INVARIANTS = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env': 'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': ARTIFACTS_MD5,
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


# [1] esegui i 2 validator back-to-back
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

# [3] rollup marker presente e coerente
if not os.path.isfile(repo(ROLLUP_MARKER_REL)):
    fail(f'[3] rollup marker missing: {ROLLUP_MARKER_REL}')
else:
    marker = load_json(ROLLUP_MARKER_REL)
    if marker.get('runtime_activation') is not False:
        fail('[3] rollup marker runtime_activation must be false')
    if marker.get('db_writes') != 0:
        fail('[3] rollup marker db_writes must be 0')
    if marker.get('bp_delta_runtime_enabled') is not False:
        fail('[3] rollup marker bp_delta_runtime_enabled must be false')
    for track in ('track_a', 'track_b', 'track_c', 'rollup'):
        if not isinstance(marker.get(track), dict):
            fail(f'[3] rollup marker missing {track} object')

# [4] registry v3 coerente
if not os.path.isfile(repo(REGISTRY_V3_REL)):
    fail(f'[4] registry v3 missing: {REGISTRY_V3_REL}')
else:
    reg = load_json(REGISTRY_V3_REL)
    if reg.get('version') != 3:
        fail('[4] registry v3 version must be 3')
    gl = reg.get('global', {}) or {}
    for k, exp in [
        ('endgame_safety_hardening_v39_ready', True),
        ('artifact_upgrade_safety_preview_ready', True),
        ('divine_weapon_upgrade_safety_preview_ready', True),
        ('live_commit_allowed_in_this_pack', False),
        ('db_writes', 0),
        ('reward_grant_enabled', False),
        ('materials_consumed', False),
        ('premium_currency_used', False),
        ('bp_delta_runtime_enabled', False),
    ]:
        if gl.get(k) != exp:
            fail(f'[4] registry v3 global.{k} must be {exp!r} (got {gl.get(k)!r})')
    fams = set((reg.get('operation_families') or {}).keys())
    miss = REQUIRED_OP_FAMILIES - fams
    if miss:
        fail(f'[4] registry v3 operation_families missing: {sorted(miss)}')
    of = reg.get('operation_families') or {}
    for fam in ('artifact_upgrade_commit', 'divine_weapon_upgrade_commit'):
        if of.get(fam, {}).get('live_commit_allowed') is not False:
            fail(f'[4] registry v3 {fam}.live_commit_allowed must be false')
        if of.get(fam, {}).get('db_writes') != 0:
            fail(f'[4] registry v3 {fam}.db_writes must be 0')
        if of.get(fam, {}).get('bp_delta_runtime_enabled') is not False:
            fail(f'[4] registry v3 {fam}.bp_delta_runtime_enabled must be false')

# [5] v37/v38 shared contracts/registries still present
for rel in [SHARED_CONTRACT_V1_REL, REGISTRY_V2_REL]:
    if not os.path.isfile(repo(rel)):
        fail(f'[5] required file from prior pack missing: {rel}')

# [6] artifacts.py legacy unchanged (MD5)
if not os.path.isfile(repo(ARTIFACTS_REL)):
    fail(f'[6] {ARTIFACTS_REL} missing')
else:
    with open(repo(ARTIFACTS_REL), 'rb') as f:
        got = hashlib.md5(f.read()).hexdigest()
    if got != ARTIFACTS_MD5:
        fail(f'[6] {ARTIFACTS_REL} MD5 must remain {ARTIFACTS_MD5} (got {got})')

# [7] suite runner: 3 tuple v39
if not os.path.isfile(repo(SUITE_REL)):
    fail(f'[7] suite runner missing: {SUITE_REL}')
else:
    sr = read_text(SUITE_REL)
    for tup in SUITE_TUPLES_V39:
        cnt = sr.count(tup)
        if cnt != 1:
            fail(f'[7] suite runner must contain exactly 1 occurrence of {tup}, got {cnt}')

# [8] doc 249 presente
if not os.path.isfile(repo(DOC_REL)):
    fail(f'[8] doc missing: {DOC_REL}')

# [9] server.py: scoped router registrations per i 2 preview safety v39
sv = read_text('backend/server.py')
required_includes = [
    'from routes.artifact_upgrade_safety_preview import router',
    'artifact_upgrade_safety_preview_router',
    'from routes.divine_weapon_upgrade_safety_preview import router',
    'divine_weapon_upgrade_safety_preview_router',
]
for needle in required_includes:
    if needle not in sv:
        fail(f'[9] server.py missing scoped router registration: {needle}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] MEGA_ECONOMY_SAFETY_ACCELERATION_3_v39_ROLLUP validator')
    sys.exit(1)

print('[PASS] MEGA_ECONOMY_SAFETY_ACCELERATION_3_v39_ROLLUP validator')
sys.exit(0)
