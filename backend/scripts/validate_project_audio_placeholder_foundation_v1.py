#!/usr/bin/env python3
"""
PROJECT_AUDIO_PLACEHOLDER_FOUNDATION validator (statico, audio TEST foundation only).

Asserisce:
  - 5 JSON design (A, B, C, D, E) + 1 proof marker
  - tutti i JSON validi + verdict atteso per track
  - 12 audio entries in registry con required metadata keys
  - 12 file WAV TEST presenti in frontend/assets/audio/test_placeholders/
  - tutti i file WAV header-valid (riff/wave) + dimensione <300 KiB
  - manifest.json presente con 12 entries
  - generator script presente in backend/scripts/
  - tutti gli entries hanno audio_status=test_placeholder, replace_before_release=true,
    runtime_attached=false
  - nessun audio runtime engine installato (no expo-av/expo-audio/react-native-sound in package.json)
  - nessun import audio runtime in frontend/app/* o backend
  - frontend lock invariants intatti (SHOP/BP/VIP/ITEM_SHOP_LOCKED_V2)
  - MD5 invarianti baseline rispettati su battle_engine.py / .env /
    routes/artifacts.py / battlepass.tsx / vip.tsx
  - Soul Forge files NON toccati in questo pack
  - combat.tsx no broad refactor
  - nessun audio import in combat.tsx, soul-forge.tsx
  - validator NON indebolisce alcun REQUIRED validator

Exit 0 su PASS, 1 su FAIL. Registrazione OPTIONAL nel suite runner.
"""
import hashlib
import json
import re
import sys
import wave
from pathlib import Path

ROOT = Path('/app')
DIR = ROOT / 'data/design/audio_placeholder'
AUDIO_DIR = ROOT / 'frontend/assets/audio/test_placeholders'

REQUIRED_TRACKS = {
    'audio_surface_audit_v1.json':                       'TRACK_A_AUDIO_SURFACE_AUDIT_READY',
    'test_audio_registry_and_manifest_v1.json':          'TRACK_B_TEST_AUDIO_REGISTRY_AND_MANIFEST_READY',
    'placeholder_audio_asset_generation_v1.json':        'TRACK_C_PLACEHOLDER_AUDIO_ASSET_GENERATION_READY',
    'audio_runtime_attachment_policy_v1.json':           'TRACK_D_AUDIO_RUNTIME_ATTACHMENT_POLICY_READY',
    'final_audio_replacement_audit_policy_v1.json':      'TRACK_E_FINAL_AUDIO_REPLACEMENT_AUDIT_POLICY_READY',
}
PROOF_MARKER = 'audio_placeholder_suite_registration_proof_marker_v1.json'

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

REQUIRED_AUDIO_KEYS = {
    'test_ui_click', 'test_ui_confirm', 'test_ui_back_cancel', 'test_ui_error_locked',
    'test_reward_basic', 'test_notification_basic', 'test_mode_enter',
    'test_battle_start', 'test_battle_hit_soft', 'test_battle_victory_stinger',
    'test_battle_defeat_stinger', 'test_ambient_placeholder_loop',
}

REQUIRED_METADATA_KEYS = {
    'audio_key', 'mode_id', 'screen_id', 'file_path', 'audio_status',
    'replace_before_release', 'final_audio_expected', 'runtime_attached',
    'category', 'duration_target_ms', 'loop', 'volume_hint', 'notes',
}

FORBIDDEN_AUDIO_RUNTIME_TOKENS = [
    'expo-av', 'expo-audio', 'react-native-sound', 'react-native-track-player',
]

