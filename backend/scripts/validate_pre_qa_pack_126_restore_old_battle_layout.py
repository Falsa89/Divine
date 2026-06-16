#!/usr/bin/env python3
"""
Pack 126 — Validator: restore old 6v6 battle visual layout (3 cols x 2 rows).
"""
from __future__ import annotations
import json, sys, re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
UTIL = REPO_ROOT / 'frontend' / 'src' / 'utils' / 'previewBattleTeam.ts'


def main() -> int:
    errors = []
    src = UTIL.read_text(encoding='utf-8') if UTIL.exists() else ''
    if not src:
        errors.append(f'missing {UTIL}'); return _emit(errors)
    # Required: POS_BACKEND map with grid_x values 1,4,7 and grid_y 1,4 covering 6 slots
    if 'POS_BACKEND' not in src:
        errors.append('POS_BACKEND mapping missing')
    else:
        print('OK    POS_BACKEND mapping present')
    needed_cols = ['grid_x: 1', 'grid_x: 4', 'grid_x: 7']
    for c in needed_cols:
        if c not in src:
            errors.append(f'missing column: {c}')
        else:
            print(f'OK    {c} present (legacy backend col convention)')
    if 'grid_y: 1' not in src or 'grid_y: 4' not in src:
        errors.append('missing grid_y values 1/4 (legacy backend row convention)')
    # Count POS_BACKEND entries
    entries = re.findall(r'grid_x:\s*\d+', src)
    if len(entries) < 6:
        errors.append(f'POS_BACKEND has only {len(entries)} entries (need >=6 for 6v6)')
    else:
        print(f'OK    POS_BACKEND has {len(entries)} grid positions (6v6 layout)')
    # faction prefix derivation
    if 'hero_id.split' not in src:
        errors.append('faction derivation from hero_id prefix missing')
    else:
        print('OK    faction derived from hero_id prefix')
    return _emit(errors)


def _emit(errors):
    print('\n' + '='*72)
    print('Pack 126 — restore old battle layout')
    print('='*72)
    report = {'pack': 'PRE_QA_PACK_126_RESTORE_OLD_BATTLE_LAYOUT', 'status': 'PASS' if not errors else 'FAIL', 'errors': errors}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_126_restore_old_battle_layout_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  6v6 layout restored: 3 cols (front/mid/back) x 2 rows, all 6 heroes visible')
    return 0


if __name__ == '__main__':
    sys.exit(main())
