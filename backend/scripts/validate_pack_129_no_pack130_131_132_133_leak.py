#!/usr/bin/env python3
"""Pack 129 — No Pack 130/131/132/133 leak (STATIC fs scan)."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = ['pack_131', 'pack_132', 'pack_133',
             'PACK_131', 'PACK_132', 'PACK_133']
IGNORE = ['.git/', 'node_modules/', '__pycache__/', '.expo/']


def main() -> int:
    errors = []; notes = []; leaked = []
    for p in REPO_ROOT.rglob('*'):
        if not p.is_file(): continue
        rel = str(p.relative_to(REPO_ROOT))
        if any(seg in rel for seg in IGNORE): continue
        for pat in FORBIDDEN:
            if pat in p.name:
                leaked.append(rel); break
    if leaked:
        for f in leaked[:20]: errors.append(f'Pack 130+ leak: {f}')
    else:
        print('OK    nessun file Pack 130/131/132/133 trovato')
    return _emit(errors, notes, leaked)


def _emit(errors, notes, leaked):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_129_NO_PACK130_131_132_133_LEAK',
              'status': 'PASS' if not errors else 'FAIL',
              'errors': errors, 'notes': notes, 'leaked_files': leaked,
              'validation_kind': 'STATIC', 'enforcement': 'ENFORCED_NO_FUTURE_PACK_LEAK'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_129_no_pack130_131_132_133_leak_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  no Pack 130/131/132/133 leak')
    return 0


if __name__ == '__main__': sys.exit(main())
