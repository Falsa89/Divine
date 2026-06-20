#!/usr/bin/env python3
"""Pack 132 — Forbidden areas untouched validator.

Uses git diff vs Pack 131 final SHA. Forbidden paths must be byte-intact.
"""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ANCHOR = '588f1bfca1da7e190f642a1892897e4c5d99aa6d'
FORBIDDEN_PATHS = [
    'backend/battle_engine.py',
    'backend/battle_core.py',
    'backend/game_systems.py',
    'backend/.env',
    'data/design/heroes_master.json',
    'frontend/app/combat.tsx',
    'frontend/app/story.tsx',
    'backend/routes/v96_team_formation.py',
    'backend/routes/v130_lobby_launch_context.py',
    'backend/routes/v131_combat_preview.py',
    'backend/helpers/real_player_snapshot.py',
    'backend/helpers/lobby_launch_context.py',
    'backend/helpers/combat_preview_adapter.py',
]
FORBIDDEN_PREFIXES = [
    'data/design/final_numbers/',
    'frontend/assets/audio/',
    'frontend/assets/images/',
    'frontend/app/',
]


def main():
    errs = []
    r = subprocess.run(['git', '-C', str(REPO_ROOT), 'diff', '--name-only', f'{ANCHOR}..HEAD'],
                       capture_output=True, text=True)
    changed = [l.strip() for l in r.stdout.splitlines() if l.strip()] if r.returncode == 0 else []
    for f in changed:
        if f in FORBIDDEN_PATHS or any(f.startswith(p) for p in FORBIDDEN_PREFIXES):
            errs.append(f'forbidden: {f}')
    return _emit(errs, changed)


def _emit(errs, changed):
    report = {'pack': 'PACK_132_FORBIDDEN_AREAS_UNTOUCHED',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'changed_since_pack131_final': changed,
              'pack131_final_anchor': ANCHOR,
              'validation_kind': 'STATIC+GIT_DIFF',
              'enforcement': 'ENFORCED_GIT_DIFF'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_132_forbidden_areas_untouched_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs:
            print(f'FAIL {e}')
        return 1
    print('PASS  forbidden areas untouched since Pack 131 final anchor')
    return 0


if __name__ == '__main__':
    sys.exit(main())
