#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator: PROJECT_BATTLE_REPLAY_PREVIEW_ROUTE_PACK (v36)
Phase: PHASE_6
Mode:  BATTLE_REPLAY_PREVIEW_ROUTE_GATED_VIEW_ONLY

Asserisce i 27 punti richiesti dal prompt.
"""
from __future__ import annotations
import json
import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

BACKEND_ROUTE_REL = 'backend/routes/battle_replay_preview.py'
FRONTEND_ROUTE_REL = 'frontend/app/battle-replay-preview.tsx'
DESIGN_REL = 'data/design/guild_war_replay/battle_replay_preview_route_v1.json'
PROOF_REL = 'data/design/guild_war_replay/battle_replay_preview_route_proof_marker_v1.json'
REGISTRY_V8 = 'data/design/battle_entrypoints/battle_entrypoint_registry_v8.json'
REGISTRY_V7 = 'data/design/battle_entrypoints/battle_entrypoint_registry_v7.json'
DOC_REL = 'docs/divine/237_BATTLE_REPLAY_PREVIEW_ROUTE.md'
VALIDATOR_REL = 'backend/scripts/validate_project_battle_replay_preview_route_v1.py'
SUITE_REL = 'backend/scripts/run_hero_skill_kit_validator_suite.py'

FEATURE_FLAG = 'BATTLE_REPLAY_PREVIEW_ENABLED'
NAMESPACE = '/api/battle-replay-preview'
ENDPOINTS = ['/config', '/sample-guild-war-replay', '/validate-replay-payload', '/playback-preview']

V35_REQUIRED_FIELDS = [
    'guild_war_battle_id', 'battle_instance_id', 'war_id', 'guild_id_attacker',
    'guild_id_defender', 'attacker_snapshot', 'defender_snapshot',
    'battle_seed_or_precomputed_log', 'playback_timeline', 'result_summary',
    'war_score_delta_display_only', 'reward_policy', 'guild_points_policy',
    'privacy_policy', 'retention_policy', 'created_at', 'expires_at',
]

PROOF_REQUIRED = {
    'battle_replay_preview_route_created': True,
    'battle_replay_live_route_created': False,
    'viewer_kind': 'guild_war_view',
    'generic_visual_shell_reused': True,
    'guild_war_runtime_changed': False,
    'war_score_mutation_enabled': False,
    'guild_points_mutation_enabled': False,
    'reward_grant_enabled': False,
    'exp_grant_enabled': False,
    'progress_enabled': False,
    'combat_tsx_changed': False,
    'story_tsx_changed': False,
    'story_sandbox_changed': False,
    'generic_preview_route_changed': False,
    'home_routes_changed': False,
    'battle_engine_changed': False,
    'economy_changed': False,
    'gacha_changed': False,
    'bp_vip_shop_changed': False,
    'material_raid_changed': False,
    'gem_socket_changed': False,
    'rune_runtime_changed': False,
    'artifact_runtime_changed': False,
    'divine_weapon_runtime_changed': False,
}

FAILURES: list[str] = []


def fail(msg): FAILURES.append(msg)
def repo(p): return os.path.join(REPO_ROOT, p)
def read_text(rel): return open(repo(rel), 'r', encoding='utf-8').read()
def load_json(rel): return json.load(open(repo(rel), 'r', encoding='utf-8'))


def _strip_python_comments_and_docstrings(src):
    out = re.sub(r'"""[\s\S]*?"""', '', src)
    out = re.sub(r"'''[\s\S]*?'''", '', out)
    out = re.sub(r'#[^\n]*', '', out)
    return out


def _strip_js_comments(src):
    out = re.sub(r'/\*[\s\S]*?\*/', '', src)
    out = re.sub(r'//[^\n]*', '', out)
    return out


# 1-3. backend route + frontend route + design/proof/doc/registry exist
for rel in [BACKEND_ROUTE_REL, FRONTEND_ROUTE_REL, DESIGN_REL, PROOF_REL, REGISTRY_V8, REGISTRY_V7, DOC_REL, VALIDATOR_REL]:
    if not os.path.isfile(repo(rel)):
        fail(f'[1-3] missing required file: {rel}')

if FAILURES:
    for f in FAILURES: print('FAIL:', f)
    print('[FAIL] PROJECT_BATTLE_REPLAY_PREVIEW_ROUTE validator')
    sys.exit(1)

route_text = read_text(BACKEND_ROUTE_REL)
frontend_text = read_text(FRONTEND_ROUTE_REL)
route_code = _strip_python_comments_and_docstrings(route_text)
frontend_code = _strip_js_comments(frontend_text)

# 4. namespace
if NAMESPACE not in route_text:
    fail(f'[4] backend route must contain namespace {NAMESPACE}')

# 5. feature flag
if FEATURE_FLAG not in route_text:
    fail(f'[5] backend route must reference {FEATURE_FLAG}')

# 6. default 503 disabled
if 'status_code=503' not in route_text:
    fail('[6] backend route must raise HTTP 503 when disabled')
if '"status": "disabled"' not in route_text and "'status': 'disabled'" not in route_text:
    fail('[6] backend route must include status:disabled envelope')

# 7. endpoints presence
for ep in ENDPOINTS:
    g = f'@router.get("{ep}")'; p = f'@router.post("{ep}")'
    if g not in route_text and p not in route_text:
        fail(f'[7] backend route missing endpoint decorator for {ep}')

# 8. sample replay includes all v35 fields
for fld in V35_REQUIRED_FIELDS:
    if f'"{fld}":' not in route_text:
        fail(f'[8] sample Guild War replay missing v35 field key: {fld}')

# 9. payload policies disable reward/guild points/war score mutation
for needle in [
    '"grant_enabled": False',           # reward_policy.grant_enabled
    '"replay_grants_rewards": False',
    '"mutate_enabled": False',          # guild_points_policy.mutate_enabled
    '"display_only_in_replay": True',
    '"applied": False',                 # war_score_delta_display_only.applied
    '"war_score_mutation_enabled": False',
    '"guild_points_mutation_enabled": False',
]:
    if needle not in route_text:
        fail(f'[9] backend route must contain safety token {needle}')

# 10. no battle_engine import
for tok in ['from battle_engine', 'import battle_engine', 'battle_engine.']:
    if tok in route_code:
        fail(f'[10] backend route must not reference battle_engine token: {tok}')

# 11. no /api/battle/simulate or /api/story/battle in executable code
for tok in ['/api/battle/simulate', '/api/story/battle']:
    if tok in route_code:
        fail(f'[11] backend route must not call {tok}')

# 12. no DB write tokens
for tok in ['db.users', 'db.user_heroes', 'db.server_profiles', '.update_one(', '.update_many(',
            '.insert_one(', '.insert_many(', '.delete_one(', '.delete_many(',
            'find_one_and_update', 'pymongo', 'AsyncIOMotorClient', 'motor.motor_asyncio']:
    if tok in route_text:
        fail(f'[12] backend route must not contain DB token: {tok}')

# 13. frontend: no /api/battle/simulate or /api/story/battle in exec
for tok in ['/api/battle/simulate', '/api/story/battle']:
    if tok in frontend_code:
        fail(f'[13] frontend route must not call {tok}')

# 14. no AsyncStorage write
for tok in ['AsyncStorage.setItem', 'AsyncStorage.mergeItem', 'AsyncStorage.multiSet',
            'AsyncStorage.multiMerge', 'AsyncStorage.removeItem', 'AsyncStorage.clear']:
    if tok in frontend_code:
        fail(f'[14] frontend route must not contain {tok}')

# 15. no claim/commit/war-score button text
banned = ['Claim Reward', 'Claim Now', 'Reclama Reward', 'Riscatta', 'Commit Now', 'Commit Result',
          'Commit Reward', 'Conferma Reward', 'Apply War Score', 'Apply Score', 'Commit War Score',
          'War Score Commit', 'War Score Claim']
for ph in banned:
    if ph in frontend_text:
        fail(f'[15] frontend must not contain button text: "{ph}"')

# 16. frontend references VisualBattlePreviewShell
if 'VisualBattlePreviewShell' not in frontend_code:
    fail('[16] frontend must reference VisualBattlePreviewShell')
if "from '../components/visualBattleRunner/VisualBattlePreviewShell'" not in frontend_code:
    fail('[16] frontend must import VisualBattlePreviewShell from v35 components path')

# 17. no live /battle-replay file created
for rel in ['frontend/app/battle-replay.tsx', 'backend/routes/battle_replay.py']:
    if os.path.isfile(repo(rel)):
        fail(f'[17] live battle-replay file must not exist: {rel}')

# 18. combat.tsx unchanged: still calls /api/battle/simulate
if '/api/battle/simulate' not in read_text('frontend/app/combat.tsx'):
    fail('[18] frontend/app/combat.tsx must still contain /api/battle/simulate')

# 19. story.tsx unchanged: still calls /api/story/battle
if '/api/story/battle' not in read_text('frontend/app/story.tsx'):
    fail('[19] frontend/app/story.tsx must still contain /api/story/battle')

# 20. sandbox unchanged (presence)
if not os.path.isfile(repo('frontend/app/story-visual-battle-sandbox.tsx')):
    fail('[20] story-visual-battle-sandbox.tsx must exist')

# 21. generic-visual-battle-runner-preview.tsx must still contain v35b sentinel
gv = 'frontend/app/generic-visual-battle-runner-preview.tsx'
if not os.path.isfile(repo(gv)):
    fail('[21] generic-visual-battle-runner-preview.tsx missing')
else:
    gvt = read_text(gv)
    if 'PUBLIC_CONTENT_REPAIR_v35b_VISUAL_BATTLE_PREVIEW_SHELL_MOUNT' not in gvt:
        fail('[21] generic-visual-battle-runner-preview.tsx must still contain v35b sentinel')
    if 'VisualBattlePreviewShell' not in gvt:
        fail('[21] generic-visual-battle-runner-preview.tsx must still mount VisualBattlePreviewShell')

# 22. Home routes unchanged: play/battle -> /story
hm = read_text('frontend/constants/homeAssetsManifest.ts')
block = re.search(r'HOME_ROUTES[^=]*=\s*\{([\s\S]*?)\};', hm)
if not block:
    fail('[22] HOME_ROUTES block missing')
else:
    blk = re.sub(r'//[^\n]*', '', block.group(1))
    if not re.search(r"\bplay\s*:\s*'/story'", blk):
        fail('[22] HOME_ROUTES.play must remain /story')
    if not re.search(r"\bbattle\s*:\s*'/story'", blk):
        fail('[22] HOME_ROUTES.battle must remain /story')
    if 'battle-replay-preview' in blk:
        fail('[22] HOME_ROUTES must not link to /battle-replay-preview')

# 23. battle_engine.py unchanged (presence)
if not os.path.isfile(repo('backend/battle_engine.py')):
    fail('[23] backend/battle_engine.py missing')

# 24. server.py: only registers preview router
sv = read_text('backend/server.py')
if 'from routes.battle_replay_preview import router' not in sv:
    fail('[24] server.py must import battle_replay_preview router')
if 'battle_replay_preview_router' not in sv:
    fail('[24] server.py must register battle_replay_preview_router')

# 25. registry v8 preserves v7 policies
reg8 = load_json(REGISTRY_V8)
reg7 = load_json(REGISTRY_V7)
v7_feats = {e.get('feature') for e in reg7.get('entries', [])}
v8_feats = {e.get('feature') for e in reg8.get('entries', [])}
missing = v7_feats - v8_feats
if missing:
    fail(f'[25] registry v8 missing v7 features: {sorted(missing)}')

if reg8.get('version') != 8:
    fail('[25] registry v8 version must be 8')

brp = next((e for e in reg8.get('entries', []) if e.get('feature') == 'battle_replay_preview'), None)
if not brp:
    fail('[25] registry v8 missing battle_replay_preview entry')
else:
    for k, exp in [
        ('current_endpoint', '/api/battle-replay-preview/*'),
        ('feature_flag', 'BATTLE_REPLAY_PREVIEW_ENABLED'),
        ('viewer_kind', 'guild_war_view'),
        ('reward_grant_enabled', False),
        ('exp_grant_enabled', False),
        ('progress_enabled', False),
        ('war_score_mutation_enabled', False),
        ('guild_points_mutation_enabled', False),
        ('db_writes', 0),
    ]:
        if brp.get(k) != exp:
            fail(f'[25] registry v8 battle_replay_preview.{k} must be {exp!r} (got {brp.get(k)!r})')

# guild_war preserved as only autoresolve exception
gw = next((e for e in reg8.get('entries', []) if e.get('feature') == 'guild_war'), None)
if not gw or gw.get('is_only_autoresolve_exception') is not True:
    fail('[25] registry v8 guild_war.is_only_autoresolve_exception must be True')

# battle_replay_viewer_future preserved
bv = next((e for e in reg8.get('entries', []) if e.get('feature') == 'battle_replay_viewer_future'), None)
if not bv or bv.get('runtime_status') != 'design_only':
    fail('[25] registry v8 battle_replay_viewer_future must remain runtime_status=design_only')

gp = reg8.get('global_policy', {}) or {}
for k, exp in [
    ('battle_replay_preview_route_ready', True),
    ('battle_replay_live_route_created', False),
    ('replay_view_never_grants_rewards', True),
    ('replay_view_never_mutates_war_score', True),
    ('replay_view_never_mutates_guild_points', True),
    ('only_guild_war_can_autoresolve', True),
]:
    if gp.get(k) is not exp:
        fail(f'[25] registry v8 global_policy.{k} must be {exp}')

# 26. proof marker booleans
proof = load_json(PROOF_REL)
for k, exp in PROOF_REQUIRED.items():
    if proof.get(k) != exp:
        fail(f'[26] proof marker {k} must be {exp!r} (got {proof.get(k)!r})')
if proof.get('db_writes', 1) != 0:
    fail('[26] proof marker db_writes must be 0')
if proof.get('default_http_status') != 503:
    fail('[26] proof marker default_http_status must be 503')
if proof.get('feature_flag') != FEATURE_FLAG:
    fail(f'[26] proof marker feature_flag must be {FEATURE_FLAG}')
if proof.get('suite_runner_tuple_v36_count') != 1:
    fail('[26] proof marker suite_runner_tuple_v36_count must be 1')

# 27. suite runner tuple count
if not os.path.isfile(repo(SUITE_REL)):
    fail('[27] suite runner missing')
else:
    sr = read_text(SUITE_REL)
    token = "'PROJECT-BATTLE-REPLAY-PREVIEW-ROUTE'"
    cnt = sr.count(token)
    if cnt != 1:
        fail(f'[27] suite runner must contain exactly 1 v36 tuple token, got {cnt}')
    for sentinel in [
        'PUBLIC_SYNC_DIAGNOSTIC_BLOCK_v36_BATTLE_REPLAY_PREVIEW_ROUTE',
        'PUBLIC_SYNC_TAG_v36_BATTLE_REPLAY_PREVIEW_ROUTE',
        'BATTLE_REPLAY_PREVIEW_ROUTE_REGISTRATION_SENTINEL',
    ]:
        if sentinel not in sr:
            fail(f'[27] suite runner missing sentinel: {sentinel}')
    val_name = 'validate_project_battle_replay_preview_route_v1.py'
    if sr.count(f"'{val_name}'") != 1:
        fail(f'[27] suite runner must reference {val_name} exactly once')

# Final
if FAILURES:
    for f in FAILURES: print('FAIL:', f)
    print('[FAIL] PROJECT_BATTLE_REPLAY_PREVIEW_ROUTE validator')
    sys.exit(1)

print('[PASS] PROJECT_BATTLE_REPLAY_PREVIEW_ROUTE validator')
sys.exit(0)
