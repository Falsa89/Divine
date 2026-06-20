#!/usr/bin/env python3
"""Pack 133 — Final Pre-QA Chain Marker validator."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MARKER = REPO_ROOT / 'data' / 'design' / 'system_safety' / 'pack_133_final_pre_qa_chain_marker.json'
REQUIRED = ['pack', 'pre_qa_chain_status', 'pack_127_status',
            'pack_128_status', 'pack_129_status', 'pack_130_status',
            'pack_131_status', 'pack_132_status', 'pack_133_status',
            'device_qa_status', 'release_ready', 'db_write_scope',
            'runtime_mutation_scope', 'reward_progress_scope']


def main():
    errs = []
    if not MARKER.exists():
        return _emit(['final chain marker missing'])
    try:
        d = json.loads(MARKER.read_text(encoding='utf-8'))
    except Exception as e:
        return _emit([f'invalid JSON: {e}'])
    for k in REQUIRED:
        if k not in d:
            errs.append(f'missing key: {k}')
    if d.get('pack') != 133:
        errs.append('pack != 133')
    if d.get('release_ready') is True:
        errs.append('release_ready must be False')
    if d.get('db_write_scope') != 'NONE':
        errs.append('db_write_scope must be NONE')
    if d.get('runtime_mutation_scope') != 'NONE':
        errs.append('runtime_mutation_scope must be NONE')
    if d.get('reward_progress_scope') != 'NONE':
        errs.append('reward_progress_scope must be NONE')
    for k in ['pack_127_status', 'pack_128_status', 'pack_129_status',
              'pack_130_status', 'pack_131_status', 'pack_132_status']:
        if 'CLOSED' not in str(d.get(k, '')):
            errs.append(f'{k} must be a CLOSED_PUBLIC_REPO_*_SYNCED status')
    return _emit(errs)


def _emit(errs):
    report = {'pack': 'PACK_133_FINAL_CHAIN_MARKER',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'validation_kind': 'STATIC', 'enforcement': 'ENFORCED'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_133_final_chain_marker_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print('PASS  final pre-QA chain marker coherent')
    return 0


if __name__ == '__main__': sys.exit(main())
