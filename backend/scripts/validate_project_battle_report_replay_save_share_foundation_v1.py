#!/usr/bin/env python3
"""
PROJECT_BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION validator (statico, OPTIONAL).

Asserisce:
  - file frontend required esistono
  - PostBattleSummary contiene labels Replay/Salva/Condividi e handlers
  - proof marker safety booleans corretti
  - MD5 invarianti sui 5 file protetti intatti
  - battle_engine.py non modificato
  - nessuna nuova backend route per replay/save/share
  - Replay/Save/Share frontend NON contengono stringhe forbidden:
      grant_reward, claim_reward, hero_exp +=, /api/battle/simulate
  - suite runner ha esattamente UNA tupla per questo pack
  - sync sentinel + registration sentinel presenti

Exit 0 su PASS, 1 su FAIL. Registrazione OPTIONAL.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path('/app')

FRONTEND_REQUIRED = [
    ROOT / 'frontend/components/battle/battleReplayTypes.ts',
    ROOT / 'frontend/components/battle/BattleReplayPreview.tsx',
    ROOT / 'frontend/utils/buildBattleReplaySnapshot.ts',
    ROOT / 'frontend/utils/battleReplayStorage.ts',
    ROOT / 'frontend/utils/battleShareText.ts',
    ROOT / 'frontend/components/battle/PostBattleSummary.tsx',
]

DESIGN_JSON = ROOT / 'data/design/battle_report_replay_share/battle_report_replay_save_share_foundation_v1.json'
PROOF_MARKER = ROOT / 'data/design/battle_report_replay_share/battle_report_replay_save_share_proof_marker_v1.json'
DOC_MAIN = ROOT / 'docs/divine/211_BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION.md'
SUITE_RUNNER = ROOT / 'backend/scripts/run_hero_skill_kit_validator_suite.py'

MD5_INVARIANTS = {
    'backend/battle_engine.py':    '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env':                'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx':        '45fcc9890b6b128c37088bc33aa54caf',
}

# Stringhe FORBIDDEN nei file replay/save/share frontend:
FORBIDDEN_STRINGS_IN_REPLAY_FILES = [
    'grant_reward', 'claim_reward', 'hero_exp +=', '/api/battle/simulate',
]


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    # 1) MD5 invariants
    for rel, exp in MD5_INVARIANTS.items():
        p = ROOT / rel
        if not p.exists():
            fail(f'missing MD5-protected file: {rel}')
        h = hashlib.md5(p.read_bytes()).hexdigest()
        if h != exp:
            fail(f'MD5 mismatch on {rel}: expected={exp} actual={h}')

    # 2) Frontend files exist
    for p in FRONTEND_REQUIRED:
        if not p.exists():
            fail(f'missing frontend file: {p}')

    # 3) Design JSON
    if not DESIGN_JSON.exists():
        fail(f'missing design JSON: {DESIGN_JSON}')
    design = json.loads(DESIGN_JSON.read_text())
    if design.get('task_id') != 'PROJECT_BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION':
        fail(f'design JSON wrong task_id: {design.get("task_id")!r}')
    if design.get('runtime_mode') != 'PREVIEW_ONLY':
        fail('design JSON runtime_mode must be PREVIEW_ONLY')
    if design.get('db_writes') != 0:
        fail(f'design JSON db_writes must be 0, got {design.get("db_writes")}')
    if design.get('backend_routes_added'):
        fail('design JSON backend_routes_added must be empty')

    # 4) Proof marker safety booleans
    if not PROOF_MARKER.exists():
        fail(f'missing proof marker: {PROOF_MARKER}')
    marker = json.loads(PROOF_MARKER.read_text())
    required_true = [
        'replay_visual_only', 'no_rng_rerun', 'no_reward_duplication',
        'no_exp_duplication', 'no_item_grant', 'no_db_writes',
        'save_local_only', 'share_text_only',
    ]
    for k in required_true:
        if marker.get(k) is not True:
            fail(f'marker {k} must be true')
    if marker.get('server_replay_storage') is not False:
        fail('marker server_replay_storage must be false')
    expected_verdict = 'PROJECT_BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION_PREVIEW_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
    if marker.get('verdict') != expected_verdict:
        fail(f'marker verdict mismatch: expected {expected_verdict}, got {marker.get("verdict")!r}')

    # 5) PostBattleSummary contains required labels/handlers
    pbs = (ROOT / 'frontend/components/battle/PostBattleSummary.tsx').read_text()
    for needed in [
        'BattleReplayPreview',
        'buildBattleReplaySnapshot',
        'saveBattleReplay',
        'buildBattleShareText',
        'REPLAY',
        'SALVA',
        'CONDIVIDI',
        'handleOpenReplay',
        'handleSave',
        'handleShare',
    ]:
        if needed not in pbs:
            fail(f'PostBattleSummary.tsx missing required token: {needed!r}')
    # PostBattleSummary deve NON chiamare simulate dal replay path
    if '/api/battle/simulate' in pbs:
        fail('PostBattleSummary.tsx must NOT reference /api/battle/simulate')

    # 6) Replay/Save/Share frontend files must NOT contain forbidden strings
    for p in [
        ROOT / 'frontend/components/battle/BattleReplayPreview.tsx',
        ROOT / 'frontend/utils/buildBattleReplaySnapshot.ts',
        ROOT / 'frontend/utils/battleReplayStorage.ts',
        ROOT / 'frontend/utils/battleShareText.ts',
    ]:
        src = p.read_text()
        for forbidden in FORBIDDEN_STRINGS_IN_REPLAY_FILES:
            if forbidden in src:
                fail(f'{p.name} contains forbidden string: {forbidden!r}')

    # 7) Replay preview specifics
    replay_src = (ROOT / 'frontend/components/battle/BattleReplayPreview.tsx').read_text()
    for needed in ['REPLAY VISIVO', 'NESSUNA RICOMPENSA', 'NESSUN EXP', 'VISIVO-ONLY',
                   'BattleReplaySnapshotV1']:
        if needed not in replay_src:
            fail(f'BattleReplayPreview missing required token: {needed!r}')

    # 8) Storage helper specifics
    storage_src = (ROOT / 'frontend/utils/battleReplayStorage.ts').read_text()
    for needed in ['AsyncStorage', 'BATTLE_REPLAY_STORAGE_KEY',
                   'BATTLE_REPLAY_MAX_LOCAL', 'local_only', 'server_synced',
                   'rewards_disabled', 'exp_disabled', 'grants_disabled', 'no_rng_rerun']:
        if needed not in storage_src:
            fail(f'battleReplayStorage.ts missing required token: {needed!r}')
    # Must NOT call any backend / fetch
    for forbidden in ['fetch(', "axios.", '/api/']:
        if forbidden in storage_src:
            fail(f'battleReplayStorage.ts must NOT make backend calls: {forbidden!r}')

    # 9) Share helper specifics
    share_src = (ROOT / 'frontend/utils/battleShareText.ts').read_text()
    if 'Divine Waifus' not in share_src:
        fail('battleShareText.ts must build Divine Waifus prefixed string')
    for forbidden in ['http://', 'https://', '/api/']:
        if forbidden in share_src:
            fail(f'battleShareText.ts must NOT include URL: {forbidden!r}')

    # 10) Suite runner contains tuple exactly once + sentinels
    suite_src = SUITE_RUNNER.read_text()
    tuple_str = "('PROJECT-BATTLE-REPORT-REPLAY-SAVE-SHARE-FOUNDATION'"
    count = suite_src.count(tuple_str)
    if count != 1:
        fail(f'suite runner must have exactly 1 tuple, found {count}')
    if 'PUBLIC_SYNC_TAG_v26_BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION' not in suite_src:
        fail('suite runner missing PUBLIC_SYNC_TAG_v26 sentinel')
    if 'BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION_REGISTRATION_SENTINEL' not in suite_src:
        fail('suite runner missing REGISTRATION_SENTINEL')

    # 11) NO new backend route file added with name suggesting replay/save/share
    routes_dir = ROOT / 'backend/routes'
    for f in routes_dir.iterdir():
        n = f.name.lower()
        if 'replay' in n or 'battle_share' in n or 'battle_save' in n:
            fail(f'forbidden new backend route file: {f.name}')

    # 12) Doc main exists
    if not DOC_MAIN.exists():
        fail(f'missing doc: {DOC_MAIN}')

    print('[PASS] PROJECT_BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION master validator')


if __name__ == '__main__':
    main()
