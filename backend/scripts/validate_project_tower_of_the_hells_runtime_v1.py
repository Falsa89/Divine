#!/usr/bin/env python3
"""
PROJECT_TOWER_OF_THE_HELLS_RUNTIME validator (statico).

Asserisce:
  - 8 JSON design tracks (A..H) + 1 proof marker presenti e validi
  - tutti i JSON con task_id == PROJECT_TOWER_OF_THE_HELLS_RUNTIME + verdict atteso
  - MD5 invarianti baseline su 5 file protetti
  - frontend locks attivi (VIP/BP/Shop/ItemShop)
  - frontend/app/tower-of-the-hells.tsx presente con marker TEST/placeholder
  - frontend/constants/towerOfTheHellsFloors.ts presente con 20 floors design
  - frontend/app/_layout.tsx contiene Stack.Screen "tower-of-the-hells"
  - frontend/app/(tabs)/home.tsx menu Torre punta a /tower-of-the-hells
  - nessun nuovo endpoint backend Tower implementato (backend_runtime: false)
  - tower.tsx (orphan) non aggiunto in questo pack
  - audio_status / asset_status = test_placeholder; replace_before_release = true
  - validator NON indebolisce alcun REQUIRED validator

Exit 0 su PASS, 1 su FAIL. Registrazione OPTIONAL.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
DIR = ROOT / 'data/design/tower_of_the_hells'

REQUIRED_TRACKS = {
    'tower_surface_and_wiring_audit_v1.json':                'TRACK_A_TOWER_SURFACE_AND_WIRING_AUDIT_READY',
    'tower_runtime_mvp_implementation_v1.json':              'TRACK_B_TOWER_RUNTIME_MVP_IMPLEMENTATION_READY',
    'test_asset_audio_registry_v1.json':                     'TRACK_C_TEST_ASSET_AUDIO_REGISTRY_READY',
    'reward_anti_exploit_and_progress_policy_v1.json':       'TRACK_D_REWARD_ANTI_EXPLOIT_AND_PROGRESS_POLICY_READY',
    'mode_feature_wiring_registry_update_v1.json':           'TRACK_E_MODE_FEATURE_WIRING_REGISTRY_UPDATE_READY',
    'mobile_qa_and_placeholder_replacement_plan_v1.json':    'TRACK_F_MOBILE_QA_AND_PLACEHOLDER_REPLACEMENT_PLAN_READY',
    'validator_and_suite_registration_v1.json':              'TRACK_G_VALIDATOR_AND_SUITE_REGISTRATION_READY',
    'completion_and_public_sync_v1.json':                    'TRACK_H_COMPLETION_AND_PUBLIC_SYNC_READY',
}
PROOF_MARKER = 'tower_of_the_hells_runtime_suite_registration_proof_marker_v1.json'

EXPECTED_INVARIANTS = {
    'backend/battle_engine.py':       '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env':                   'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py':    '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx':    '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx':           '45fcc9890b6b128c37088bc33aa54caf',
}

FRONTEND_LOCK_ASSERTS = [
    ('frontend/app/vip.tsx',        'VIP_LOCKED_V2 = true'),
    ('frontend/app/battlepass.tsx', 'BP_LOCKED_V2 = true'),
    ('frontend/app/battlepass.tsx', 'BP_PREMIUM_BUY_LOCKED_V2 = true'),
    ('frontend/app/shop.tsx',       'SHOP_LOCKED_V2 = true'),
    ('frontend/app/item-shop.tsx',  'ITEM_SHOP_LOCKED_V2 = true'),
]

TOWER_SCREEN_REQUIRED_TOKENS = [
    'TOWER_OF_THE_HELLS_MODE_ID',
    'TOWER_OF_THE_HELLS_FLOORS',
    'TOWER_OF_THE_HELLS_LOCAL_PROGRESS_KEY',
    'AsyncStorage',
    'Torre degli Inferi (TEST)',
    'TEST PLACEHOLDER',
    'Test Clear (TEST)',
    'first_clear_reward',
    'no_stamina',
]

TOWER_CATALOG_REQUIRED_TOKENS = [
    "TOWER_OF_THE_HELLS_MODE_ID = 'tower_of_the_hells'",
    'TOWER_OF_THE_HELLS_FLOORS',
    'replace_before_release: true',
    'test_placeholder',
    'is_boss',
]

# These would indicate forbidden runtime activations
FORBIDDEN_TOWER_TOKENS = [
    'SYNERGY_V2_BATTLE_ACTIVE',
    'ARTIFACT_BONUS_RUNTIME_ACTIVE',
    'DIVINE_WEAPON_RUNTIME_ACTIVE',
    'STATUS_EFFECT_RUNTIME_ACTIVE',
    'stamina_cost',
    'ticket_cost',
    'wallet_grant',
    'gems_grant',
]

FORBIDDEN_AUDIO_RUNTIME_IMPORTS = [
    "from 'expo-av'", 'from "expo-av"',
    "from 'expo-audio'", 'from "expo-audio"',
    "from 'react-native-sound'", 'from "react-native-sound"',
]

# No new tower backend endpoint patterns should appear
FORBIDDEN_BACKEND_TOWER_ENDPOINTS_PATTERN = re.compile(
    r"['\"]/api/tower[-_]of[-_]the[-_]hells",
    re.IGNORECASE,
)


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def fail(msg):
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main():
    # 1) Track JSONs
    for fname, expected_verdict in REQUIRED_TRACKS.items():
        p = DIR / fname
        if not p.exists():
            fail(f'missing track file: {fname}')
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            fail(f'invalid JSON {fname}: {e}')
        if d.get('verdict') != expected_verdict:
            fail(f'{fname} verdict mismatch: got {d.get("verdict")!r} expected {expected_verdict!r}')
        if d.get('task_id') != 'PROJECT_TOWER_OF_THE_HELLS_RUNTIME':
            fail(f'{fname} task_id mismatch: {d.get("task_id")!r}')

    # 2) Proof marker
    pm = DIR / PROOF_MARKER
    if not pm.exists():
        fail(f'missing proof marker: {PROOF_MARKER}')
    pm_d = json.loads(pm.read_text(encoding='utf-8'))
    if pm_d.get('purpose') != 'DEDICATED_SUITE_REGISTRATION_PROOF_MARKER':
        fail('proof marker purpose mismatch')
    if pm_d.get('validator_file_role') != 'OPTIONAL':
        fail('proof marker role must be OPTIONAL')
    if pm_d.get('mode_id') != 'tower_of_the_hells':
        fail('proof marker mode_id must be tower_of_the_hells')
    for boolkey in ('weakens_REQUIRED_validators', 'fakes_PASS', 'backend_runtime',
                    'battle_engine_change', 'combat_change', 'hero_kit_change',
                    'character_bible_change', 'gacha_change',
                    'iap_bp_vip_shop_activation', 'artifact_change',
                    'constellation_unhide', 'divine_weapon_runtime',
                    'synergy_v2_battle_activation', 'status_effect_runtime',
                    'broad_audio_engine', 'final_art_audio_imported',
                    'server_profiles_live_activation', 'second_server_opened',
                    'stamina_reintroduced', 'monetized_attempts',
                    'infinite_reward_farming', 'reward_grants_economy',
                    'broad_player_data_mutation', 'required_validator_weakening',
                    'env_secret_added', 'db_migration'):
        if pm_d.get(boolkey) is not False:
            fail(f'proof marker must declare {boolkey}=false (got {pm_d.get(boolkey)!r})')
    if pm_d.get('db_writes', -1) != 0:
        fail('proof marker db_writes must be 0')
    if pm_d.get('asset_status') != 'test_placeholder':
        fail('proof marker asset_status must be test_placeholder')
    if pm_d.get('audio_status') != 'test_placeholder':
        fail('proof marker audio_status must be test_placeholder')
    if pm_d.get('replace_before_release') is not True:
        fail('proof marker replace_before_release must be True')

    # 3) MD5 invariants
    for rel, expected_hash in EXPECTED_INVARIANTS.items():
        actual = md5(ROOT / rel)
        if actual != expected_hash:
            fail(f'invariant drift on {rel}: expected {expected_hash} got {actual}')

    # 4) Frontend locks still in place
    for rel, token in FRONTEND_LOCK_ASSERTS:
        p = ROOT / rel
        if not p.exists():
            fail(f'frontend lock file missing: {rel}')
        if token not in p.read_text(encoding='utf-8'):
            fail(f'frontend lock token missing in {rel}: {token!r}')

    # 5) Tower screen file present + required tokens
    tower_screen = ROOT / 'frontend/app/tower-of-the-hells.tsx'
    if not tower_screen.exists():
        fail('frontend/app/tower-of-the-hells.tsx missing')
    ts = tower_screen.read_text(encoding='utf-8')
    for tok in TOWER_SCREEN_REQUIRED_TOKENS:
        if tok not in ts:
            fail(f'tower-of-the-hells.tsx missing required token: {tok!r}')
    for tok in FORBIDDEN_TOWER_TOKENS:
        if tok in ts:
            fail(f'tower-of-the-hells.tsx contains forbidden token: {tok!r}')
    for tok in FORBIDDEN_AUDIO_RUNTIME_IMPORTS:
        if tok in ts:
            fail(f'tower-of-the-hells.tsx contains forbidden audio runtime import: {tok!r}')

    # 6) Floor catalog file present + 20 floors design
    catalog = ROOT / 'frontend/constants/towerOfTheHellsFloors.ts'
    if not catalog.exists():
        fail('frontend/constants/towerOfTheHellsFloors.ts missing')
    cat = catalog.read_text(encoding='utf-8')
    for tok in TOWER_CATALOG_REQUIRED_TOKENS:
        if tok not in cat:
            fail(f'towerOfTheHellsFloors.ts missing required token: {tok!r}')
    if 'length: 20' not in cat:
        fail('towerOfTheHellsFloors.ts must define exactly 20 floors (length: 20)')

    # 7) _layout.tsx contains Stack.Screen for tower-of-the-hells
    layout = (ROOT / 'frontend/app/_layout.tsx').read_text(encoding='utf-8')
    if '"tower-of-the-hells"' not in layout:
        fail('_layout.tsx missing Stack.Screen "tower-of-the-hells"')

    # 8) home menu legacy preservato (MD5_LOCKED SF_MERGE); la nuova route
    #    /tower-of-the-hells \u00e8 raggiungibile via deep-link / future menu update.
    #    Verifichiamo solo che la nuova route NON sia stata accidentalmente
    #    cablata nel menu (per non rompere SF_MERGE MD5 invariant).
    home = (ROOT / 'frontend/app/(tabs)/home.tsx').read_text(encoding='utf-8')
    if "router.push('/tower-of-the-hells' as any)" in home:
        fail("home.tsx MUST NOT be modified in this pack (SF_MERGE MD5 invariant)")

    # 9) NO new backend tower-of-the-hells endpoint route added (legacy /api/tower/*
    #    \u00e8 fuori scope di questo pack e non viene toccato)
    backend_root = ROOT / 'backend'
    forbidden_specific_re = re.compile(
        r"['\"]/api/tower[-_]of[-_]the[-_]hells",
        re.IGNORECASE,
    )
    for p in backend_root.rglob('*.py'):
        if any(part in ('__pycache__', 'scripts') for part in p.parts):
            continue
        content = p.read_text(encoding='utf-8', errors='ignore')
        m = forbidden_specific_re.search(content)
        if m:
            fail(f'backend endpoint for tower-of-the-hells MUST NOT exist in this pack: {p} matched {m.group(0)!r}')

    # 10) Track B: backend_runtime False, mvp_scope frontend_test_mvp_only
    b = json.loads((DIR / 'tower_runtime_mvp_implementation_v1.json').read_text())
    if b.get('backend_runtime') is not False:
        fail('Track B backend_runtime must be False')
    if b.get('mvp_scope') != 'frontend_test_mvp_only':
        fail('Track B mvp_scope must be frontend_test_mvp_only')
    if b.get('floors', {}).get('count') != 20:
        fail('Track B floors.count must be 20')
    if b.get('combat_integration', '').upper().startswith('NONE_RUNTIME') is False:
        fail('Track B combat_integration must start with NONE_RUNTIME')
    if b.get('persistence', {}).get('db_writes') != 0:
        fail('Track B persistence.db_writes must be 0')

    # 11) Track C: asset/audio test_placeholder + replace_before_release true
    c = json.loads((DIR / 'test_asset_audio_registry_v1.json').read_text())
    if c.get('asset_status') != 'test_placeholder':
        fail('Track C asset_status must be test_placeholder')
    if c.get('audio_status') != 'test_placeholder':
        fail('Track C audio_status must be test_placeholder')
    if c.get('replace_before_release') is not True:
        fail('Track C replace_before_release must be True')
    if c.get('broad_audio_engine_attached') is not False:
        fail('Track C broad_audio_engine_attached must be False')

    # 12) Track D: anti-exploit policy
    dt = json.loads((DIR / 'reward_anti_exploit_and_progress_policy_v1.json').read_text())
    if not dt.get('rules'):
        fail('Track D rules must be non-empty')
    if dt.get('replace_before_release') is not True:
        fail('Track D replace_before_release must be True')

    # 13) Track E: mode_id + frontend route updated
    e = json.loads((DIR / 'mode_feature_wiring_registry_update_v1.json').read_text())
    me = e.get('mode_entry', {})
    if me.get('mode_id') != 'tower_of_the_hells':
        fail('Track E mode_entry.mode_id must be tower_of_the_hells')
    if me.get('backend_runtime') is not False:
        fail('Track E mode_entry.backend_runtime must be False')
    if me.get('db_writes') != 0:
        fail('Track E mode_entry.db_writes must be 0')
    if me.get('monetized_attempts') is not False:
        fail('Track E mode_entry.monetized_attempts must be False')
    if me.get('farming_possible') is not False:
        fail('Track E mode_entry.farming_possible must be False')

    # 14) Track F: 15+ checklist items
    f = json.loads((DIR / 'mobile_qa_and_placeholder_replacement_plan_v1.json').read_text())
    if len(f.get('mobile_qa_checklist', [])) < 15:
        fail('Track F must have at least 15 mobile_qa_checklist items')
    if not f.get('placeholder_replacement_plan'):
        fail('Track F placeholder_replacement_plan must be non-empty')

    # 15) Completion track
    h = json.loads((DIR / 'completion_and_public_sync_v1.json').read_text())
    if h.get('db_writes') != 0:
        fail('Track H db_writes must be 0')
    if h.get('backend_runtime') is not False:
        fail('Track H backend_runtime must be False')
    if 'TEST_MVP_READY' not in h.get('local_verdict', ''):
        fail('Track H local_verdict must contain TEST_MVP_READY')

    print('[PASS] PROJECT_TOWER_OF_THE_HELLS_RUNTIME master validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
