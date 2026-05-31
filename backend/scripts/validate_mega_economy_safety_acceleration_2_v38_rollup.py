#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rollup validator: MEGA_ECONOMY_SAFETY_ACCELERATION_2_GEAR_FORGE_AND_RUNE_HARDENING_PACK_v38
Phase: MEGA_BATCH_ECONOMY_SAFETY_ACCELERATION_2
Mode:  PREVIEW-ONLY (Track A + Track B) + DESIGN-CONTRACT-AUDIT-ONLY (Track C registry v2)

Esegue back-to-back i 2 validator (Track A, Track B) e asserisce invarianti
globali: 5 file core MD5-locked, conteggi tuple v38 = 1, registry v2 presente
e coerente, v37 shared contract ancora presente, forge.py intoccato.
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
    ('TRACK-A', 'validate_project_gear_forge_fusion_commit_safety_hardening_v1.py'),
    ('TRACK-B', 'validate_project_rune_scroll_talisman_commit_safety_hardening_v1.py'),
]

ROLLUP_MARKER_REL = 'data/design/economy_safety/mega_economy_safety_acceleration_2_v38_rollup_marker_v1.json'
REGISTRY_V2_REL = 'data/design/economy_safety/build_system_economy_safety_registry_v2.json'
SHARED_CONTRACT_V1_REL = 'data/design/economy_safety/economy_idempotency_and_atomic_commit_contract_v1.json'
DOC_REL = 'docs/divine/244_MEGA_ECONOMY_SAFETY_ACCELERATION_2_v38.md'
SUITE_REL = 'backend/scripts/run_hero_skill_kit_validator_suite.py'
FORGE_LEGACY_REL = 'backend/routes/forge.py'

SUITE_TUPLES_V38 = [
    "'PROJECT-GEAR-FORGE-FUSION-COMMIT-SAFETY-HARDENING'",
    "'PROJECT-RUNE-SCROLL-TALISMAN-COMMIT-SAFETY-HARDENING'",
    "'MEGA-ECONOMY-SAFETY-ACCELERATION-2-v38-ROLLUP'",
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

# [4] registry v2 coerente
if not os.path.isfile(repo(REGISTRY_V2_REL)):
    fail(f'[4] registry v2 missing: {REGISTRY_V2_REL}')
else:
    reg = load_json(REGISTRY_V2_REL)
    if reg.get('version') != 2:
        fail('[4] registry v2 version must be 2')
    gl = reg.get('global', {}) or {}
    for k, exp in [
        ('build_system_safety_hardening_v38_ready', True),
        ('live_commit_allowed_in_this_pack', False),
        ('db_writes', 0),
        ('reward_grant_enabled', False),
        ('materials_consumed', False),
        ('premium_currency_used', False),
        ('bp_delta_runtime_enabled', False),
    ]:
        if gl.get(k) != exp:
            fail(f'[4] registry v2 global.{k} must be {exp!r} (got {gl.get(k)!r})')
    fams = set((reg.get('operation_families') or {}).keys())
    miss = REQUIRED_OP_FAMILIES - fams
    if miss:
        fail(f'[4] registry v2 operation_families missing: {sorted(miss)}')
    # Track A/B safety layer state
    of = reg.get('operation_families') or {}
    for fam in ('gear_forge_fusion_commit', 'rune_scroll_talisman_commit'):
        if of.get(fam, {}).get('live_commit_allowed') is not False:
            fail(f'[4] registry v2 {fam}.live_commit_allowed must be false')
        if of.get(fam, {}).get('db_writes') != 0:
            fail(f'[4] registry v2 {fam}.db_writes must be 0')
        if of.get(fam, {}).get('bp_delta_runtime_enabled') is not False:
            fail(f'[4] registry v2 {fam}.bp_delta_runtime_enabled must be false')

# [5] v37 shared contract still exists
if not os.path.isfile(repo(SHARED_CONTRACT_V1_REL)):
    fail(f'[5] v37 shared contract missing: {SHARED_CONTRACT_V1_REL}')

# [6] forge.py legacy unchanged (presence)
if not os.path.isfile(repo(FORGE_LEGACY_REL)):
    fail(f'[6] forge.py legacy missing: {FORGE_LEGACY_REL}')

# [7] suite runner: 3 tuple v38
if not os.path.isfile(repo(SUITE_REL)):
    fail(f'[7] suite runner missing: {SUITE_REL}')
else:
    sr = read_text(SUITE_REL)
    for tup in SUITE_TUPLES_V38:
        cnt = sr.count(tup)
        if cnt != 1:
            fail(f'[7] suite runner must contain exactly 1 occurrence of {tup}, got {cnt}')

# [8] doc 244 presente
if not os.path.isfile(repo(DOC_REL)):
    fail(f'[8] doc missing: {DOC_REL}')

# [9] server.py: solo router scoped registrations per i 2 preview safety
sv = read_text('backend/server.py')
required_includes = [
    'from routes.gear_forge_fusion_safety_preview import router',
    'gear_forge_fusion_safety_preview_router',
    'from routes.rune_scroll_talisman_safety_preview import router',
    'rune_scroll_talisman_safety_preview_router',
]
for needle in required_includes:
    if needle not in sv:
        fail(f'[9] server.py missing scoped router registration: {needle}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] MEGA_ECONOMY_SAFETY_ACCELERATION_2_v38_ROLLUP validator')
    sys.exit(1)

print('[PASS] MEGA_ECONOMY_SAFETY_ACCELERATION_2_v38_ROLLUP validator')
sys.exit(0)
