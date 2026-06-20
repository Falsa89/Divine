#!/usr/bin/env python3
"""Pack 132 — No frontend or runtime changes validator.

Uses git diff vs Pack 131 final SHA to ensure Pack 132 only changes
scripts/markers/docs.
"""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ANCHOR = '588f1bfca1da7e190f642a1892897e4c5d99aa6d'  # Pack 131 micro doc fix
ALLOWED_PREFIXES = (
    'backend/scripts/',
    'data/design/system_safety/',
    'docs/divine/',
    '.emergent/',  # non-functional timestamp only
)
FORBIDDEN_PATHS_EXACT = {
    'backend/server.py', 'backend/.env', 'backend/battle_engine.py',
    'backend/battle_core.py', 'backend/game_systems.py',
    'frontend/app/combat.tsx', 'frontend/app/story.tsx',
}


def main():
    errs = []
    r = subprocess.run(['git', '-C', str(REPO_ROOT), 'diff', '--name-only', f'{ANCHOR}..HEAD'],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return _emit([f'git diff failed: {r.stderr.strip()}'], [])
    changed = [l.strip() for l in r.stdout.splitlines() if l.strip()]
    for f in changed:
        if f in FORBIDDEN_PATHS_EXACT:
            errs.append(f'forbidden runtime file modified: {f}')
            continue
        if f.startswith('frontend/'):
            errs.append(f'frontend modified: {f}')
            continue
        if f.startswith('backend/helpers/') or f.startswith('backend/routes/') or f.startswith('backend/models/'):
            errs.append(f'backend runtime modified: {f}')
            continue
        if not any(f.startswith(p) for p in ALLOWED_PREFIXES):
            errs.append(f'file outside Pack 132 allowed scope: {f}')
    return _emit(errs, changed)


def _emit(errs, changed):
    report = {'pack': 'PACK_132_NO_FRONTEND_RUNTIME_CHANGES',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'changed_since_pack131_final': changed,
              'pack131_final_anchor': '588f1bfca1da7e190f642a1892897e4c5d99aa6d',
              'validation_kind': 'STATIC+GIT_DIFF',
              'enforcement': 'ENFORCED_GIT_DIFF'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_132_no_frontend_runtime_changes_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs:
            print(f'FAIL {e}')
        return 1
    print('PASS  no frontend / runtime changes in Pack 132 scope')
    return 0


if __name__ == '__main__':
    sys.exit(main())
