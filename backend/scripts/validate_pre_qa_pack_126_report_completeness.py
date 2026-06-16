#!/usr/bin/env python3
"""Pack 126 — report completeness validator."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS = REPO_ROOT / 'docs' / 'divine'

REQUIRED = [
    'Device QA Pack 125',
    'Files audited',
    'DB/backend/user/server alignment',
    'QA seed before/after',
    'Team save env',
    'Global combat background',
    'Old battle layout',
    'Why only 5 heroes',
    'Preview result no fake EXP',
    'Before/after',
    'Validator results',
    'no-live',
    'Rollback',
    'Device QA V6 checklist',
    'Remaining blockers',
    'next step',
]


def main() -> int:
    errors = []
    cands = sorted(DOCS.glob('*PACK_126*.md'))
    if not cands:
        errors.append('no Pack 126 report .md found')
        return _emit(errors)
    src = cands[-1].read_text(encoding='utf-8')
    print(f'OK    report: {cands[-1].name}')
    for sec in REQUIRED:
        if sec.lower() not in src.lower():
            errors.append(f'missing section: `{sec}`')
        else:
            print(f'OK    section: {sec}')
    return _emit(errors)


def _emit(errors):
    print('\n' + '='*72)
    print('Pack 126 — report completeness')
    print('='*72)
    report = {'pack': 'PRE_QA_PACK_126_REPORT_COMPLETENESS', 'status': 'PASS' if not errors else 'FAIL', 'errors': errors}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_126_report_completeness_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  report contains all required sections')
    return 0


if __name__ == '__main__':
    sys.exit(main())
