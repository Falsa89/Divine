#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator: PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT_PACK (v33)
Phase: PHASE_3 sister
Mode:  DESIGN_CONTRACT_AUDIT_ONLY

Asserisce 19 punti richiesti dal prompt del pack:
  1. tutti i file JSON/doc richiesti esistono;
  2. il generic runner contract dichiara runtime_activation = false;
  3. /combat resta direct/dev/QA e unchanged (contract field);
  4. payload schema include tutti i required_fields;
  5. adapter matrix include tutte le mode richieste;
  6. ogni mode ha can_grant_rewards_in_runner = false;
  7. result commit contract: runner non committa reward/EXP/progress;
  8. replay view contract: replay/view non concede mai reward;
  9. registry v5 marca direct_visual_combat_route contract-ready runtime-pending;
 10. registry v5 preserva Guild War come unica eccezione auto-resolve con replay/view link;
 11. frontend/app/combat.tsx contiene ancora /api/battle/simulate;
 12. frontend/app/story.tsx contiene ancora /api/story/battle;
 13. frontend/app/story-visual-battle-sandbox.tsx esiste;
 14. frontend/constants/homeAssetsManifest.ts mantiene Home Play/Battle a /story;
 15. backend/battle_engine.py invariato (file presente, non rewritten in questo pack);
 16. nessuna nuova rotta backend aggiunta (no backend/routes/visual_battle_runner*.py);
 17. nessun DB write token introdotto nei contract design (db_writes=0 e marker booleans);
 18. proof marker booleans corretti;
 19. suite runner contiene esattamente UNA tupla locale v33.
