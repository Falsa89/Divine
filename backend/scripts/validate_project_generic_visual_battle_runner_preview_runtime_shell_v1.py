#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator Track A: PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_RUNTIME_SHELL_PACK (v35 Track A)
Phase: PHASE_4B
Mode:  PREVIEW_ROUTE_GATED_NO_LIVE_COMMIT

Verifica i 15 punti del prompt Track A.
"""
from __future__ import annotations
import json
import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

SHELL_COMPONENTS = [
    'frontend/components/visualBattleRunner/VisualBattlePreviewShell.tsx',
    'frontend/components/visualBattleRunner/VisualBattleTimelinePlayer.tsx',
    'frontend/components/visualBattleRunner/VisualBattlePreviewHpBars.tsx',
    'frontend/components/visualBattleRunner/VisualBattleSafetyPanel.tsx',
]
ROUTE_REL = 'frontend/app/generic-visual-battle-runner-preview.tsx'
DESIGN_REL = 'data/design/visual_battle_runner/generic_visual_battle_runner_preview_runtime_shell_v1.json'
PROOF_REL = 'data/design/visual_battle_runner/generic_visual_battle_runner_preview_runtime_shell_proof_marker_v1.json'
DOC_REL = 'docs/divine/233_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_RUNTIME_SHELL.md'

PROOF_REQUIRED = {
    'runtime_shell_created': True,
    'runtime_shell_runtime_changed': False,
    'reuses_existing_v34_route': True,
    'combat_tsx_changed': False,
    'story_tsx_changed': False,
    'story_sandbox_changed': False,
    'home_routes_changed': False,
    'battle_engine_changed': False,
    'backend_route_changed': False,
    'reward_grant_enabled': False,
    'exp_grant_enabled': False,
    'progress_enabled': False,
    'shell_components_have_reward_button': False,
    'shell_components_have_claim_button': False,
    'shell_components_have_commit_button': False,
    'shell_components_use_async_storage_writes': False,
    'shell_components_call_battle_simulate': False,
    'shell_components_call_story_battle': False,
    'shell_components_recompute_winner': False,
    'shell_components_simulate_battle': False,
    'shell_components_use_math_random_for_battle': False,
}

FAILURES: list[str] = []


def fail(msg): FAILURES.append(msg)
def repo(p): return os.path.join(REPO_ROOT, p)
def read_text(rel): return open(repo(rel), 'r', encoding='utf-8').read()


def _strip_js_comments(src: str) -> str:
    out = re.sub(r'/\*[\s\S]*?\*/', '', src)
    out = re.sub(r'//[^\n]*', '', out)
    return out


# 1. components exist
for rel in SHELL_COMPONENTS:
    if not os.path.isfile(repo(rel)):
        fail(f'[1] missing shell component: {rel}')

for rel in [ROUTE_REL, DESIGN_REL, PROOF_REL, DOC_REL]:
    if not os.path.isfile(repo(rel)):
        fail(f'[1] missing required file: {rel}')

if FAILURES:
    for f in FAILURES: print('FAIL:', f)
    print('[FAIL] PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_RUNTIME_SHELL validator')
    sys.exit(1)

route_text = read_text(ROUTE_REL)
route_code = _strip_js_comments(route_text)

# 2. route imports the shell
if 'VisualBattlePreviewShell' not in route_code:
    fail('[2] generic preview route must import/use VisualBattlePreviewShell')
if "from '../components/visualBattleRunner/VisualBattlePreviewShell'" not in route_code:
    fail('[2] generic preview route must import VisualBattlePreviewShell from components/visualBattleRunner')

# 3. shell route remains deeplink-only (no Home/menu link added)
hm_rel = 'frontend/constants/homeAssetsManifest.ts'
hm = read_text(hm_rel)
block = re.search(r'HOME_ROUTES[^=]*=\s*\{([\s\S]*?)\};', hm)
if block and 'generic-visual-battle-runner-preview' in block.group(1):
    fail('[3] HOME_ROUTES must not link to generic-visual-battle-runner-preview')

# 4. no Home/menu/story/combat link in components
all_components_text = ''
for rel in SHELL_COMPONENTS:
    all_components_text += '\n' + read_text(rel)
all_components_code = _strip_js_comments(all_components_text)
for needle in ["'/story'", '"/story"', "'/combat'", '"/combat"', "'/'", 'router.push', 'Link href']:
    if needle in all_components_code:
        fail(f'[4] shell components must not add navigation link: {needle}')

# 5+6. no /api/battle/simulate or /api/story/battle in shell components or route delta (code-only)
for tok in ['/api/battle/simulate', '/api/story/battle']:
    if tok in all_components_code:
        fail(f'[5-6] shell components must not call {tok}')

# 7. no reward/commit/claim button text in shell
banned = ['Claim Reward', 'Claim Now', 'Reclama', 'Riscatta', 'Commit Now', 'Commit Result', 'Commit Reward', 'Conferma Reward']
for ph in banned:
    if ph in all_components_text:
        fail(f'[7] shell components must not contain button text: "{ph}"')

# 8. no AsyncStorage write
for tok in ['AsyncStorage.setItem', 'AsyncStorage.mergeItem', 'AsyncStorage.multiSet', 'AsyncStorage.multiMerge', 'AsyncStorage.removeItem', 'AsyncStorage.clear']:
    if tok in all_components_code:
        fail(f'[8] shell components must not contain {tok}')

# 9. no DB/economy/token mutation patterns
for tok in ['db.users', 'db.user_heroes', '.update_one(', '.insert_one(', 'mongo', 'PyMongo']:
    if tok in all_components_code:
        fail(f'[9] shell components must not contain DB mutation token: {tok}')

# 10. combat.tsx unchanged (still calls /api/battle/simulate)
if '/api/battle/simulate' not in read_text('frontend/app/combat.tsx'):
    fail('[10] frontend/app/combat.tsx must still contain /api/battle/simulate')

# 11. story.tsx unchanged
if '/api/story/battle' not in read_text('frontend/app/story.tsx'):
    fail('[11] frontend/app/story.tsx must still contain /api/story/battle')

# 12. sandbox.tsx unchanged (presence)
if not os.path.isfile(repo('frontend/app/story-visual-battle-sandbox.tsx')):
    fail('[12] story-visual-battle-sandbox.tsx must exist')

# 13. Home routes unchanged: play/battle -> /story
block = re.search(r'HOME_ROUTES[^=]*=\s*\{([\s\S]*?)\};', hm)
if block:
    blk = re.sub(r'//[^\n]*', '', block.group(1))
    mp = re.search(r"\bplay\s*:\s*'([^']+)'", blk)
    mb = re.search(r"\bbattle\s*:\s*'([^']+)'", blk)
    if not mp or mp.group(1) != '/story':
        fail('[13] HOME_ROUTES.play must remain /story')
    if not mb or mb.group(1) != '/story':
        fail('[13] HOME_ROUTES.battle must remain /story')

# 14. battle_engine.py unchanged (presence)
if not os.path.isfile(repo('backend/battle_engine.py')):
    fail('[14] backend/battle_engine.py must exist')

# 15. proof marker booleans
proof = json.load(open(repo(PROOF_REL), 'r', encoding='utf-8'))
for k, expected in PROOF_REQUIRED.items():
    if proof.get(k) is not expected:
        fail(f'[15] proof marker {k} must be {expected} (got {proof.get(k)!r})')
if proof.get('db_writes', 1) != 0:
    fail('[15] proof marker db_writes must be 0')
if proof.get('suite_runner_tuple_v35_track_a_count') != 1:
    fail('[15] proof marker suite_runner_tuple_v35_track_a_count must be 1')

# no Math.random for battle outcomes in components
if re.search(r'Math\.random\s*\(\s*\)', all_components_code):
    fail('[BONUS] shell components must not use Math.random()')

if FAILURES:
    for f in FAILURES: print('FAIL:', f)
    print('[FAIL] PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_RUNTIME_SHELL validator')
    sys.exit(1)

print('[PASS] PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_RUNTIME_SHELL validator')
sys.exit(0)
