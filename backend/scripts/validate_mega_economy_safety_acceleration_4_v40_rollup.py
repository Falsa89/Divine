#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rollup validator: MEGA_ECONOMY_SAFETY_ACCELERATION_4_BATTLE_PASS_AND_MAIL_CLAIM_HARDENING_PACK_v40
Phase: MEGA_BATCH_ECONOMY_SAFETY_ACCELERATION_4

Esegue back-to-back i 2 validator (Track A, Track B) e asserisce invarianti
globali: 5 file core MD5-locked, conteggi tuple v40 = 1, registry v4 presente
e coerente (8 op families con safety layer), v37/v38/v39 registries ancora
presenti, sentinel LOUD v40 in server.py.
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
    ('TRACK-A', 'validate_project_battle_pass_claim_safety_hardening_v1.py'),
    ('TRACK-B', 'validate_project_mail_claim_safety_hardening_v1.py'),
]

ROLLUP_MARKER_REL = 'data/design/economy_safety/mega_economy_safety_acceleration_4_v40_rollup_marker_v1.json'
REGISTRY_V4_REL = 'data/design/economy_safety/reward_claim_economy_safety_registry_v4.json'
REGISTRY_V3_REL = 'data/design/economy_safety/endgame_economy_safety_registry_v3.json'
REGISTRY_V2_REL = 'data/design/economy_safety/build_system_economy_safety_registry_v2.json'
SHARED_CONTRACT_V1_REL = 'data/design/economy_safety/economy_idempotency_and_atomic_commit_contract_v1.json'
DOC_REL = 'docs/divine/253_MEGA_ECONOMY_SAFETY_ACCELERATION_4_v40.md'
SUITE_REL = 'backend/scripts/run_hero_skill_kit_validator_suite.py'
SERVER_REL = 'backend/server.py'

LOUD_SENTINEL = 'PUBLIC_CONTENT_REGISTRATION_v40_BATTLE_PASS_AND_MAIL_CLAIM_SAFETY_LOUD'

SUITE_TUPLES_V40 = [
    "'PROJECT-BATTLE-PASS-CLAIM-SAFETY-HARDENING'",
    "'PROJECT-MAIL-CLAIM-SAFETY-HARDENING'",
    "'MEGA-ECONOMY-SAFETY-ACCELERATION-4-v40-ROLLUP'",
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


# [1] run sub-validators
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

# [3] rollup marker
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
    if marker.get('all_8_operation_families_have_preview_safety_layer') is not True:
        fail('[3] rollup marker all_8_operation_families_have_preview_safety_layer must be true')
    for track in ('track_a', 'track_b', 'track_c', 'rollup'):
        if not isinstance(marker.get(track), dict):
            fail(f'[3] rollup marker missing {track} object')

# [4] registry v4 coerente
if not os.path.isfile(repo(REGISTRY_V4_REL)):
    fail(f'[4] registry v4 missing: {REGISTRY_V4_REL}')
else:
    reg = load_json(REGISTRY_V4_REL)
    if reg.get('version') != 4:
        fail('[4] registry v4 version must be 4')
    if reg.get('supersedes') != 'endgame_economy_safety_registry_v3':
        fail('[4] registry v4 must supersede endgame_economy_safety_registry_v3')
    gl = reg.get('global', {}) or {}
    for k, exp in [
        ('all_8_operation_families_have_preview_safety_layer', True),
        ('battle_pass_claim_safety_preview_ready', True),
        ('mail_claim_safety_preview_ready', True),
        ('live_commit_allowed_in_this_pack', False),
        ('live_claim_allowed_in_this_pack', False),
        ('db_writes', 0),
        ('reward_grant_enabled', False),
        ('materials_consumed', False),
        ('premium_currency_used', False),
        ('bp_delta_runtime_enabled', False),
    ]:
        if gl.get(k) != exp:
            fail(f'[4] registry v4 global.{k} must be {exp!r} (got {gl.get(k)!r})')
    fams = set((reg.get('operation_families') or {}).keys())
    miss = REQUIRED_OP_FAMILIES - fams
    if miss:
        fail(f'[4] registry v4 operation_families missing: {sorted(miss)}')
    of = reg.get('operation_families') or {}
    for fam in ('battle_pass_reward_claim', 'mail_reward_claim'):
        node = of.get(fam, {}) or {}
        if node.get('status') != 'preview_only_safety_layer_present':
            fail(f'[4] registry v4 {fam}.status must be preview_only_safety_layer_present')
        if node.get('live_claim_allowed') is not False:
            fail(f'[4] registry v4 {fam}.live_claim_allowed must be false')
        if node.get('reward_grant_enabled') is not False:
            fail(f'[4] registry v4 {fam}.reward_grant_enabled must be false')
        if node.get('db_writes') != 0:
            fail(f'[4] registry v4 {fam}.db_writes must be 0')

# [5] v37 contract + v38 registry v2 + v39 registry v3 still present
for rel in [SHARED_CONTRACT_V1_REL, REGISTRY_V2_REL, REGISTRY_V3_REL]:
    if not os.path.isfile(repo(rel)):
        fail(f'[5] required file from prior pack missing: {rel}')

# [6] suite runner: 3 tuple v40
if not os.path.isfile(repo(SUITE_REL)):
    fail(f'[6] suite runner missing: {SUITE_REL}')
else:
    sr = read_text(SUITE_REL)
    for tup in SUITE_TUPLES_V40:
        cnt = sr.count(tup)
        if cnt != 1:
            fail(f'[6] suite runner must contain exactly 1 occurrence of {tup}, got {cnt}')

# [7] doc 253 presente
if not os.path.isfile(repo(DOC_REL)):
    fail(f'[7] doc missing: {DOC_REL}')

# [8] server.py: scoped router registrations + LOUD sentinel
sv = read_text(SERVER_REL)
required_includes = [
    'from routes.battle_pass_claim_safety_preview import router',
    'battle_pass_claim_safety_preview_router',
    'from routes.mail_claim_safety_preview import router',
    'mail_claim_safety_preview_router',
]
for needle in required_includes:
    if needle not in sv:
        fail(f'[8] server.py missing scoped router registration: {needle}')
if LOUD_SENTINEL not in sv:
    fail(f'[8] server.py missing LOUD sentinel: {LOUD_SENTINEL}')
if sv.count('app.include_router(battle_pass_claim_safety_preview_router)') != 1:
    fail('[8] server.py include_router(battle_pass_claim_safety_preview_router) count must be 1')
if sv.count('app.include_router(mail_claim_safety_preview_router)') != 1:
    fail('[8] server.py include_router(mail_claim_safety_preview_router) count must be 1')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] MEGA_ECONOMY_SAFETY_ACCELERATION_4_v40_ROLLUP validator')
    sys.exit(1)

print('[PASS] MEGA_ECONOMY_SAFETY_ACCELERATION_4_v40_ROLLUP validator')
sys.exit(0)
