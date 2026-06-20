#!/usr/bin/env python3
"""Pack 132 — Master Device QA Gate Matrix validator.

Static-only validator. ENFORCED level: marker file present + verdict pinned
+ device_qa_status BLOCKED + Pack 133 not started + no forbidden 'ready' claims.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MARKER = REPO_ROOT / 'data' / 'design' / 'system_safety' / 'pack_132_master_device_qa_gate_marker.json'
FORBIDDEN_VERDICTS = ['DEVICE_QA_READY', 'DEVICE_QA_PASS', 'PUBLIC_QA_READY', 'RELEASE_READY']
REQUIRED_KEYS = ['pack', 'verdict', 'device_qa_status', 'device_qa_gate_status', 'pack_133_required_for_device_qa',
                 'db_write_scope', 'runtime_mutation_scope', 'manual_required', 'not_executed', 'next_required_pack']


def main():
    errs = []
    if not MARKER.exists():
        return _emit(['marker missing: ' + str(MARKER.relative_to(REPO_ROOT))])
    try:
        data = json.loads(MARKER.read_text(encoding='utf-8'))
    except Exception as e:
        return _emit([f'marker JSON invalid: {e}'])
    for k in REQUIRED_KEYS:
        if k not in data:
            errs.append(f'missing key: {k}')
    if data.get('pack') != 132:
        errs.append('pack != 132')
    if data.get('device_qa_status') != 'BLOCKED':
        errs.append('device_qa_status must be BLOCKED')
    if data.get('db_write_scope') != 'NONE':
        errs.append('db_write_scope must be NONE')
    if data.get('runtime_mutation_scope') != 'NONE':
        errs.append('runtime_mutation_scope must be NONE')
    if data.get('pack_133_started') is True:
        errs.append('Pack 133 must not be started')
    verdict = str(data.get('verdict', ''))
    for fv in FORBIDDEN_VERDICTS:
        if fv in verdict:
            errs.append(f'forbidden verdict token in marker: {fv}')
    if 'PACK_132' not in verdict:
        errs.append('verdict must reference PACK_132')
    return _emit(errs)


def _emit(errs):
    report = {'pack': 'PACK_132_MASTER_DEVICE_QA_GATE_MATRIX',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_132_master_device_qa_gate_matrix_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs:
            print(f'FAIL {e}')
        return 1
    print('PASS  master device QA gate matrix coherent (BLOCKED)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
