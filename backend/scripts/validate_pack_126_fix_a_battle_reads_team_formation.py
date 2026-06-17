#!/usr/bin/env python3
"""Pack 126-FIX-A — Validator: battle.tsx must read team.team_formation (Pack 125+) not only team.formation (legacy)."""
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
    # Required: union access team?.team_formation || team?.formation
    if 'team?.team_formation' not in src and 'team?.team_formation || team?.formation' not in src and 'team_formation || team?.formation' not in src and 'team_formation || team' not in src:
        errors.append('battle.tsx does not read team.team_formation (Pack 125+ key)')
    else:
        print('OK    battle.tsx reads team.team_formation (Pack 125+ key)')
    # Required: savedFormation normalized variable
    if 'savedFormation' not in src:
        errors.append('battle.tsx does not introduce savedFormation normalized variable')
    else:
        print('OK    savedFormation normalized variable present')
    # Anti-regression: must NOT only check team?.formation?.length
    # i.e. must not rely on `team.formation` exclusively without union.
    # We allow `team.formation` if union with team_formation exists.
    if 'team.team_formation' not in src and 'team_formation' not in src:
        errors.append('battle.tsx must reference team_formation at least once')
    return _emit(errors)


def _emit(errors):
    print('\n' + '='*72)
    print('Pack 126-FIX-A — battle.tsx reads team_formation contract')
    print('='*72)
    report = {'pack':'PACK_126_FIX_A_BATTLE_READS_TEAM_FORMATION','status':'PASS' if not errors else 'FAIL','errors':errors}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_126_fix_a_battle_reads_team_formation_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  battle.tsx normalizes team_formation (Pack 125+) + formation (legacy)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