"""
from __future__ import annotations
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

REQUIRED_FILES = [
    'data/design/visual_battle_runner/generic_visual_battle_runner_contract_v1.json',
    'data/design/visual_battle_runner/visual_battle_runner_payload_schema_v1.json',
    'data/design/visual_battle_runner/visual_battle_runner_mode_adapter_matrix_v1.json',
    'data/design/visual_battle_runner/visual_battle_runner_result_commit_contract_v1.json',
    'data/design/visual_battle_runner/visual_battle_runner_replay_view_contract_v1.json',
    'data/design/visual_battle_runner/generic_visual_battle_runner_contract_proof_marker_v1.json',
    'data/design/battle_entrypoints/battle_entrypoint_registry_v5.json',
    'docs/divine/231_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT.md',
    'backend/scripts/validate_project_generic_visual_battle_runner_contract_v1.py',
]

REQUIRED_PAYLOAD_FIELDS = [
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

REQUIRED_MODES = [
    'story',
    'story_sandbox',
    'direct_qa_combat',
    'guild_war_replay',
    'tower',
    'raid',
    'material_raid',
    'boss',
    'event_battle',
    'trial',
    'pvp',
]

PROOF_REQUIRED_BOOLEANS = {
    'generic_runner_contract_defined': True,
    'generic_runner_runtime_changed': False,
    'combat_tsx_changed': False,
    'story_tsx_changed': False,
    'story_sandbox_changed': False,
    'home_routes_changed': False,
    'backend_routes_changed': False,
    'battle_engine_changed': False,
    'story_battle_endpoint_changed': False,
    'battle_simulate_endpoint_changed': False,
    'reward_logic_changed': False,
    'exp_logic_changed': False,
    'story_progress_logic_changed': False,
    'economy_changed': False,
    'gacha_changed': False,
    'material_raid_changed': False,
    'gem_socket_changed': False,
    'rune_runtime_changed': False,
    'artifact_runtime_changed': False,
    'divine_weapon_runtime_changed': False,
    'guild_war_runtime_changed': False,
    'runner_never_grants_rewards': True,
    'replay_view_never_grants_rewards': True,
    'sandbox_never_grants_rewards': True,
}

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def repo(path: str) -> str:
    return os.path.join(REPO_ROOT, path)


def load_json(rel: str) -> dict:
    with open(repo(rel), 'r', encoding='utf-8') as fh:
        return json.load(fh)


def read_text(rel: str) -> str:
    with open(repo(rel), 'r', encoding='utf-8') as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# 1. required files exist
# ---------------------------------------------------------------------------
for rel in REQUIRED_FILES:
    if not os.path.isfile(repo(rel)):
        fail(f'[1] missing required file: {rel}')

if FAILURES:
    # senza i file base non ha senso proseguire
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT validator')
    sys.exit(1)

# ---------------------------------------------------------------------------
# 2. generic runner contract: runtime_activation == false
# ---------------------------------------------------------------------------
contract = load_json('data/design/visual_battle_runner/generic_visual_battle_runner_contract_v1.json')
if contract.get('runtime_activation') is not False:
    fail('[2] generic runner contract runtime_activation must be False')
if contract.get('runtime_changed_this_pack') is not False:
    fail('[2] generic runner contract runtime_changed_this_pack must be False')
if contract.get('db_writes', 1) != 0:
    fail('[2] generic runner contract db_writes must be 0')

# ---------------------------------------------------------------------------
# 3. /combat remains direct/dev/QA and unchanged
# ---------------------------------------------------------------------------
cs = contract.get('current_state', {}).get('combat_route', {})
if cs.get('changed_in_this_pack') is not False:
    fail('[3] contract: combat_route.changed_in_this_pack must be False')
if cs.get('refactored_in_this_pack') is not False:
    fail('[3] contract: combat_route.refactored_in_this_pack must be False')
if 'direct' not in (cs.get('role') or '').lower():
    fail('[3] contract: combat_route.role must mention direct/dev/QA')
if cs.get('calls_endpoint_on_mount') != '/api/battle/simulate':
    fail('[3] contract: combat_route.calls_endpoint_on_mount must be /api/battle/simulate')

# ---------------------------------------------------------------------------
# 4. payload schema contains all required fields
# ---------------------------------------------------------------------------
payload = load_json('data/design/visual_battle_runner/visual_battle_runner_payload_schema_v1.json')
declared_required = set(payload.get('required_fields', []))
fields_dict = payload.get('fields', {}) or {}
for f in REQUIRED_PAYLOAD_FIELDS:
    if f not in declared_required:
        fail(f'[4] payload schema missing required_fields entry: {f}')
    if f not in fields_dict:
        fail(f'[4] payload schema missing fields.{f} definition')

if payload.get('runtime_activation') is not False:
    fail('[4] payload schema runtime_activation must be False')

# ---------------------------------------------------------------------------
# 5+6. adapter matrix
# ---------------------------------------------------------------------------
matrix = load_json('data/design/visual_battle_runner/visual_battle_runner_mode_adapter_matrix_v1.json')
adapters = matrix.get('adapters', {}) or {}
for m in REQUIRED_MODES:
    if m not in adapters:
        fail(f'[5] adapter matrix missing mode: {m}')
        continue
    a = adapters[m]
    if a.get('runtime_changed_this_pack') is not False:
        fail(f'[6] adapter {m}: runtime_changed_this_pack must be False')
    if a.get('can_grant_rewards_in_runner') is not False:
        fail(f'[6] adapter {m}: can_grant_rewards_in_runner must be False')
    if a.get('can_advance_progress_in_runner') is not False:
        fail(f'[6] adapter {m}: can_advance_progress_in_runner must be False')

if matrix.get('runtime_activation') is not False:
    fail('[5] adapter matrix runtime_activation must be False')
if matrix.get('all_adapters_runtime_changed_this_pack') is not False:
    fail('[5] adapter matrix all_adapters_runtime_changed_this_pack must be False')

# ---------------------------------------------------------------------------
# 7. result commit contract
# ---------------------------------------------------------------------------
rcc = load_json('data/design/visual_battle_runner/visual_battle_runner_result_commit_contract_v1.json')
rcc_inv = rcc.get('invariants', {}) or {}
for key in [
    'runner_commits_results',
    'runner_commits_rewards',
    'runner_commits_exp',
    'runner_commits_story_progress',
    'runner_commits_daily_progress',
    'runner_commits_quest_progress',
    'runner_commits_achievement_progress',
    'runner_writes_to_db',
    'runner_consumes_stamina',
    'runner_consumes_tickets',
    'replay_commits_anything',
    'sandbox_commits_anything',
    'qa_direct_commits_anything',
]:
    if rcc_inv.get(key) is not False:
        fail(f'[7] result commit contract invariant {key} must be False')

if rcc_inv.get('idempotency_key_required') is not True:
    fail('[7] result commit contract idempotency_key_required must be True')

# ---------------------------------------------------------------------------
# 8. replay view contract
# ---------------------------------------------------------------------------
rvc = load_json('data/design/visual_battle_runner/visual_battle_runner_replay_view_contract_v1.json')
rvc_inv = rvc.get('invariants', {}) or {}
for key in [
    'replay_view_grants_rewards',
    'replay_view_grants_exp',
    'replay_view_advances_story_progress',
    'replay_view_advances_daily_progress',
    'replay_view_advances_quest_progress',
    'replay_view_advances_achievement_progress',
    'replay_view_writes_to_db',
    'replay_view_reruns_battle',
    'guild_war_view_grants_rewards',
    'guild_war_view_advances_progress',
    'sandbox_preview_grants_rewards',
    'sandbox_preview_advances_progress',
    'qa_direct_grants_rewards',
    'qa_direct_advances_progress',
]:
    if rvc_inv.get(key) is not False:
        fail(f'[8] replay view contract invariant {key} must be False')

# ---------------------------------------------------------------------------
# 9+10. registry v5
# ---------------------------------------------------------------------------
reg5 = load_json('data/design/battle_entrypoints/battle_entrypoint_registry_v5.json')
if reg5.get('version') != 5:
    fail('[9] registry v5 version must be 5')
entries = reg5.get('entries', []) or []
by_feat = {e.get('feature'): e for e in entries}

dvcr = by_feat.get('direct_visual_combat_route')
if not dvcr:
    fail('[9] registry v5 missing direct_visual_combat_route entry')
else:
    if dvcr.get('contract_status') != 'generic_runner_contract_ready_runtime_pending':
        fail('[9] registry v5 direct_visual_combat_route.contract_status must be generic_runner_contract_ready_runtime_pending')
    if dvcr.get('runtime_changed_this_pack') is not False:
        fail('[9] registry v5 direct_visual_combat_route.runtime_changed_this_pack must be False')

gw = by_feat.get('guild_war')
if not gw:
    fail('[10] registry v5 missing guild_war entry')
else:
    if gw.get('is_only_autoresolve_exception') is not True:
        fail('[10] registry v5 guild_war.is_only_autoresolve_exception must be True')
    if gw.get('replay_link_required') is not True:
        fail('[10] registry v5 guild_war.replay_link_required must be True')
    if gw.get('replay_link_target_future') != '/battle-replay':
        fail('[10] registry v5 guild_war.replay_link_target_future must be /battle-replay')

# tutti gli altri modes visual-required tranne guild_war
non_visual_allowed_features = {'home_play', 'home_mode_battle_button', 'story_visual_battle_sandbox', 'guild_war'}
for e in entries:
    feat = e.get('feature')
    if feat in non_visual_allowed_features:
        continue
    desired = (e.get('desired_resolution_type') or '').lower()
    if 'visual_battle' not in desired and 'replay_view' not in desired:
        fail(f'[10] registry v5 entry {feat} must desire visual_battle (or replay_view): got {desired}')

global_policy = reg5.get('global_policy', {})
if global_policy.get('only_guild_war_can_autoresolve') is not True:
    fail('[10] registry v5 global_policy.only_guild_war_can_autoresolve must be True')
if global_policy.get('guild_war_requires_replay_link') is not True:
    fail('[10] registry v5 global_policy.guild_war_requires_replay_link must be True')
if global_policy.get('generic_visual_battle_runner_contract_ready') is not True:
    fail('[10] registry v5 global_policy.generic_visual_battle_runner_contract_ready must be True')
if global_policy.get('generic_visual_battle_runner_runtime_done') is not False:
    fail('[10] registry v5 global_policy.generic_visual_battle_runner_runtime_done must be False')

# ---------------------------------------------------------------------------
# 11. combat.tsx still calls /api/battle/simulate
# ---------------------------------------------------------------------------
combat_path = 'frontend/app/combat.tsx'
if not os.path.isfile(repo(combat_path)):
    fail('[11] frontend/app/combat.tsx missing')
else:
    if '/api/battle/simulate' not in read_text(combat_path):
        fail('[11] frontend/app/combat.tsx must still contain /api/battle/simulate')

# ---------------------------------------------------------------------------
# 12. story.tsx still calls /api/story/battle
# ---------------------------------------------------------------------------
story_path = 'frontend/app/story.tsx'
if not os.path.isfile(repo(story_path)):
    fail('[12] frontend/app/story.tsx missing')
else:
    if '/api/story/battle' not in read_text(story_path):
        fail('[12] frontend/app/story.tsx must still contain /api/story/battle')

# ---------------------------------------------------------------------------
# 13. story-visual-battle-sandbox.tsx exists
# ---------------------------------------------------------------------------
sandbox_path = 'frontend/app/story-visual-battle-sandbox.tsx'
if not os.path.isfile(repo(sandbox_path)):
    fail('[13] frontend/app/story-visual-battle-sandbox.tsx must exist')

# ---------------------------------------------------------------------------
# 14. homeAssetsManifest.ts keeps Play/Battle -> /story
# ---------------------------------------------------------------------------
hm_path = 'frontend/constants/homeAssetsManifest.ts'
if not os.path.isfile(repo(hm_path)):
    fail('[14] frontend/constants/homeAssetsManifest.ts missing')
else:
    hm = read_text(hm_path)
    if "play:" not in hm or "'/story'" not in hm:
        fail("[14] homeAssetsManifest.ts must keep play -> '/story'")
    if "battle:" not in hm:
        fail('[14] homeAssetsManifest.ts must have a battle route mapping')
    # entrambe le mappature attive devono puntare a /story (dentro HOME_ROUTES).
    # Le occorrenze nei commenti non contano: estraiamo solo il blocco
    # HOME_ROUTES = { ... } e poi togliamo i commenti `// ...`.
    import re
    block_match = re.search(r'HOME_ROUTES[^=]*=\s*\{([\s\S]*?)\};', hm)
    if not block_match:
        fail('[14] homeAssetsManifest.ts must declare HOME_ROUTES = { ... }')
    else:
        block = block_match.group(1)
        # rimuovi commenti single-line
        block_clean = re.sub(r'//[^\n]*', '', block)
        m_play = re.search(r"\bplay\s*:\s*'([^']+)'", block_clean)
        m_battle = re.search(r"\bbattle\s*:\s*'([^']+)'", block_clean)
        if not m_play or m_play.group(1) != '/story':
            fail(f"[14] HOME_ROUTES.play must map to /story (got {m_play.group(1) if m_play else None})")
        if not m_battle or m_battle.group(1) != '/story':
            fail(f"[14] HOME_ROUTES.battle must map to /story (got {m_battle.group(1) if m_battle else None})")

# ---------------------------------------------------------------------------
# 15. battle_engine.py present (invariato)
# ---------------------------------------------------------------------------
if not os.path.isfile(repo('backend/battle_engine.py')):
    fail('[15] backend/battle_engine.py must exist (MD5-locked, unchanged)')

# ---------------------------------------------------------------------------
# 16. no new backend route added by this pack
# ---------------------------------------------------------------------------
forbidden_new_routes = [
    'backend/routes/visual_battle_runner.py',
    'backend/routes/generic_visual_battle_runner.py',
    'backend/routes/visual_battle_runner_preview.py',
]
for rel in forbidden_new_routes:
    if os.path.isfile(repo(rel)):
        fail(f'[16] forbidden new backend route exists: {rel}')

# ---------------------------------------------------------------------------
# 17. no DB write tokens introduced in design files of this pack
#     (i contract elencano i token VIETATI in liste denominate, quindi
#      controlliamo solo i file di design "puri": registry v5, payload schema,
#      adapter matrix, generic contract, proof marker, doc 231.)
# ---------------------------------------------------------------------------
FORBIDDEN_DB_TOKENS = [
    'db.users.update_one',
    'db.user_heroes.update_one',
    'db.server_profiles.update_one',
    'db.story_progress.update_one',
    'db.quests.update_one',
    'db.daily.update_one',
    'db.achievements.update_one',
    '.insert_one(',
    '.update_many(',
    '.insert_many(',
    '.delete_one(',
    '.delete_many(',
]
design_pure_files = [
    'data/design/visual_battle_runner/generic_visual_battle_runner_contract_v1.json',
    'data/design/visual_battle_runner/visual_battle_runner_payload_schema_v1.json',
    'data/design/visual_battle_runner/visual_battle_runner_mode_adapter_matrix_v1.json',
    'data/design/visual_battle_runner/generic_visual_battle_runner_contract_proof_marker_v1.json',
    'data/design/battle_entrypoints/battle_entrypoint_registry_v5.json',
    'docs/divine/231_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT.md',
]
for rel in design_pure_files:
    text = read_text(rel)
    for tok in FORBIDDEN_DB_TOKENS:
        if tok in text:
            fail(f'[17] forbidden DB write token "{tok}" found in {rel}')

# ---------------------------------------------------------------------------
# 18. proof marker booleans
# ---------------------------------------------------------------------------
proof = load_json('data/design/visual_battle_runner/generic_visual_battle_runner_contract_proof_marker_v1.json')
for k, expected in PROOF_REQUIRED_BOOLEANS.items():
    if proof.get(k) is not expected:
        fail(f'[18] proof marker {k} must be {expected} (got {proof.get(k)!r})')
if proof.get('db_writes', 1) != 0:
    fail('[18] proof marker db_writes must be 0')
if proof.get('suite_runner_tuple_v33_count') != 1:
    fail('[18] proof marker suite_runner_tuple_v33_count must be 1')

# ---------------------------------------------------------------------------
# 19. suite runner contains exactly one v33 tuple
# ---------------------------------------------------------------------------
suite_path = 'backend/scripts/run_hero_skill_kit_validator_suite.py'
if not os.path.isfile(repo(suite_path)):
    fail('[19] suite runner missing')
else:
    sr = read_text(suite_path)
    tuple_token = "'PROJECT-GENERIC-VISUAL-BATTLE-RUNNER-CONTRACT'"
    cnt = sr.count(tuple_token)
    if cnt != 1:
        fail(f"[19] suite runner must contain exactly 1 v33 tuple token, got {cnt}")
    for sentinel in [
        'PUBLIC_SYNC_TAG_v33_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT',
        'GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT_REGISTRATION_SENTINEL',
        'PUBLIC_SYNC_DIAGNOSTIC_BLOCK_v33_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT',
    ]:
        if sentinel not in sr:
            fail(f'[19] suite runner missing sentinel: {sentinel}')
    val_name = 'validate_project_generic_visual_battle_runner_contract_v1.py'
    if sr.count(f"'{val_name}'") != 1:
        fail(f'[19] suite runner must reference {val_name} exactly once')

# ---------------------------------------------------------------------------
# Final verdict
# ---------------------------------------------------------------------------
if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT validator')
    sys.exit(1)

print('[PASS] PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_CONTRACT validator')
sys.exit(0)
