#!/usr/bin/env python3
"""Pack 133 — Evidence Manifest Truth validator."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MARKER = REPO_ROOT / 'data' / 'design' / 'system_safety' / 'pack_133_device_qa_evidence_marker.json'
MANUAL_MD = REPO_ROOT / 'docs' / 'divine' / 'device_qa_evidence_manifest_PACK_133.md'
REQUIRED_KEYS = ['pack', 'verdict', 'device_qa_status',
                 'authenticated_smoke_status', 'screenshot_evidence_status',
                 'physical_device_status', 'manual_signoff_status',
                 'release_ready', 'db_write_scope', 'runtime_mutation_scope',
                 'reward_progress_scope', 'secret_redaction_policy',
                 'endpoint_evidence_summary', 'known_gaps', 'manual_required']
FORBIDDEN_VERDICTS = ['DEVICE_QA_READY', 'DEVICE_QA_PASS', 'PUBLIC_QA_READY',
                     'RELEASE_READY', 'PRODUCTION_READY', 'COMMERCIAL_READY']


def main():
    errs = []
    if not MARKER.exists():
        return _emit(['evidence marker missing'])
    try:
        data = json.loads(MARKER.read_text(encoding='utf-8'))
    except Exception as e:
        return _emit([f'evidence marker invalid: {e}'])
    for k in REQUIRED_KEYS:
        if k not in data:
            errs.append(f'missing key: {k}')
    if data.get('release_ready') is True:
        errs.append('release_ready must be False in Pack 133')
    if data.get('db_write_scope') != 'NONE':
        errs.append('db_write_scope must be NONE')
    if data.get('runtime_mutation_scope') != 'NONE':
        errs.append('runtime_mutation_scope must be NONE')
    if data.get('reward_progress_scope') != 'NONE':
        errs.append('reward_progress_scope must be NONE')
    verdict = str(data.get('verdict', ''))
    for fv in FORBIDDEN_VERDICTS:
        if fv in verdict:
            errs.append(f'forbidden verdict token in marker: {fv}')
    if 'PACK_133' not in verdict:
        errs.append('verdict must reference PACK_133')
    # manifest MD presente? (puo' essere generato a runtime, ma per truth occorre marker valido)
    return _emit(errs)


def _emit(errs):
    report = {'pack': 'PACK_133_EVIDENCE_MANIFEST_TRUTH',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_133_evidence_manifest_truth_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print('PASS  evidence manifest marker coherent')
    return 0


if __name__ == '__main__': sys.exit(main())
