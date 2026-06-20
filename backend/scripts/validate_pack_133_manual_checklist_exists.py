#!/usr/bin/env python3
"""Pack 133 — Manual Device QA Checklist exists validator."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKLIST = REPO_ROOT / 'docs' / 'divine' / 'device_qa_manual_checklist_PACK_133.md'
REQUIRED_SECTIONS = [
    'Prerequisiti env', 'Account QA', 'Server QA', 'JWT / Credenziali',
    'Avvio backend', 'Avvio Expo', 'Test Home',
    'Test server selection', 'Test pre-battle lobby', 'Test launch context preview',
    'Test combat preview', 'Test post-battle preview safe',
    'no reward', 'no EXP', 'no progress',
    'Screenshot richiesti', 'Criteri PASS', 'Criteri BLOCKED', 'Signoff manuale',
]


def main():
    errs = []
    if not CHECKLIST.exists():
        return _emit(['manual checklist missing: ' + str(CHECKLIST.relative_to(REPO_ROOT))])
    src = CHECKLIST.read_text(encoding='utf-8')
    for s in REQUIRED_SECTIONS:
        if s.lower() not in src.lower():
            errs.append(f'missing checklist section: {s}')
    return _emit(errs)


def _emit(errs):
    report = {'pack': 'PACK_133_MANUAL_CHECKLIST_EXISTS',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'validation_kind': 'STATIC',
              'enforcement': 'VALIDATED_ONLY'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_133_manual_checklist_exists_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print('PASS  manual Device QA checklist present and complete')
    return 0


if __name__ == '__main__': sys.exit(main())
