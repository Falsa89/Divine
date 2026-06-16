#!/usr/bin/env python3
"""PRE_QA_P0 — validate_current_zip_truth_rebaseline_v1.

Verifica che il rebaseline P0 sia coerente con il current ZIP:

  1. I 6 JSON in data/design/current_truth/ esistono e parsano.
  2. I 15 MD5 dichiarati in current_code_md5_snapshot_v1.json corrispondono
     ai MD5 reali calcolati sui file presenti nel filesystem.
  3. battle_engine.py current MD5 == 8b7f55d4f58605138daa8bbace23f514
     ed e' marcato come current-state truth (non come stale).
  4. Old MD5 151ca35... e' marcato superseded/historical, non come current
     invariant, in stale_md5_reference_inventory_v1.json e
     rebaseline_decision_record_v1.json.
  5. rebaseline_decision_record_v1.json dichiara:
       runtime_changed_by_this_pack=false,
       gameplay_changed_by_this_pack=false,
       db_write_performed=false,
       live_unlock_performed=false,
       reward_live_opened=false,
       gacha_live_opened=false,
       shop_live_opened=false,
       vip_live_opened=false,
       battlepass_live_opened=false,
       iap_opened=false.

Onesto, read-only, no fake PASS.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(HERE))
TRUTH_DIR = os.path.join(R, 'data', 'design', 'current_truth')

REQUIRED_FILES = {
    'current_code_md5_snapshot_v1.json': 'snapshot',
    'stale_md5_reference_inventory_v1.json': 'stale',
    'validator_truth_status_matrix_v1.json': 'matrix',
    'public_guardrail_current_snapshot_v1.json': 'guardrail',
    'rebaseline_decision_record_v1.json': 'decision',
    'next_macro_pack_readiness_v1.json': 'readiness',
}

OLD_STALE_MD5 = '151ca35ad3bc35f0a6209cb3744ed440'
EXPECTED_BATTLE_ENGINE_MD5 = '8b7f55d4f58605138daa8bbace23f514'


def _md5(fp: str) -> str:
    h = hashlib.md5()
    with open(fp, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    failures = []
    loaded = {}

    # 1) JSON presenti + parsabili
    for fn, key in REQUIRED_FILES.items():
        fp = os.path.join(TRUTH_DIR, fn)
        if not os.path.exists(fp):
            failures.append(f'missing: {fp}')
            continue
        try:
            loaded[key] = json.load(open(fp, encoding='utf-8'))
        except Exception as e:
            failures.append(f'json parse error {fn}: {e}')

    if failures:
        return _emit('FAIL', failures)

    # 2) MD5 declared vs real
    snap = loaded['snapshot']
    mismatches = []
    for rel, md5_declared in snap.get('files', {}).items():
        fp_abs = os.path.join(R, rel)
        if not os.path.exists(fp_abs):
            mismatches.append({'file': rel, 'reason': 'missing_in_fs'})
            continue
        real = _md5(fp_abs)
        if real != md5_declared:
            mismatches.append({
                'file': rel,
                'declared': md5_declared,
                'real': real,
            })
    if mismatches:
        for m in mismatches:
            failures.append(f'MD5 mismatch: {m}')

    # 3) battle_engine current MD5 + truth source
    be_decl = snap.get('files', {}).get('backend/battle_engine.py')
    if be_decl != EXPECTED_BATTLE_ENGINE_MD5:
        failures.append(
            f'battle_engine.py declared MD5 != expected current: '
            f'declared={be_decl} expected={EXPECTED_BATTLE_ENGINE_MD5}')

    # 4) Old MD5 marked superseded/historical
    stale = loaded['stale']
    if stale.get('stale_md5_target') != OLD_STALE_MD5:
        failures.append(
            f'stale_md5_target != {OLD_STALE_MD5} (val={stale.get("stale_md5_target")})')
    cb = stale.get('category_breakdown', {})
    if 'current_unsafe_validator_baseline' not in cb:
        failures.append('stale inventory missing current_unsafe_validator_baseline')
    if 'historical_acceptable' not in cb:
        failures.append('stale inventory missing historical_acceptable')

    decision = loaded['decision']
    be_dec = decision.get('battle_engine_md5_decision', {})
    if be_dec.get('old_md5') != OLD_STALE_MD5:
        failures.append('decision record old_md5 mismatch')
    if be_dec.get('current_md5_in_zip') != EXPECTED_BATTLE_ENGINE_MD5:
        failures.append('decision record current_md5_in_zip mismatch')
    if be_dec.get('runtime_change_introduced_by_this_pack') is not False:
        failures.append('decision record runtime_change_introduced_by_this_pack != false')

    # 5) Hard invariants
    inv = decision.get('hard_invariants_dichiarati_da_questo_pack', {})
    required_false = [
        'runtime_changed_by_this_pack',
        'gameplay_changed_by_this_pack',
        'db_write_performed',
        'live_unlock_performed',
        'reward_live_opened',
        'gacha_live_opened',
        'shop_live_opened',
        'vip_live_opened',
        'battlepass_live_opened',
        'iap_opened',
        'battle_result_commit_opened',
        'exp_progress_commit_opened',
        'ranking_live_opened',
        'character_bible_changed',
        'asset_changed',
        'env_flag_changed',
        'required_validator_weakened',
        'required_validator_removed',
        'historical_docs_deleted',
        'historical_docs_meaning_changed',
    ]
    for k in required_false:
        if inv.get(k) is not False:
            failures.append(f'hard invariant {k} != false (val={inv.get(k)!r})')

    if failures:
        return _emit('FAIL', failures)

    print(
        '[v_p0_truth_rebaseline] OK '
        f'files_verified={len(snap.get("files", {}))} '
        f'battle_engine_md5={EXPECTED_BATTLE_ENGINE_MD5} '
        f'old_md5_marked_superseded=true '
        f'runtime_changed=false db_write=false live_unlock=false'
    )
    return 0


def _emit(verdict: str, failures: list) -> int:
    print(f'[v_p0_truth_rebaseline] {verdict}')
    for f in failures:
        print(f'  - {f}')
    return 0 if verdict == 'OK' else 1


if __name__ == '__main__':
    sys.exit(main())
