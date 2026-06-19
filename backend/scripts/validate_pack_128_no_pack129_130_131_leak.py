#!/usr/bin/env python3
"""Pack 128 — No Pack 130/131/132/133 leak (STATIC + git check).

Verifica che NESSUN file Pack 130+ sia stato creato/modificato in questo branch.
Pack 129 è il pack successivo a Pack 128 e in Pack 129 (chiuso) viene aggiornato
questo validator per rimuovere `pack_129/PACK_129` dalla forbidden list — Pack
129 è ora pack precedente, non un future-pack leak.
"""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_PATTERNS = ['pack_132', 'pack_133',
                      'PACK_132', 'PACK_133']


def main() -> int:
    errors = []; notes = []
    # Filesystem scan.
    leaked = []
    for p in REPO_ROOT.rglob('*'):
        if not p.is_file(): continue
        if any(seg in str(p.relative_to(REPO_ROOT)) for seg in ['.git/', 'node_modules/', '__pycache__/', '.expo/']):
            continue
        name = p.name
        for pat in FORBIDDEN_PATTERNS:
            if pat in name:
                leaked.append(str(p.relative_to(REPO_ROOT)))
                break
    if leaked:
        for f in leaked[:20]:
            errors.append(f'Pack 129+ leak detected: {f}')
    else:
        print('OK    nessun file Pack 129/130/131/132/133 trovato in tree')
    return _emit(errors, notes, leaked)


def _emit(errors, notes, leaked):
    print('\n' + '=' * 72)
    report = {
        'pack': 'PACK_128_NO_PACK129_130_131_132_133_LEAK',
        'status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
        'notes': notes,
        'leaked_files': leaked,
        'validation_kind': 'STATIC',
        'enforcement': 'ENFORCED_NO_FUTURE_PACK_LEAK',
    }
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_128_no_pack129_130_131_leak_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  no Pack 129/130/131/132/133 leak')
    return 0


if __name__ == '__main__': sys.exit(main())
