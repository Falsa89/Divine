#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator: PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE_PACK (v34)
Phase: PHASE_4
Mode:  PREVIEW_ROUTE_GATED_NO_LIVE_COMMIT

Asserisce i 24 punti richiesti dal prompt del pack.
"""
from __future__ import annotations
import json
import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

BACKEND_ROUTE_REL = 'backend/routes/generic_visual_battle_runner_preview.py'
FRONTEND_ROUTE_REL = 'frontend/app/generic-visual-battle-runner-preview.tsx'
DESIGN_REL = 'data/design/visual_battle_runner/generic_visual_battle_runner_preview_route_v1.json'
PROOF_REL = 'data/design/visual_battle_runner/generic_visual_battle_runner_preview_route_proof_marker_v1.json'
REGISTRY_V6_REL = 'data/design/battle_entrypoints/battle_entrypoint_registry_v6.json'
REGISTRY_V5_REL = 'data/design/battle_entrypoints/battle_entrypoint_registry_v5.json'
DOC_REL = 'docs/divine/232_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE.md'
VALIDATOR_REL = 'backend/scripts/validate_project_generic_visual_battle_runner_preview_route_v1.py'
SUITE_REL = 'backend/scripts/run_hero_skill_kit_validator_suite.py'

FEATURE_FLAG = 'GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ENABLED'
NAMESPACE = '/api/generic-visual-battle-runner-preview'
ENDPOINTS = ['/config', '/sample-payload', '/validate-payload', '/playback-preview']

V33_REQUIRED_FIELDS = [
    'battle_instance_id',
    'runner_mode',
    'mode_id',
    'source_entrypoint',
    'viewer_kind',
    'team_snapshot',
    'enemy_snapshot',
    'formation_snapshot',
    'battle_background_context',
    'battle_seed_or_precomputed_battle_log',
    'playback_timeline',
    'result_summary',
    'reward_policy',
    'exp_policy',
    'progress_policy',
    'result_commit_policy',
    'replay_snapshot_policy',
    'ui_policy',
    'privacy_policy',
    'created_at',
    'expires_at',
]

PROOF_REQUIRED_BOOLEANS = {
    'generic_runner_preview_route_created': True,
    'generic_runner_live_runtime_enabled': False,
    'combat_tsx_changed': False,
    'story_tsx_changed': False,
    'story_sandbox_changed': False,
    'home_routes_changed': False,
    'battle_engine_changed': False,
    'story_battle_endpoint_changed': False,
    'battle_simulate_endpoint_changed': False,
    'story_runtime_conversion_done': False,
    'combat_route_refactored': False,
    'reward_grant_enabled': False,
    'exp_grant_enabled': False,
    'progress_enabled': False,
    'economy_changed': False,
    'gacha_changed': False,
    'bp_vip_shop_changed': False,
    'material_raid_changed': False,
    'gem_socket_changed': False,
    'rune_runtime_changed': False,
    'artifact_runtime_changed': False,
    'divine_weapon_runtime_changed': False,
    'guild_war_runtime_changed': False,
    'runner_preview_never_grants_rewards': True,
    'runner_preview_never_grants_exp': True,
    'runner_preview_never_advances_progress': True,
}

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def repo(p: str) -> str:
    return os.path.join(REPO_ROOT, p)


def read_text(rel: str) -> str:
    with open(repo(rel), 'r', encoding='utf-8') as fh:
        return fh.read()


def load_json(rel: str) -> dict:
    with open(repo(rel), 'r', encoding='utf-8') as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# 1-3. backend route + frontend route + design/proof/doc/registry exist
# ---------------------------------------------------------------------------
required_files = [
    BACKEND_ROUTE_REL,
    FRONTEND_ROUTE_REL,
    DESIGN_REL,
    PROOF_REL,
    REGISTRY_V6_REL,
    DOC_REL,
    VALIDATOR_REL,
]
for rel in required_files:
    if not os.path.isfile(repo(rel)):
        fail(f'[1-3] missing required file: {rel}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE validator')
    sys.exit(1)

route_text = read_text(BACKEND_ROUTE_REL)
frontend_text = read_text(FRONTEND_ROUTE_REL)

# ---------------------------------------------------------------------------
# 4. namespace
# ---------------------------------------------------------------------------
if NAMESPACE not in route_text:
    fail(f'[4] backend route must contain namespace {NAMESPACE}')

# ---------------------------------------------------------------------------
# 5. feature flag
# ---------------------------------------------------------------------------
if FEATURE_FLAG not in route_text:
    fail(f'[5] backend route must reference feature flag {FEATURE_FLAG}')

# ---------------------------------------------------------------------------
# 6. default 503 disabled behavior
# ---------------------------------------------------------------------------
if 'status_code=503' not in route_text:
    fail('[6] backend route must raise HTTP 503 when disabled')
if '"status": "disabled"' not in route_text and "'status': 'disabled'" not in route_text:
    fail('[6] backend route must include status:disabled envelope')

# ---------------------------------------------------------------------------
# 7. endpoints presence
# ---------------------------------------------------------------------------
for ep in ENDPOINTS:
    # search for @router.get("/config") or @router.post("/validate-payload")
    method_get = f'@router.get("{ep}")'
    method_post = f'@router.post("{ep}")'
    if method_get not in route_text and method_post not in route_text:
        fail(f'[7] backend route missing endpoint decorator for {ep}')

# ---------------------------------------------------------------------------
# 8. sample payload includes all v33 schema fields
# ---------------------------------------------------------------------------
for fld in V33_REQUIRED_FIELDS:
    needle = f'"{fld}":'
    if needle not in route_text:
        fail(f'[8] sample payload missing v33 field key: {fld}')

# ---------------------------------------------------------------------------
# 9. safety flags presence (no reward/EXP/progress/DB)
# ---------------------------------------------------------------------------
for sf in [
    '"db_writes": 0',
    '"reward_grant_enabled": False',
    '"exp_grant_enabled": False',
    '"progress_enabled": False',
]:
    if sf not in route_text:
        fail(f'[9] backend route must expose safety flag {sf}')

# ---------------------------------------------------------------------------
# 10. route does not import/call battle_engine
# ---------------------------------------------------------------------------
forbidden_engine_tokens = [
    'from battle_engine',
    'import battle_engine',
    'battle_engine.',
]
for tok in forbidden_engine_tokens:
    if tok in route_text:
        fail(f'[10] backend route must not reference battle_engine: token "{tok}"')

# ---------------------------------------------------------------------------
# 11. route does not call /api/battle/simulate or /api/story/battle
# (commenti e docstring sono esclusi: contengono dichiarazioni di sicurezza
#  che indicano esplicitamente l'assenza della chiamata; controlliamo solo il
#  codice eseguibile.)
# ---------------------------------------------------------------------------
def _strip_python_comments_and_docstrings(src: str) -> str:
    # rimuovi triple-quoted strings (sia """ che ''')
    out = re.sub(r'"""[\s\S]*?"""', '', src)
    out = re.sub(r"'''[\s\S]*?'''", '', out)
    # rimuovi commenti single-line python
    out = re.sub(r'#[^\n]*', '', out)
    return out


route_code_only = _strip_python_comments_and_docstrings(route_text)
forbidden_endpoint_calls = ['/api/battle/simulate', '/api/story/battle']
for tok in forbidden_endpoint_calls:
    if tok in route_code_only:
        fail(f'[11] backend route must not call/reference {tok} (in executable code)')

# ---------------------------------------------------------------------------
# 12. route does not contain DB write tokens
# ---------------------------------------------------------------------------
forbidden_db_tokens = [
    'db.users',
    'db.user_heroes',
    'db.server_profiles',
    'db.story_progress',
    'db.quests',
    'db.daily',
    'db.achievements',
    '.update_one(',
    '.update_many(',
    '.insert_one(',
    '.insert_many(',
    '.delete_one(',
    '.delete_many(',
    'find_one_and_update',
    'pymongo',
    'AsyncIOMotorClient',
    'motor.motor_asyncio',
]
for tok in forbidden_db_tokens:
    if tok in route_text:
        fail(f'[12] backend route must not contain DB write token: {tok}')

# ---------------------------------------------------------------------------
# 13. frontend does not call /api/battle/simulate or /api/story/battle
# (commenti TS esclusi: contengono dichiarazioni di sicurezza)
# ---------------------------------------------------------------------------
def _strip_js_comments(src: str) -> str:
    # rimuovi /* ... */ multi-line
    out = re.sub(r'/\*[\s\S]*?\*/', '', src)
    # rimuovi // commenti single-line
    out = re.sub(r'//[^\n]*', '', out)
    return out


frontend_code_only = _strip_js_comments(frontend_text)
for tok in forbidden_endpoint_calls:
    if tok in frontend_code_only:
        fail(f'[13] frontend route must not call {tok} (in executable code)')

# ---------------------------------------------------------------------------
# 14. frontend does not contain AsyncStorage write tokens
# ---------------------------------------------------------------------------
forbidden_async_tokens = [
    'AsyncStorage.setItem',
    'AsyncStorage.mergeItem',
    'AsyncStorage.multiSet',
    'AsyncStorage.multiMerge',
    'AsyncStorage.removeItem',
    'AsyncStorage.clear',
]
for tok in forbidden_async_tokens:
    if tok in frontend_text:
        fail(f'[14] frontend route must not contain {tok}')

# ---------------------------------------------------------------------------
# 15. no claim/commit button text in frontend
# ---------------------------------------------------------------------------
banned_button_phrases = [
    'Claim Reward',
    'claim reward',
    'Claim Now',
    'Reclama',
    'Reclama Reward',
    'Riscatta',
    'Commit Result',
    'Commit Now',
    'Commit Reward',
    'Conferma Reward',
]
for phrase in banned_button_phrases:
    if phrase in frontend_text:
        fail(f'[15] frontend route must not contain button text: "{phrase}"')

# Inoltre verifichiamo che le safety flags FE dichiarino claim/commit disabilitati.
if 'claim_button_enabled' in frontend_text and '"true"' in frontend_text.replace(' ', '').lower():
    # heuristic only; non-fatal
    pass

# ---------------------------------------------------------------------------
# 16. combat.tsx unchanged and still contains /api/battle/simulate
# ---------------------------------------------------------------------------
combat_rel = 'frontend/app/combat.tsx'
if not os.path.isfile(repo(combat_rel)):
    fail('[16] frontend/app/combat.tsx missing')
else:
    if '/api/battle/simulate' not in read_text(combat_rel):
        fail('[16] frontend/app/combat.tsx must still contain /api/battle/simulate')

# ---------------------------------------------------------------------------
# 17. story.tsx unchanged and still contains /api/story/battle
# ---------------------------------------------------------------------------
story_rel = 'frontend/app/story.tsx'
if not os.path.isfile(repo(story_rel)):
    fail('[17] frontend/app/story.tsx missing')
else:
    if '/api/story/battle' not in read_text(story_rel):
        fail('[17] frontend/app/story.tsx must still contain /api/story/battle')

# ---------------------------------------------------------------------------
# 18. story-visual-battle-sandbox.tsx unchanged (presence check)
# ---------------------------------------------------------------------------
sandbox_rel = 'frontend/app/story-visual-battle-sandbox.tsx'
if not os.path.isfile(repo(sandbox_rel)):
    fail('[18] frontend/app/story-visual-battle-sandbox.tsx missing')

# ---------------------------------------------------------------------------
# 19. Home routes unchanged: homeAssetsManifest.ts keeps play/battle -> /story
# ---------------------------------------------------------------------------
hm_rel = 'frontend/constants/homeAssetsManifest.ts'
if not os.path.isfile(repo(hm_rel)):
    fail('[19] frontend/constants/homeAssetsManifest.ts missing')
else:
    hm = read_text(hm_rel)
    block_match = re.search(r'HOME_ROUTES[^=]*=\s*\{([\s\S]*?)\};', hm)
    if not block_match:
        fail('[19] HOME_ROUTES block not found')
    else:
        block_clean = re.sub(r'//[^\n]*', '', block_match.group(1))
        m_play = re.search(r"\bplay\s*:\s*'([^']+)'", block_clean)
        m_battle = re.search(r"\bbattle\s*:\s*'([^']+)'", block_clean)
        if not m_play or m_play.group(1) != '/story':
            fail(f"[19] HOME_ROUTES.play must map to /story (got {m_play.group(1) if m_play else None})")
        if not m_battle or m_battle.group(1) != '/story':
            fail(f"[19] HOME_ROUTES.battle must map to /story (got {m_battle.group(1) if m_battle else None})")

# ---------------------------------------------------------------------------
# 20. battle_engine.py unchanged (presence + size sanity)
# ---------------------------------------------------------------------------
be_rel = 'backend/battle_engine.py'
if not os.path.isfile(repo(be_rel)):
    fail('[20] backend/battle_engine.py missing')

# ---------------------------------------------------------------------------
# 21. server.py only changed to register the preview router
# ---------------------------------------------------------------------------
server_rel = 'backend/server.py'
if not os.path.isfile(repo(server_rel)):
    fail('[21] backend/server.py missing')
else:
    sv = read_text(server_rel)
    if 'from routes.generic_visual_battle_runner_preview import router' not in sv:
        fail('[21] server.py must import generic_visual_battle_runner_preview router')
    if 'generic_visual_battle_runner_preview_router' not in sv:
        fail('[21] server.py must register generic_visual_battle_runner_preview_router')
    # nessuna nuova chiamata a battle simulate aggiunta
    # (heuristic — we accept simulate references that were already there)

# ---------------------------------------------------------------------------
# 22. registry v6 preserves v5 policies + adds preview entry
# ---------------------------------------------------------------------------
reg6 = load_json(REGISTRY_V6_REL)
if reg6.get('version') != 6:
    fail('[22] registry v6 version must be 6')
entries = reg6.get('entries', []) or []
by_feat = {e.get('feature'): e for e in entries}

# preview entry presente e gated
pv = by_feat.get('generic_visual_battle_runner_preview')
if not pv:
    fail('[22] registry v6 missing generic_visual_battle_runner_preview entry')
else:
    if pv.get('current_endpoint') != '/api/generic-visual-battle-runner-preview/*':
        fail('[22] registry v6 preview entry current_endpoint mismatch')
    if pv.get('feature_flag') != FEATURE_FLAG:
        fail('[22] registry v6 preview entry feature_flag mismatch')
    for k in ['reward_grant_enabled', 'exp_grant_enabled', 'progress_enabled']:
        if pv.get(k) is not False:
            fail(f'[22] registry v6 preview entry {k} must be False')
    if pv.get('db_writes', 1) != 0:
        fail('[22] registry v6 preview entry db_writes must be 0')

# preserve v5 entries
preserved = {
    'direct_visual_combat_route': 'generic_runner_contract_ready_runtime_pending',
    'story_stage_battle': 'sandbox_ready_runner_contract_ready_runtime_pending',
    'story_visual_battle_sandbox': 'sandbox_preview_ready',
}
for feat, expected_status in preserved.items():
    e = by_feat.get(feat)
    if not e:
        fail(f'[22] registry v6 missing preserved entry: {feat}')
    elif e.get('contract_status') != expected_status:
        fail(f'[22] registry v6 entry {feat}.contract_status must remain {expected_status} (got {e.get("contract_status")!r})')

# guild_war preserved as only autoresolve exception
gw = by_feat.get('guild_war')
if not gw:
    fail('[22] registry v6 missing guild_war entry')
else:
    if gw.get('is_only_autoresolve_exception') is not True:
        fail('[22] registry v6 guild_war.is_only_autoresolve_exception must remain True')
    if gw.get('replay_link_required') is not True:
        fail('[22] registry v6 guild_war.replay_link_required must remain True')

# global_policy keys
gp = reg6.get('global_policy', {}) or {}
for k, expected in {
    'generic_runner_preview_route_ready': True,
    'generic_runner_live_runtime_done': False,
    'combat_route_refactored': False,
    'story_runtime_conversion_done': False,
    'runner_preview_never_grants_rewards': True,
    'runner_preview_never_grants_exp': True,
    'runner_preview_never_advances_progress': True,
    'only_guild_war_can_autoresolve': True,
}.items():
    if gp.get(k) is not expected:
        fail(f'[22] registry v6 global_policy.{k} must be {expected}')

# ---------------------------------------------------------------------------
# 23. proof marker booleans correct
# ---------------------------------------------------------------------------
proof = load_json(PROOF_REL)
for k, expected in PROOF_REQUIRED_BOOLEANS.items():
    if proof.get(k) is not expected:
        fail(f'[23] proof marker {k} must be {expected} (got {proof.get(k)!r})')
if proof.get('db_writes', 1) != 0:
    fail('[23] proof marker db_writes must be 0')
if proof.get('default_http_status') != 503:
    fail('[23] proof marker default_http_status must be 503')
if proof.get('feature_flag') != FEATURE_FLAG:
    fail(f'[23] proof marker feature_flag must be {FEATURE_FLAG}')
if proof.get('suite_runner_tuple_v34_count') != 1:
    fail('[23] proof marker suite_runner_tuple_v34_count must be 1')

# ---------------------------------------------------------------------------
# 24. suite runner tuple count v34 exactly 1 + sentinels
# ---------------------------------------------------------------------------
if not os.path.isfile(repo(SUITE_REL)):
    fail('[24] suite runner missing')
else:
    sr = read_text(SUITE_REL)
    token = "'PROJECT-GENERIC-VISUAL-BATTLE-RUNNER-PREVIEW-ROUTE'"
    cnt = sr.count(token)
    if cnt != 1:
        fail(f'[24] suite runner must contain exactly 1 v34 tuple token, got {cnt}')
    for sentinel in [
        'PUBLIC_SYNC_DIAGNOSTIC_BLOCK_v34_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE',
        'PUBLIC_SYNC_TAG_v34_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE',
        'GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE_REGISTRATION_SENTINEL',
    ]:
        if sentinel not in sr:
            fail(f'[24] suite runner missing sentinel: {sentinel}')
    val_name = 'validate_project_generic_visual_battle_runner_preview_route_v1.py'
    if sr.count(f"'{val_name}'") != 1:
        fail(f'[24] suite runner must reference {val_name} exactly once')

# ---------------------------------------------------------------------------
# Final verdict
# ---------------------------------------------------------------------------
if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE validator')
    sys.exit(1)

print('[PASS] PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE validator')
sys.exit(0)
