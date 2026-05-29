#!/usr/bin/env python3
"""
PROJECT_COMBAT_FINALIZE_FOR_RELEASE validator (statico, audit + finalize controllato).

Asserisce:
  - 7 JSON design tracks (A..G) + 1 proof marker presenti e validi
  - tutti i JSON hanno task_id == PROJECT_COMBAT_FINALIZE_FOR_RELEASE
  - verdict atteso per ciascun track
  - MD5 invarianti baseline su battle_engine.py / .env / routes/artifacts.py /
    battlepass.tsx / vip.tsx
  - frontend locks attivi (VIP/BP/Shop/ItemShop)
  - combat.tsx: regole canoniche compliant (3x3, facing, drawer, speed key)
  - BattleReport.tsx: shape compliant (allies/enemies/damage/healing/MVP)
  - PostBattleSummary.tsx: shape compliant (rewards/EXP/level_up)
  - buildPostBattleSummary.ts: shape compliant (mvp by damage_dealt)
  - audio runtime: nessun import expo-av/expo-audio/react-native-sound nel combat
    o nei componenti battle
  - audio placeholders (12 WAV + manifest) ancora presenti (intoccati dal pack 184)
  - battle_engine.py: no Synergy V2 battle activation, no artifact bonus runtime
  - validator NON indebolisce alcun REQUIRED validator

Exit 0 su PASS, 1 su FAIL. Registrazione OPTIONAL nel suite runner.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
DIR = ROOT / 'data/design/combat_finalize'

REQUIRED_TRACKS = {
    'combat_surface_audit_v1.json':                          'TRACK_A_COMBAT_SURFACE_AUDIT_READY',
    'combat_canonical_alignment_audit_v1.json':              'TRACK_B_COMBAT_CANONICAL_ALIGNMENT_AUDIT_READY',
    'surgical_release_patch_v1.json':                        'TRACK_C_SURGICAL_RELEASE_PATCH_READY',
    'post_battle_report_and_audio_qa_policy_v1.json':        'TRACK_D_POST_BATTLE_REPORT_AND_AUDIO_QA_POLICY_READY',
    'mobile_qa_and_release_readiness_matrix_v1.json':        'TRACK_E_MOBILE_QA_AND_RELEASE_READINESS_MATRIX_READY',
    'validator_and_suite_registration_v1.json':              'TRACK_F_VALIDATOR_AND_SUITE_REGISTRATION_READY',
    'completion_and_public_sync_v1.json':                    'TRACK_G_COMPLETION_AND_PUBLIC_SYNC_READY',
}
PROOF_MARKER = 'combat_finalize_for_release_suite_registration_proof_marker_v1.json'

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

FORBIDDEN_AUDIO_RUNTIME_TOKENS = [
    'expo-av', 'expo-audio', 'react-native-sound', 'react-native-track-player',
]

# Combat canonical compliance tokens
COMBAT_REQUIRED_TOKENS = [
    'grid_x',
    'grid_y',
    "facing: 'right'",
    "facing: 'left'",
    'SPEED_BASE',
    'chatDrawer',
]

BATTLE_REPORT_REQUIRED_TOKENS = [
    'damage_dealt',
    'damage_received',
    'healing_done',
    'mvp_ally_id',
    'mvp_enemy_id',
]

POST_BATTLE_REQUIRED_TOKENS = [
    'rewards.auto_claim',
    'account_level_up',
    'new_account_level',
]

BUILD_POST_BATTLE_REQUIRED_TOKENS = [
    'damage_dealt',
    'mvpId',
    'allies',
    'enemies',
]

# These must NOT appear (would mean unauthorized runtime activation)
FORBIDDEN_RUNTIME_ACTIVATION_TOKENS = [
    'SYNERGY_V2_BATTLE_ACTIVE',
    'synergy_v2_battle_active',
    'ARTIFACT_BONUS_RUNTIME_ACTIVE',
    'DIVINE_WEAPON_RUNTIME_ACTIVE',
    'STATUS_EFFECT_RUNTIME_ACTIVE',
    'VFX_RUNTIME_ACTIVE',
]


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def fail(msg):
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main():
    # 1) Track JSON files present + valid + expected verdict
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
        if d.get('task_id') != 'PROJECT_COMBAT_FINALIZE_FOR_RELEASE':
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
    if pm_d.get('weakens_REQUIRED_validators') is not False:
        fail('proof marker must declare weakens_REQUIRED_validators=false')
    if pm_d.get('battle_engine_touched') is not False:
        fail('proof marker must declare battle_engine_touched=false')
    if pm_d.get('combat_tsx_touched') is not False:
        fail('proof marker must declare combat_tsx_touched=false')

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

    # 5) combat.tsx canonical tokens present
    combat = (ROOT / 'frontend/app/combat.tsx').read_text(encoding='utf-8')
    for tok in COMBAT_REQUIRED_TOKENS:
        if tok not in combat:
            fail(f'combat.tsx missing canonical token: {tok!r}')

    # 6) BattleReport.tsx tokens
    br = (ROOT / 'frontend/components/battle/BattleReport.tsx').read_text(encoding='utf-8')
    for tok in BATTLE_REPORT_REQUIRED_TOKENS:
        if tok not in br:
            fail(f'BattleReport.tsx missing required token: {tok!r}')

    # 7) PostBattleSummary.tsx tokens
    pbs = (ROOT / 'frontend/components/battle/PostBattleSummary.tsx').read_text(encoding='utf-8')
    for tok in POST_BATTLE_REQUIRED_TOKENS:
        if tok not in pbs:
            fail(f'PostBattleSummary.tsx missing required token: {tok!r}')

    # 8) buildPostBattleSummary.ts tokens
    bpbs = (ROOT / 'frontend/components/battle/buildPostBattleSummary.ts').read_text(encoding='utf-8')
    for tok in BUILD_POST_BATTLE_REQUIRED_TOKENS:
        if tok not in bpbs:
            fail(f'buildPostBattleSummary.ts missing required token: {tok!r}')

    # 9) No audio runtime imports in combat.tsx or battle components
    audio_import_re = re.compile(r"from\s+['\"](expo-av|expo-audio|react-native-sound|react-native-track-player)['\"]|require\(['\"](expo-av|expo-audio|react-native-sound|react-native-track-player)['\"]\)")
    scan_targets = [
        ROOT / 'frontend/app/combat.tsx',
        ROOT / 'frontend/components/BattleSprite.tsx',
        ROOT / 'frontend/components/RuntimeSheetSprite.tsx',
        ROOT / 'frontend/components/battle/BattleReport.tsx',
        ROOT / 'frontend/components/battle/PostBattleSummary.tsx',
        ROOT / 'frontend/components/battle/buildPostBattleSummary.ts',
        ROOT / 'frontend/components/battle/motionSystem.ts',
        ROOT / 'frontend/components/battle/heroBattleAnimations.ts',
    ]
    for p in scan_targets:
        if not p.exists():
            continue
        content = p.read_text(encoding='utf-8', errors='ignore')
        m = audio_import_re.search(content)
        if m:
            fail(f'forbidden audio runtime import in {p}: {m.group(0)!r}')

    # 10) No audio runtime lib in package.json
    pkg = json.loads((ROOT / 'frontend/package.json').read_text(encoding='utf-8'))
    deps = set(pkg.get('dependencies', {}).keys()) | set(pkg.get('devDependencies', {}).keys())
    for tok in FORBIDDEN_AUDIO_RUNTIME_TOKENS:
        if tok in deps:
            fail(f'forbidden audio runtime lib present in package.json: {tok}')

    # 11) Audio placeholders still present (12 WAV + manifest) — pack 184 invariant
    audio_dir = ROOT / 'frontend/assets/audio/test_placeholders'
    if not audio_dir.exists():
        fail('audio test_placeholders directory missing (pack 184 invariant)')
    wavs = sorted(audio_dir.glob('*.wav'))
    if len(wavs) != 12:
        fail(f'expected exactly 12 WAV placeholders; got {len(wavs)}')
    if not (audio_dir / 'manifest.json').exists():
        fail('audio manifest.json missing (pack 184 invariant)')

    # 12) No unauthorized runtime activation tokens in battle_engine.py or combat.tsx
    be = (ROOT / 'backend/battle_engine.py').read_text(encoding='utf-8')
    for tok in FORBIDDEN_RUNTIME_ACTIVATION_TOKENS:
        if tok in be:
            fail(f'forbidden runtime activation token in battle_engine.py: {tok}')
        if tok in combat:
            fail(f'forbidden runtime activation token in combat.tsx: {tok}')

    # 13) battle_engine.py and combat.tsx NOT touched (no pack id marker injected)
    if 'PROJECT_COMBAT_FINALIZE_FOR_RELEASE' in be:
        fail('battle_engine.py MUST NOT contain pack marker (MD5_LOCKED)')
    if 'PROJECT_COMBAT_FINALIZE_FOR_RELEASE' in combat:
        fail('combat.tsx MUST NOT contain pack marker (no broad refactor)')

    # 14) BattleReport / PostBattleSummary / buildPostBattleSummary NOT touched by this pack
    #     (we want zero combat-runtime changes; only docs + validator + suite registration)
    for rel in [
        'frontend/components/battle/BattleReport.tsx',
        'frontend/components/battle/PostBattleSummary.tsx',
        'frontend/components/battle/buildPostBattleSummary.ts',
    ]:
        if 'PROJECT_COMBAT_FINALIZE_FOR_RELEASE' in (ROOT / rel).read_text(encoding='utf-8'):
            fail(f'{rel} MUST NOT contain pack marker (no runtime change in this pack)')

    # 15) Track C: no_patch_required + no runtime touch flags
    c = json.loads((DIR / 'surgical_release_patch_v1.json').read_text())
    if c.get('no_patch_required') is not True:
        fail('Track C no_patch_required must be True')
    if c.get('battle_engine_touched') is not False:
        fail('Track C battle_engine_touched must be False')
    if c.get('combat_tsx_touched') is not False:
        fail('Track C combat_tsx_touched must be False')
    if c.get('formula_change') is not False:
        fail('Track C formula_change must be False')
    if c.get('synergy_v2_battle_activation') is not False:
        fail('Track C synergy_v2_battle_activation must be False')
    if c.get('artifact_bonus_activation') is not False:
        fail('Track C artifact_bonus_activation must be False')
    if c.get('divine_weapons_runtime') is not False:
        fail('Track C divine_weapons_runtime must be False')
    if c.get('full_status_runtime') is not False:
        fail('Track C full_status_runtime must be False')
    if c.get('full_vfx_runtime') is not False:
        fail('Track C full_vfx_runtime must be False')
    if c.get('broad_audio_engine') is not False:
        fail('Track C broad_audio_engine must be False')

    # 16) Track D: design_only + runtime_change false + audio_qa_policy runtime_attached false
    dt = json.loads((DIR / 'post_battle_report_and_audio_qa_policy_v1.json').read_text())
    if dt.get('design_only') is not True:
        fail('Track D design_only must be True')
    if dt.get('runtime_change') is not False:
        fail('Track D runtime_change must be False')
    if dt.get('audio_qa_policy', {}).get('runtime_attached') is not False:
        fail('Track D audio_qa_policy.runtime_attached must be False')

    # 17) Track E: matrix non vuoto + 15 checklist items
    et = json.loads((DIR / 'mobile_qa_and_release_readiness_matrix_v1.json').read_text())
    if len(et.get('mobile_qa_checklist', [])) < 15:
        fail('Track E mobile_qa_checklist must have at least 15 items')
    if not et.get('release_readiness_matrix'):
        fail('Track E release_readiness_matrix must be non-empty')

    # 18) Track A audit_only + db_writes 0
    at = json.loads((DIR / 'combat_surface_audit_v1.json').read_text())
    if at.get('audit_only') is not True:
        fail('Track A audit_only must be True')
    if at.get('db_writes') != 0:
        fail('Track A db_writes must be 0')
    if at.get('runtime_changes') != 0:
        fail('Track A runtime_changes must be 0')

    # 19) Track B compliant_count >= 12, non_compliant_count == 0
    bt = json.loads((DIR / 'combat_canonical_alignment_audit_v1.json').read_text())
    if bt.get('compliant_count', 0) < 12:
        fail('Track B compliant_count must be >= 12')
    if bt.get('non_compliant_count', -1) != 0:
        fail('Track B non_compliant_count must be 0')

    print('[PASS] PROJECT_COMBAT_FINALIZE_FOR_RELEASE master validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
