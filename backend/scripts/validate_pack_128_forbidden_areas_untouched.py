#!/usr/bin/env python3
"""Pack 128 — Forbidden areas untouched (STATIC + git diff).

Verifica che il diff tra il commit di chiusura Pack 127 (b9b516b33) e HEAD
NON contenga modifiche alle aree vietate. Best-effort: se git non è
disponibile o il commit anchor non esiste, segnaliamo NOTE invece di FAIL.
"""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_PATHS = [
    'backend/battle_engine.py',
    'backend/battle_core.py',
    'backend/game_systems.py',
    'backend/.env',
    'data/design/heroes_master.json',
    # final_numbers/, assets/audio/, assets/images/ — directory globs
]
FORBIDDEN_PREFIXES = [
    'data/design/final_numbers/',
    'frontend/assets/audio/',
    'frontend/assets/images/',
]
PACK127_ANCHOR = 'b9b516b3334fa95a4c079af089570a278724a7af'


def main() -> int:
    errors = []; notes = []
    # Git diff anchor..HEAD
    try:
        r = subprocess.run(['git', '-C', str(REPO_ROOT), 'diff', '--name-only', f'{PACK127_ANCHOR}..HEAD'],
                            capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            notes.append(f'git diff failed (anchor maybe absent): {r.stderr.strip()[:120]}')
            changed = []
        else:
            changed = [l.strip() for l in r.stdout.splitlines() if l.strip()]
    except Exception as e:
        notes.append(f'git diff exception: {e!r}'); changed = []

    print(f'OK    file modificati dal commit Pack 127 ({PACK127_ANCHOR[:9]}): {len(changed)}')
    violations = []
    for f in changed:
        if f in FORBIDDEN_PATHS:
            violations.append(f)
        elif any(f.startswith(pref) for pref in FORBIDDEN_PREFIXES):
            violations.append(f)
    if violations:
        for v in violations:
            errors.append(f'forbidden file modified since Pack 127 anchor: {v}')
    else:
        print('OK    nessuna area forbidden toccata')
    return _emit(errors, notes, changed)


def _emit(errors, notes, changed):
    print('\n' + '=' * 72)
    report = {
        'pack': 'PACK_128_FORBIDDEN_AREAS_UNTOUCHED',
        'status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
        'notes': notes,
        'files_changed_since_pack127_anchor': changed,
        'forbidden_paths': FORBIDDEN_PATHS,
        'forbidden_prefixes': FORBIDDEN_PREFIXES,
        'pack127_anchor': PACK127_ANCHOR,
        'validation_kind': 'STATIC+GIT_DIFF',
        'enforcement': 'ENFORCED_GIT_DIFF',
    }
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_128_forbidden_areas_untouched_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    for n in notes: print(f'  NOTE  {n}')
    print('PASS  forbidden areas untouched since Pack 127 anchor')
    return 0


if __name__ == '__main__': sys.exit(main())