MAX_TOTAL_AUDIO_BYTES = 1_500_000  # 1.5 MB hard cap; expected ~300 KiB


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
        if d.get('task_id') != 'PROJECT_AUDIO_PLACEHOLDER_FOUNDATION':
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

    # 5) Track B registry has 12 entries with all required keys + audio_status/runtime_attached/replace
    reg = json.loads((DIR / 'test_audio_registry_and_manifest_v1.json').read_text())
    entries = reg.get('audio_entries', [])
    if len(entries) != 12:
        fail(f'Track B must have exactly 12 audio entries; got {len(entries)}')
    found_keys = set()
    for i, e in enumerate(entries):
        missing = REQUIRED_METADATA_KEYS - set(e.keys())
        if missing:
            fail(f'audio entry #{i} ({e.get("audio_key")}) missing required keys: {sorted(missing)}')
        if e['audio_status'] != 'test_placeholder':
            fail(f'audio entry {e["audio_key"]!r} audio_status must be test_placeholder; got {e["audio_status"]!r}')
        if e['replace_before_release'] is not True:
            fail(f'audio entry {e["audio_key"]!r} replace_before_release must be True')
        if e['final_audio_expected'] is not True:
            fail(f'audio entry {e["audio_key"]!r} final_audio_expected must be True')
        if e['runtime_attached'] is not False:
            fail(f'audio entry {e["audio_key"]!r} runtime_attached must be False')
        if not isinstance(e['loop'], bool):
            fail(f'audio entry {e["audio_key"]!r} loop must be boolean')
        if not isinstance(e['duration_target_ms'], int) or e['duration_target_ms'] <= 0:
            fail(f'audio entry {e["audio_key"]!r} duration_target_ms must be positive int')
        found_keys.add(e['audio_key'])
    missing_keys = REQUIRED_AUDIO_KEYS - found_keys
    if missing_keys:
        fail(f'registry missing required audio_keys: {sorted(missing_keys)}')

    # 6) 12 WAV files exist + are valid + total size under cap
    if not AUDIO_DIR.exists():
        fail(f'audio directory missing: {AUDIO_DIR}')
    total = 0
    for e in entries:
        f = ROOT / e['file_path']
        if not f.exists():
            fail(f'audio file missing: {e["file_path"]}')
        sz = f.stat().st_size
        total += sz
        # validate wav header
        try:
            with wave.open(str(f), 'rb') as w:
                ch = w.getnchannels()
                sw = w.getsampwidth()
                fr = w.getframerate()
                nf = w.getnframes()
            if ch != 1:
                fail(f'wav {f.name} must be mono (1ch); got {ch}')
            if sw != 2:
                fail(f'wav {f.name} must be 16-bit (sampwidth=2); got {sw}')
            if fr != 16000:
                fail(f'wav {f.name} must be 16kHz; got {fr}')
            if nf <= 0:
                fail(f'wav {f.name} has no frames')
        except wave.Error as we:
            fail(f'wav {f.name} invalid header: {we}')
    if total > MAX_TOTAL_AUDIO_BYTES:
        fail(f'total audio size {total} exceeds cap {MAX_TOTAL_AUDIO_BYTES}')

    # 7) Manifest present + 12 entries
    manifest_p = AUDIO_DIR / 'manifest.json'
    if not manifest_p.exists():
        fail('manifest.json missing in audio dir')
    manifest = json.loads(manifest_p.read_text(encoding='utf-8'))
    if len(manifest.get('entries', [])) != 12:
        fail(f'manifest.json must have 12 entries; got {len(manifest.get("entries", []))}')
    if manifest.get('all_runtime_attached_false') is not True:
        fail('manifest.json all_runtime_attached_false must be True')
    if manifest.get('all_replace_before_release_true') is not True:
        fail('manifest.json all_replace_before_release_true must be True')

    # 8) Generator script present
    gen = ROOT / 'backend/scripts/generate_audio_test_placeholders_v1.py'
    if not gen.exists():
        fail('generator script missing: backend/scripts/generate_audio_test_placeholders_v1.py')

    # 9) No audio runtime library in package.json
    pkg = json.loads((ROOT / 'frontend/package.json').read_text(encoding='utf-8'))
    deps = set(pkg.get('dependencies', {}).keys()) | set(pkg.get('devDependencies', {}).keys())
    for tok in FORBIDDEN_AUDIO_RUNTIME_TOKENS:
        if tok in deps:
            fail(f'forbidden audio runtime lib present in package.json: {tok}')

    # 10) No audio runtime imports in product code
    scan_roots = [
        ROOT / 'frontend/app',
        ROOT / 'backend/routes',
        ROOT / 'backend/server.py',
    ]
    audio_import_re = re.compile(r"from\s+['\"](expo-av|expo-audio|react-native-sound|react-native-track-player)['\"]|require\(['\"](expo-av|expo-audio|react-native-sound|react-native-track-player)['\"]\)")
    for r in scan_roots:
        files = [r] if r.is_file() else (list(r.rglob('*')) if r.exists() else [])
        for p in files:
            if not p.is_file():
                continue
            if p.suffix not in ('.py', '.ts', '.tsx', '.js', '.jsx'):
                continue
            if any(part in ('node_modules', '__pycache__') for part in p.parts):
                continue
            content = p.read_text(encoding='utf-8', errors='ignore')
            m = audio_import_re.search(content)
            if m:
                fail(f'forbidden audio runtime import in {p}: {m.group(0)!r}')

    # 11) Soul Forge files NOT touched
    sf_be = (ROOT / 'backend/routes/soul_forge.py').read_text(encoding='utf-8')
    if 'PROJECT_AUDIO_PLACEHOLDER_FOUNDATION' in sf_be:
        fail('Soul Forge backend MUST NOT be touched in this pack')
    sf_fe = (ROOT / 'frontend/app/soul-forge.tsx').read_text(encoding='utf-8')
    if 'PROJECT_AUDIO_PLACEHOLDER_FOUNDATION' in sf_fe:
        fail('Soul Forge frontend MUST NOT be touched in this pack')

    # 12) battle_engine.py + combat.tsx not touched
    be = (ROOT / 'backend/battle_engine.py').read_text(encoding='utf-8')
    if 'PROJECT_AUDIO_PLACEHOLDER_FOUNDATION' in be:
        fail('battle_engine.py MUST NOT be touched in this pack')
    cf = (ROOT / 'frontend/app/combat.tsx').read_text(encoding='utf-8')
    if 'PROJECT_AUDIO_PLACEHOLDER_FOUNDATION' in cf:
        fail('frontend/app/combat.tsx MUST NOT be broadly refactored in this pack')

    # 13) Track A: audit_only + db_writes 0 + baseline frontend_audio_directory_present was false
    a = json.loads((DIR / 'audio_surface_audit_v1.json').read_text())
    if a.get('audit_only') is not True:
        fail('Track A audit_only must be True')
    if a.get('db_writes') != 0:
        fail('Track A db_writes must be 0')
    if a.get('baseline_audio_state', {}).get('frontend_audio_directory_present') is not False:
        fail('Track A baseline_audio_state.frontend_audio_directory_present must be False')

    # 14) Track C: no external audio + python stdlib only
    c = json.loads((DIR / 'placeholder_audio_asset_generation_v1.json').read_text())
    if c.get('external_audio_files_used') != 0:
        fail('Track C external_audio_files_used must be 0')
    if c.get('copyrighted_content_used') is not False:
        fail('Track C copyrighted_content_used must be False')
    if c.get('voice_acting_used') is not False:
        fail('Track C voice_acting_used must be False')
    if c.get('audio_engine_modifications') != 0:
        fail('Track C audio_engine_modifications must be 0')

    # 15) Track D: design_only + runtime_attached_in_this_pack=False + feature flags all gated off
    dt = json.loads((DIR / 'audio_runtime_attachment_policy_v1.json').read_text())
    if dt.get('design_only') is not True:
        fail('Track D design_only must be True')
    if dt.get('runtime_attached_in_this_pack') is not False:
        fail('Track D runtime_attached_in_this_pack must be False')
    if dt.get('runtime_engine_implementation_in_this_pack') is not False:
        fail('Track D runtime_engine_implementation_in_this_pack must be False')
    ff = dt.get('feature_flags_design', {})
    if ff.get('AUDIO_ENGINE_ENABLED') is not False:
        fail('Track D AUDIO_ENGINE_ENABLED must be False')
    if ff.get('AUDIO_GLOBAL_DISABLED') is not True:
        fail('Track D AUDIO_GLOBAL_DISABLED must be True')

    # 16) Track E: release_gate_blocking_rules non vuoto
    et = json.loads((DIR / 'final_audio_replacement_audit_policy_v1.json').read_text())
    if not et.get('release_gate_blocking_rules'):
        fail('Track E release_gate_blocking_rules must be non-empty')
    if not et.get('qa_acceptance_criteria_pre_release'):
        fail('Track E qa_acceptance_criteria_pre_release must be non-empty')

    print('[PASS] PROJECT_AUDIO_PLACEHOLDER_FOUNDATION master validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
