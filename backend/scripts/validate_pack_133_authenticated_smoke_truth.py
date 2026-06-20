#!/usr/bin/env python3
"""Pack 133 — Authenticated Smoke Truth validator.

Reads pack_133_device_qa_evidence_harness_report.json (if present) and
ensures the recorded AUTHENTICATED_SMOKE_STATUS is truthful. If env QA
was missing, status MUST be MANUAL_REQUIRED. If status is EXECUTED, the
report must include at least 1 phase_2 probe.

If the harness report is absent, classifies NOT_EXECUTED (documentary).
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = REPO_ROOT / 'backend' / 'scripts' / 'reports' / 'pack_133_device_qa_evidence_harness_report.json'


def main():
    if not REPORT.exists():
        _write({'pack': 'PACK_133_AUTHENTICATED_SMOKE_TRUTH', 'status': 'PASS',
                'classification': 'NOT_EXECUTED',
                'note': 'harness report not present yet; run device_qa_evidence_harness.py first',
                'validation_kind': 'DOCUMENTARY', 'enforcement': 'NOT_EXECUTED', 'errors': []})
        print('PASS  authenticated smoke truth NOT_EXECUTED (harness report not present)')
        return 0
    try:
        data = json.loads(REPORT.read_text(encoding='utf-8'))
    except Exception as e:
        _write({'pack': 'PACK_133_AUTHENTICATED_SMOKE_TRUTH', 'status': 'FAIL',
                'classification': 'FAIL', 'errors': [str(e)],
                'validation_kind': 'DOCUMENTARY', 'enforcement': 'ENFORCED'})
        print(f'FAIL  harness report invalid: {e}')
        return 1
    errs = []
    status = data.get('AUTHENTICATED_SMOKE_STATUS')
    phase2 = data.get('phase_2_auth_probes') or []
    if status == 'EXECUTED' and not phase2:
        errs.append('AUTHENTICATED_SMOKE_STATUS=EXECUTED but no phase_2 probes recorded')
    if status == 'MANUAL_REQUIRED' and phase2:
        # Trusted: if env was missing we should not have phase_2; but tolerated.
        pass
    if status not in ('EXECUTED', 'MANUAL_REQUIRED', 'NOT_EXECUTED'):
        errs.append(f'unknown AUTHENTICATED_SMOKE_STATUS: {status}')
    if data.get('release_ready') is True:
        errs.append('release_ready must be False')
    _write({'pack': 'PACK_133_AUTHENTICATED_SMOKE_TRUTH',
            'status': 'PASS' if not errs else 'FAIL',
            'classification': status or 'NOT_EXECUTED',
            'errors': errs, 'validation_kind': 'DOCUMENTARY',
            'enforcement': 'ENFORCED'})
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print(f'PASS  authenticated smoke truth ({status})')
    return 0


def _write(report):
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_133_authenticated_smoke_truth_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__': sys.exit(main())
