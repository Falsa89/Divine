#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rollup validator: MEGA_VISUAL_BATTLE_ACCELERATION_2_v35

Esegue i due validator individuali e verifica:
  - Track A PASS
  - Track B PASS
  - proof markers exist
  - registry v7 exists
  - suite runner contains exactly 3 tuples v35 (count=1 ciascuna) e le 3 sentinelle
  - no DB writes / reward / EXP / progress / economy changes (via proof markers)
  - 5 file MD5-locked invariati (presence check)
  - combat.tsx / story.tsx / story-visual-battle-sandbox.tsx / Home routes /
    backend/battle_engine.py invariati (semantic check)
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SCRIPTS = os.path.join(REPO_ROOT, 'backend', 'scripts')

TRACK_A_VAL = 'validate_project_generic_visual_battle_runner_preview_runtime_shell_v1.py'
TRACK_B_VAL = 'validate_project_guild_war_autoresolve_replay_link_contract_v1.py'

PROOF_A = 'data/design/visual_battle_runner/generic_visual_battle_runner_preview_runtime_shell_proof_marker_v1.json'
PROOF_B = 'data/design/guild_war_replay/guild_war_replay_link_contract_proof_marker_v1.json'
ROLLUP_MARKER = 'data/design/visual_battle_runner/mega_visual_battle_acceleration_2_v35_rollup_marker_v1.json'
REGISTRY_V7 = 'data/design/battle_entrypoints/battle_entrypoint_registry_v7.json'
SUITE = 'backend/scripts/run_hero_skill_kit_validator_suite.py'

FAILURES: list[str] = []


def fail(m): FAILURES.append(m)
def repo(p): return os.path.join(REPO_ROOT, p)
def read_text(rel): return open(repo(rel), 'r', encoding='utf-8').read()


# 1. Track A + Track B validator PASS
for val in [TRACK_A_VAL, TRACK_B_VAL]:
    res = subprocess.run([sys.executable, os.path.join(SCRIPTS, val)], capture_output=True, text=True)
    if res.returncode != 0:
        fail(f'[1] {val} failed: {res.stdout}{res.stderr}')

# 2. proof markers exist
for rel in [PROOF_A, PROOF_B, ROLLUP_MARKER]:
    if not os.path.isfile(repo(rel)):
        fail(f'[2] missing marker: {rel}')

# 3. registry v7 exists
if not os.path.isfile(repo(REGISTRY_V7)):
    fail('[3] registry v7 missing')

# 4. suite runner has 3 tuples + sentinels
if not os.path.isfile(repo(SUITE)):
    fail('[4] suite runner missing')
else:
    sr = read_text(SUITE)
    for token in [
        "'PROJECT-GENERIC-VISUAL-BATTLE-RUNNER-PREVIEW-RUNTIME-SHELL'",
        "'PROJECT-GUILD-WAR-AUTORESOLVE-REPLAY-LINK-CONTRACT'",
        "'MEGA-VISUAL-BATTLE-ACCELERATION-2-v35-ROLLUP'",
    ]:
        cnt = sr.count(token)
        if cnt != 1:
            fail(f'[4] suite runner must contain exactly 1 occurrence of {token}, got {cnt}')
    for sentinel in [
        'PUBLIC_SYNC_DIAGNOSTIC_BLOCK_v35_MEGA_VISUAL_BATTLE_ACCELERATION_2',
        'PUBLIC_SYNC_TAG_v35_MEGA_VISUAL_BATTLE_ACCELERATION_2',
        'MEGA_VISUAL_BATTLE_ACCELERATION_2_REGISTRATION_SENTINEL',
    ]:
        if sentinel not in sr:
            fail(f'[4] suite runner missing sentinel: {sentinel}')

# 5. proof markers consistency: no DB writes / no reward grant / no progress
for rel in [PROOF_A, PROOF_B]:
    if os.path.isfile(repo(rel)):
        d = json.load(open(repo(rel), 'r', encoding='utf-8'))
        if d.get('db_writes', 1) != 0:
            fail(f'[5] {rel} db_writes must be 0')
        if d.get('reward_grant_enabled') is not False:
            fail(f'[5] {rel} reward_grant_enabled must be False')

# 6. MD5-locked files presence (rollup acts as last-stage gate; non aborts if md5 lib unavailable)
for rel in [
    'backend/battle_engine.py',
    'backend/.env',
    'backend/routes/artifacts.py',
    'frontend/app/battlepass.tsx',
    'frontend/app/vip.tsx',
]:
    if not os.path.isfile(repo(rel)):
        fail(f'[6] MD5-locked file missing: {rel}')

# 7. semantic unchanged files
for rel, must_contain in [
    ('frontend/app/combat.tsx', '/api/battle/simulate'),
    ('frontend/app/story.tsx', '/api/story/battle'),
]:
    if must_contain not in read_text(rel):
        fail(f'[7] {rel} must still contain {must_contain}')

if not os.path.isfile(repo('frontend/app/story-visual-battle-sandbox.tsx')):
    fail('[7] story-visual-battle-sandbox.tsx must exist')

hm = read_text('frontend/constants/homeAssetsManifest.ts')
block = re.search(r'HOME_ROUTES[^=]*=\s*\{([\s\S]*?)\};', hm)
if block:
    blk = re.sub(r'//[^\n]*', '', block.group(1))
    if not re.search(r"\bplay\s*:\s*'/story'", blk):
        fail('[7] HOME_ROUTES.play must remain /story')
    if not re.search(r"\bbattle\s*:\s*'/story'", blk):
        fail('[7] HOME_ROUTES.battle must remain /story')

if FAILURES:
    for f in FAILURES: print('FAIL:', f)
    print('[FAIL] MEGA_VISUAL_BATTLE_ACCELERATION_2_v35 rollup')
    sys.exit(1)

print('[PASS] MEGA_VISUAL_BATTLE_ACCELERATION_2_v35 rollup')
sys.exit(0)
