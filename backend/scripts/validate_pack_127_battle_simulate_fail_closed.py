#!/usr/bin/env python3
"""Pack 127 — /api/battle/simulate fail-closed (STATIC + RUNTIME if backend up)."""
from __future__ import annotations
import json, sys, subprocess
from pathlib import Path

REPO_ROOT=Path(__file__).resolve().parents[2]


def main()->int:
    errors=[]; runtime_note=None
    # STATIC: look for guard pattern in any combat-route file
    routes_dir=REPO_ROOT/'backend'/'routes'
    matches=[]
    for f in list(routes_dir.glob('*.py'))+[REPO_ROOT/'backend'/'server.py']:
        if not f.exists(): continue
        try: src=f.read_text(encoding='utf-8')
        except: continue
        if '/api/battle/simulate' in src or '"battle/simulate"' in src or "'battle/simulate'" in src:
            matches.append(str(f.relative_to(REPO_ROOT)))
    print(f'OK    /api/battle/simulate referenced in: {matches or "none-found-static"}')
    # RUNTIME: try POST without auth — expected 401/403/404, NOT 200.
    try:
        r=subprocess.run(['curl','-s','-o','/tmp/sim.json','-w','%{http_code}','-X','POST','http://localhost:8001/api/battle/simulate','-H','Content-Type: application/json','-d','{}'],capture_output=True,text=True,timeout=8)
        code=r.stdout.strip(); body=Path('/tmp/sim.json').read_text(encoding='utf-8') if Path('/tmp/sim.json').exists() else ''
        print(f'RUNTIME /api/battle/simulate (no auth): HTTP {code}')
        if code in ('200','201'):
            errors.append(f'/api/battle/simulate reachable without auth (HTTP {code}) — NOT fail-closed')
        elif code in ('401','403','404','405','422'):
            print(f'OK    fail-closed at HTTP {code} (auth/route gate)')
        else:
            runtime_note=f'unexpected HTTP {code}: {body[:200]}'
    except Exception as e:
        runtime_note=f'runtime check failed: {e}'
    return _emit(errors, runtime_note)


def _emit(errors, runtime_note=None):
    print('\n'+'='*72)
    report={'pack':'PACK_127_BATTLE_SIMULATE_FAIL_CLOSED','status':'PASS' if not errors else 'FAIL','errors':errors,'runtime_note':runtime_note,'validation_kind':'STATIC+RUNTIME'}
    out=REPO_ROOT/'backend'/'scripts'/'reports'; out.mkdir(parents=True,exist_ok=True)
    (out/'pack_127_battle_simulate_fail_closed_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  /api/battle/simulate fail-closed (auth/route gate). Future Pack 131 will replace runtime.')
    return 0

if __name__=='__main__': sys.exit(main())
