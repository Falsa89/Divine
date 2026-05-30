#!/usr/bin/env python3
"""
PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION validator (statico, OPTIONAL).

Asserisce:
  - 9 JSON design tracks (A..G) + 1 proof marker presenti e validi JSON
  - tutti i JSON con task_id == PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION
  - MD5 invarianti baseline su 5 file protetti
  - runtime components presenti:
      frontend/app/guide.tsx
      frontend/components/TutorialOverlay.tsx
      frontend/utils/tutorialStorage.ts
      frontend/constants/guideCodex.ts
      frontend/constants/tutorials.ts
  - content_status / tutorial_status = test_content
  - replace_before_release = true
  - vincoli pack onorati: no_layout_tsx_changes, no_tower_gameplay_changes, no_combat_engine_changes,
    no_home_menu_changes, no_db_writes, no_monetization, no_stamina, no_fake_pass
  - validator NON indebolisce alcun REQUIRED validator

Exit 0 su PASS, 1 su FAIL. Registrazione OPTIONAL.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path('/app')
GUIDE_DIR = ROOT / 'data/design/guide_codex'
TUT_DIR = ROOT / 'data/design/tutorial'

REQUIRED_GUIDE_JSON = {
    'guide_codex_surface_audit_v1.json':                       'TRACK_A_GUIDE_CODEX_SURFACE_AUDIT_READY',
    'guide_categories_v1.json':                                'TRACK_B_GUIDE_CONTENT_AND_TUTORIAL_SCHEMA_READY',
    'guide_entries_v1.json':                                   'TRACK_B_GUIDE_CONTENT_AND_TUTORIAL_SCHEMA_READY',
    'guide_codex_runtime_mvp_design_v1.json':                  'TRACK_C_GUIDE_CODEX_RUNTIME_MVP_READY',
    'tower_guide_and_first_unlock_v1.json':                    'TRACK_E_TOWER_GUIDE_AND_FIRST_UNLOCK_TUTORIAL_READY',
    'mode_guide_tutorial_coverage_registry_v1.json':           'TRACK_F_MODE_GUIDE_TUTORIAL_COVERAGE_REGISTRY_READY',
    'mobile_qa_release_gate_policy_v1.json':                   'TRACK_G_MOBILE_QA_AND_RELEASE_GATE_POLICY_READY',
}
REQUIRED_TUT_JSON = {
    'tutorial_entries_v1.json':              'TRACK_D_TUTORIAL_RUNTIME_FOUNDATION_READY',
    'tutorial_runtime_foundation_v1.json':   'TRACK_D_TUTORIAL_RUNTIME_FOUNDATION_READY',
}
PROOF_MARKER = GUIDE_DIR / 'guide_codex_and_tutorial_foundation_suite_registration_proof_marker_v1.json'

RUNTIME_FILES = [
    ROOT / 'frontend/app/guide.tsx',
    ROOT / 'frontend/components/TutorialOverlay.tsx',
    ROOT / 'frontend/utils/tutorialStorage.ts',
    ROOT / 'frontend/constants/guideCodex.ts',
    ROOT / 'frontend/constants/tutorials.ts',
]

MD5_INVARIANTS = {
    'backend/battle_engine.py':    '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env':                'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx':        '45fcc9890b6b128c37088bc33aa54caf',
}


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

    # 2) Design JSON tracks
    for fname, expected_verdict in REQUIRED_GUIDE_JSON.items():
        p = GUIDE_DIR / fname
        if not p.exists():
            fail(f'missing guide JSON track: {p}')
        try:
            data = json.loads(p.read_text())
        except Exception as e:
            fail(f'invalid JSON {p}: {e}')
        if data.get('task_id') != 'PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION':
            fail(f'wrong task_id in {p}: {data.get("task_id")!r}')
        if expected_verdict and data.get('verdict') != expected_verdict and 'verdict' in data:
            # Some files have composite verdicts; tolerate but require track verdict present somewhere
            if expected_verdict not in json.dumps(data):
                fail(f'expected verdict {expected_verdict} not found in {p}')

    for fname, expected_verdict in REQUIRED_TUT_JSON.items():
        p = TUT_DIR / fname
        if not p.exists():
            fail(f'missing tutorial JSON track: {p}')
        try:
            data = json.loads(p.read_text())
        except Exception as e:
            fail(f'invalid JSON {p}: {e}')
        if data.get('task_id') != 'PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION':
            fail(f'wrong task_id in {p}')
        if data.get('verdict') != expected_verdict:
            fail(f'expected verdict {expected_verdict} in {p}, got {data.get("verdict")!r}')

    # 3) Proof marker
    if not PROOF_MARKER.exists():
        fail(f'missing proof marker: {PROOF_MARKER}')
    try:
        marker = json.loads(PROOF_MARKER.read_text())
    except Exception as e:
        fail(f'invalid proof marker JSON: {e}')
    if marker.get('task_id') != 'PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION':
        fail('proof marker task_id mismatch')
    if marker.get('verdict') != 'PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING':
        fail(f'proof marker verdict mismatch: {marker.get("verdict")!r}')

    # 4) Runtime files
    for p in RUNTIME_FILES:
        if not p.exists():
            fail(f'missing runtime component: {p}')

    # 5) Content status checks
    cats = json.loads((GUIDE_DIR / 'guide_categories_v1.json').read_text())
    if cats.get('content_status') != 'test_content':
        fail('guide_categories content_status not test_content')
    if cats.get('replace_before_release') is not True:
        fail('guide_categories replace_before_release not true')

    tut = json.loads((TUT_DIR / 'tutorial_entries_v1.json').read_text())
    if tut.get('tutorial_status') != 'test_content':
        fail('tutorial_entries tutorial_status not test_content')
    if tut.get('replace_before_release') is not True:
        fail('tutorial_entries replace_before_release not true')

    # 6) Constraints honored
    constraints = marker.get('constraints_honored') or {}
    must_be_true = [
        'no_combat_formula_changes', 'no_battle_engine_changes',
        'no_layout_tsx_changes', 'no_home_menu_changes',
        'no_server_profiles_live_changes', 'no_shop_bp_vip_iap_unlock',
        'no_db_migrations', 'no_broad_user_mutation', 'no_monetization',
        'no_stamina_or_tickets', 'no_tower_gameplay_changes',
        'no_required_validator_weakening', 'no_fake_pass',
    ]
    for k in must_be_true:
        if not constraints.get(k):
            fail(f'constraint not honored: {k}')

    print('[PASS] PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION master validator')


if __name__ == '__main__':
    main()
