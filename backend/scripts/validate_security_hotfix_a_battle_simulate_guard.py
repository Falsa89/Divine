#!/usr/bin/env python3
"""SECURITY_HOTFIX_A — Validate /api/battle/simulate fail-closed guard."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FILE = REPO_ROOT / 'backend' / 'battle_engine.py'


def main():
    errs = []
    src = FILE.read_text(encoding='utf-8')
    # Trova la def della route simulate (regex tollerante a doc/decorators tra route e def).
    m = re.search(r'@router\.post\(\s*[\'"]/battle/simulate[\'"]\s*\)[^\n]*\n[^\n]*async def simulate_battle_endpoint\b', src)
    if not m:
        return _emit(['simulate_battle_endpoint route not found'])
    body_start = m.end()
    # Trova il primo db.teams.find_one dopo la def.
    db_pos = src.find('db.teams.find_one', body_start)
    if db_pos < 0:
        return _emit(['db.teams.find_one not found after route def'])
    body_segment = src[body_start:db_pos]
    required_tokens = [
        'BATTLE_SIMULATE_LIVE_DISABLED_PRE_QA',
        'BATTLE_SIMULATE_LIVE_ENABLED',
        "status_code=423",
        'SECURITY_HOTFIX_A',
    ]
    for tk in required_tokens:
        if tk not in body_segment:
            errs.append(f'guard token missing before db.teams.find_one: {tk}')
    return _emit(errs)


def _emit(errs):
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    rep = {'pack': 'SECURITY_HOTFIX_A_BATTLE_SIMULATE_GUARD',
           'status': 'PASS' if not errs else 'FAIL', 'errors': errs,
           'enforcement': 'ENFORCED_STATIC'}
    (out / 'security_hotfix_a_battle_simulate_guard_report.json').write_text(
        json.dumps(rep, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print('PASS  battle/simulate fail-closed guard present before any DB read')
    return 0


if __name__ == '__main__': sys.exit(main())
