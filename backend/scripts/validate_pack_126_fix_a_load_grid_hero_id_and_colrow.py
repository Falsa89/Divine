#!/usr/bin/env python3
"""Pack 126-FIX-A — Validator: load grid must support hero_id (Pack 125+) in addition to user_hero_id (legacy)."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
T = REPO_ROOT / 'frontend' / 'app' / '(tabs)' / 'battle.tsx'


def main() -> int:
    errors = []
    src = T.read_text(encoding='utf-8') if T.exists() else ''
    if not src:
        errors.append(f'missing {T}'); return _emit(errors)
    # Required: savedHeroKey union
    union_patterns = [
        ('savedHeroKey', 'savedHeroKey variable'),
        ('f?.user_hero_id || f?.hero_id', 'savedHeroKey union user_hero_id|hero_id'),
    ]
    for pat, desc in union_patterns:
        if pat not in src:
            errors.append(f'missing `{pat}`: {desc}')
        else:
            print(f'OK    {desc}')
    # Required: triple lookup x.id | x.hero_id | x.canonical_id
    if 'x?.id === savedHeroKey' not in src and 'x.id === savedHeroKey' not in src:
        errors.append('missing lookup x.id === savedHeroKey')
    else:
        print('OK    lookup by x.id present')
    if 'x?.hero_id === savedHeroKey' not in src and 'x.hero_id === savedHeroKey' not in src:
        errors.append('missing fallback lookup x.hero_id === savedHeroKey')
    else:
        print('OK    fallback lookup by x.hero_id present')
    if 'canonical_id' not in src:
        errors.append('missing canonical_id fallback')
    else:
        print('OK    canonical_id fallback present')
    # Required: col/row direct path
    if "typeof f.col === 'number' && typeof f.row === 'number'" not in src:
        errors.append('missing col/row direct mapping (Pack 125+ slot format)')
    else:
        print('OK    col/row direct mapping present')
    # Required: legacy x/y still supported
    if "typeof f.x === 'number' && typeof f.y === 'number'" not in src:
        errors.append('missing legacy x/y mapping')
    else:
        print('OK    legacy x/y mapping present')
    # Required: slot_index still supported
    if 'slot_index' not in src:
        errors.append('missing slot_index mapping')
    else:
        print('OK    slot_index mapping present')
    return _emit(errors)


def _emit(errors):
    print('\n' + '='*72)
    print('Pack 126-FIX-A — load grid supports hero_id + col/row')
    print('='*72)
    report = {'pack':'PACK_126_FIX_A_LOAD_GRID_HERO_ID_AND_COLROW','status':'PASS' if not errors else 'FAIL','errors':errors}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_126_fix_a_load_grid_hero_id_and_colrow_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  load grid supports hero_id + col/row + legacy x/y + slot_index + canonical_id')
    return 0


if __name__ == '__main__':
    sys.exit(main())
