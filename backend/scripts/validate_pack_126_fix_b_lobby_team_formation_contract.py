#!/usr/bin/env python3
"""Pack 126-FIX-B — Validator: pre-battle-lobby supports team_formation + hero_id/col/row + triple lookup."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
T = REPO_ROOT / 'frontend' / 'app' / 'pre-battle-lobby.tsx'

REQUIRED = [
    ('d.team_formation', 'reads team_formation (Pack 125+)'),
    ('(d as any).formation', 'fallback to legacy formation'),
    ('e.user_hero_id || e.hero_id || e.canonical_id', 'triple hero key fallback in filter'),
    ('hh?.id === heroKey || hh?.hero_id === heroKey || hh?.canonical_id === heroKey', 'triple lookup predicate'),
    ('heroMap[String(h.hero_id)]', 'heroMap indexed by hero_id'),
    ('heroMap[String(h.canonical_id)]', 'heroMap indexed by canonical_id'),
    ('getCanonicalBackendUrl', 'uses canonical backend URL resolver (FIX D)'),
    ('PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER', 'honest blocker when no real team'),
]


def main() -> int:
    errors = []
    src = T.read_text(encoding='utf-8') if T.exists() else ''
    for pat, desc in REQUIRED:
        if pat not in src:
            errors.append(f'missing `{pat}`: {desc}')
        else:
            print(f'OK    {desc}')
    # Anti-regression: must NOT only check e.user_hero_id without union
    if 'e.user_hero_id)' in src and 'e.user_hero_id || e.hero_id' not in src:
        errors.append('still filters by e.user_hero_id alone (Pack 125+ uses hero_id)')
    return _emit(errors)


def _emit(errors):
    print('\n' + '='*72)
    report = {'pack':'PACK_126_FIX_B_LOBBY_TEAM_FORMATION_CONTRACT','status':'PASS' if not errors else 'FAIL','errors':errors}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_126_fix_b_lobby_team_formation_contract_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  pre-battle-lobby supports team_formation + hero_id/col/row + triple lookup + canonical URL resolver')
    return 0

if __name__ == '__main__': sys.exit(main())
