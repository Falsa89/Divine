#!/usr/bin/env python3
"""Pack 130 — Forbidden areas untouched (git diff dal Pack 129 close)."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_PATHS = ['backend/battle_engine.py', 'backend/battle_core.py',
                   'backend/game_systems.py', 'backend/.env',
                   'data/design/heroes_master.json',
                   'frontend/app/combat.tsx', 'frontend/app/story.tsx',
                   'backend/routes/v96_team_formation.py']
FORBIDDEN_PREFIXES = ['data/design/final_numbers/', 'frontend/assets/audio/', 'frontend/assets/images/']
PACK129_ANCHOR = 'bcd72f45751d875edfc2d65a6a4b5dcbce966356'


def main() -> int:
    errors = []; notes = []
    try:
        r = subprocess.run(['git', '-C', str(REPO_ROOT), 'diff', '--name-only', f'{PACK129_ANCHOR}..HEAD'],
                            capture_output=True, text=True, timeout=10)
        changed = [l.strip() for l in r.stdout.splitlines() if l.strip()] if r.returncode == 0 else []
    except Exception as e:
        notes.append(f'git exception: {e!r}'); changed = []
    print(f'OK    file modificati dal Pack 129 close: {len(changed)}')
    violations = []
    for f in changed:
        if f in FORBIDDEN_PATHS or any(f.startswith(pref) for pref in FORBIDDEN_PREFIXES):
            violations.append(f); errors.append(f'forbidden file modified: {f}')
    if not violations: print('OK    no forbidden area touched')
    return _emit(errors, notes, changed)


def _emit(errors, notes, changed):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_130_FORBIDDEN_AREAS_UNTOUCHED',
              'status': 'PASS' if not errors else 'FAIL', 'errors': errors, 'notes': notes,
              'files_changed_since_pack129_anchor': changed,
              'forbidden_paths': FORBIDDEN_PATHS,
              'forbidden_prefixes': FORBIDDEN_PREFIXES,
              'pack129_anchor': PACK129_ANCHOR,
              'validation_kind': 'STATIC+GIT_DIFF',
              'enforcement': 'ENFORCED_GIT_DIFF'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_130_forbidden_areas_untouched_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  forbidden areas untouched since Pack 129 anchor')
    return 0


if __name__ == '__main__': sys.exit(main())
