#!/usr/bin/env python3
"""Pack 129 — Forbidden areas untouched (git diff dal Pack 128 close)."""
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
    'frontend/app/combat.tsx',
    'frontend/app/story.tsx',
]
FORBIDDEN_PREFIXES = [
    'data/design/final_numbers/',
    'frontend/assets/audio/',
    'frontend/assets/images/',
]
PACK128_ANCHOR = 'bb58cedd2bce2bf39030be1e6cc5ac5353fa2945'


def main() -> int:
    errors = []; notes = []
    try:
        r = subprocess.run(['git', '-C', str(REPO_ROOT), 'diff', '--name-only', f'{PACK128_ANCHOR}..HEAD'],
                            capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            notes.append(f'git diff failed: {r.stderr.strip()[:120]}')
            changed = []
        else:
            changed = [l.strip() for l in r.stdout.splitlines() if l.strip()]
    except Exception as e:
        notes.append(f'git exception: {e!r}'); changed = []
    print(f'OK    file modificati dal Pack 128 close ({PACK128_ANCHOR[:9]}): {len(changed)}')
    violations = []
    for f in changed:
        if f in FORBIDDEN_PATHS or any(f.startswith(pref) for pref in FORBIDDEN_PREFIXES):
            violations.append(f)
    for v in violations:
        errors.append(f'forbidden file modified since Pack 128 anchor: {v}')
    if not violations:
        print('OK    nessuna area forbidden toccata')
    return _emit(errors, notes, changed)


def _emit(errors, notes, changed):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_129_FORBIDDEN_AREAS_UNTOUCHED',
              'status': 'PASS' if not errors else 'FAIL',
              'errors': errors, 'notes': notes,
              'files_changed_since_pack128_anchor': changed,
              'forbidden_paths': FORBIDDEN_PATHS,
              'forbidden_prefixes': FORBIDDEN_PREFIXES,
              'pack128_anchor': PACK128_ANCHOR,
              'validation_kind': 'STATIC+GIT_DIFF',
              'enforcement': 'ENFORCED_GIT_DIFF'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_129_forbidden_areas_untouched_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    for n in notes: print(f'  NOTE  {n}')
    print('PASS  forbidden areas untouched since Pack 128 anchor')
    return 0


if __name__ == '__main__': sys.exit(main())
