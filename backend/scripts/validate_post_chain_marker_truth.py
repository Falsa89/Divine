#!/usr/bin/env python3
"""POST_CHAIN — Marker truth validator."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MARKER = REPO_ROOT / 'data' / 'design' / 'system_safety' / 'post_chain_repo_hygiene_pass_1_marker.json'
REQUIRED = ['pass', 'verdict', 'pre_qa_chain_status', 'device_qa_status',
            'release_ready', 'artifact_policy_status',
            'emergent_noise_policy_status', 'future_pack_leak_guard_status',
            'runtime_mutation_scope', 'db_write_scope', 'reward_progress_scope']


def main():
    errs = []
    if not MARKER.exists():
        return _emit(['post-chain marker missing'])
    try:
        d = json.loads(MARKER.read_text(encoding='utf-8'))
    except Exception as e:
        return _emit([f'invalid JSON: {e}'])
    for k in REQUIRED:
        if k not in d: errs.append(f'missing key: {k}')
    if d.get('release_ready') is True:
        errs.append('release_ready must be False')
    if d.get('runtime_mutation_scope') != 'NONE':
        errs.append('runtime_mutation_scope must be NONE')
    if d.get('db_write_scope') != 'NONE':
        errs.append('db_write_scope must be NONE')
    if d.get('reward_progress_scope') != 'NONE':
        errs.append('reward_progress_scope must be NONE')
    if d.get('device_qa_status') != 'MANUAL_REQUIRED':
        errs.append('device_qa_status must be MANUAL_REQUIRED')
    if 'POST_CHAIN_REPO_HYGIENE_PASS_1' not in str(d.get('verdict', '')):
        errs.append('verdict must reference POST_CHAIN_REPO_HYGIENE_PASS_1')
    if d.get('pack_134_started') is True:
        errs.append('pack_134_started must be False')
    for k in ['pack_127_status', 'pack_128_status', 'pack_129_status',
              'pack_130_status', 'pack_131_status', 'pack_132_status', 'pack_133_status']:
        if 'CLOSED' not in str(d.get(k, '')):
            errs.append(f'{k} must be CLOSED_PUBLIC_REPO_*_SYNCED')
    return _emit(errs)


def _emit(errs):
    report = {'pack': 'POST_CHAIN_MARKER_TRUTH',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'validation_kind': 'STATIC', 'enforcement': 'ENFORCED'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'post_chain_marker_truth_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print('PASS  post-chain marker coherent')
    return 0


if __name__ == '__main__': sys.exit(main())
