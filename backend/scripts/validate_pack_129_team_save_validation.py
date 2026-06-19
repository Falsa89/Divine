#!/usr/bin/env python3
"""Pack 129 — Team save validations checklist (STATIC).

Verifica che il route Pack 125 valida i payload secondo Pack 129 §7.3.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTE = REPO_ROOT / 'backend' / 'routes' / 'v96_team_formation.py'

REQUIRED_VALIDATIONS = {
    'auth required': 'Depends(get_current_user)',
    'team size max 6': 'len(body.team_formation) > 6',
    'slot (col,row) unique': 'len(set(positions)) != len(positions)',
    'hero_id unique': 'len(set(hero_ids)) != len(hero_ids)',
    'PSP fail-closed': 'PLAYER_SERVER_PROFILE_REQUIRED',
    'ownership check': 'OWNERSHIP_VALIDATION_FAILED',
    'col range 0-2': 'ge=0, le=2',
}


def main() -> int:
    errors = []; notes = []
    if not ROUTE.exists(): errors.append('v96_team_formation.py missing'); return _emit(errors, notes)
    src = ROUTE.read_text(encoding='utf-8')
    for name, signal in REQUIRED_VALIDATIONS.items():
        if signal not in src:
            errors.append(f'validation `{name}` not found (signal `{signal}` missing)')
        else:
            print(f'OK    {name} → signal present')
    return _emit(errors, notes)


def _emit(errors, notes):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_129_TEAM_SAVE_VALIDATION',
              'status': 'PASS' if not errors else 'FAIL',
              'errors': errors, 'notes': notes,
              'required_validations': list(REQUIRED_VALIDATIONS.keys()),
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED_ALL_REQUIRED_VALIDATIONS_PRESENT_IN_PACK_125_ENDPOINT'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_129_team_save_validation_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  team save validations complete (auth/size/slot/duplicate/PSP/ownership)')
    return 0


if __name__ == '__main__': sys.exit(main())
