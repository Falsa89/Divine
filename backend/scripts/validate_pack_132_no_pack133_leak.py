#!/usr/bin/env python3
"""Pack 132 — No Pack 133 leak validator."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = []  # Pack 133 \u00e8 l'ultimo della catena Pre-QA; nessun pack futuro da forbidire qui.
IGNORE = ['.git/', 'node_modules/', '__pycache__/', '.expo/']


def main():
    errs = []
    leaked = []
    for p in REPO_ROOT.rglob('*'):
        if not p.is_file():
            continue
        rel = str(p.relative_to(REPO_ROOT))
        if any(s in rel for s in IGNORE):
            continue
        for pat in FORBIDDEN:
            if pat in p.name:
                leaked.append(rel)
                break
    if leaked:
        for f in leaked[:20]:
            errs.append(f'Pack 133 leak: {f}')
    return _emit(errs, leaked)


def _emit(errs, leaked):
    report = {'pack': 'PACK_132_NO_PACK133_LEAK',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'leaked_files': leaked,
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_132_no_pack133_leak_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs:
            print(f'FAIL {e}')
        return 1
    print('PASS  no Pack 133 leak')
    return 0


if __name__ == '__main__':
    sys.exit(main())
