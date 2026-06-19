#!/usr/bin/env python3
"""Pack 127 — Backend startup writes detection (STATIC)."""
from __future__ import annotations
import json, sys, re
from pathlib import Path

REPO_ROOT=Path(__file__).resolve().parents[2]
SERVER=REPO_ROOT/'backend'/'server.py'

FORBIDDEN_STARTUP=['db.users.insert','db.users.update','db.gacha_pulls.insert','db.transactions.insert','db.mail.insert','grant_starter_heroes(','seed_legacy_heroes(']


def main()->int:
    errors=[]; src=SERVER.read_text(encoding='utf-8') if SERVER.exists() else ''
    if not src: errors.append('server.py missing'); return _emit(errors)
    # Find @app.on_event("startup") or lifespan handlers
    m=re.search(r'(on_event\(["\']startup["\']\)|lifespan|@asynccontextmanager)[\s\S]{0,8000}',src)
    blob = m.group(0) if m else ''
    if not blob:
        print('NOTE  no startup handler found')
    for fp in FORBIDDEN_STARTUP:
        if fp in blob:
            errors.append(f'startup handler contains forbidden write: `{fp}`')
    print(f'OK    startup write scan: {len(FORBIDDEN_STARTUP)} patterns checked')
    # Bot kill switch hint
    if 'BOTS_DISABLED' not in src and 'BOT_KILL_SWITCH' not in src:
        print('NOTE  server.py does not explicitly read BOTS_DISABLED/BOT_KILL_SWITCH — verify bot routes for env gate')
    return _emit(errors)


def _emit(errors):
    print('\n'+'='*72)
    report={'pack':'PACK_127_BACKEND_NO_STARTUP_WRITES','status':'PASS' if not errors else 'FAIL','errors':errors,'validation_kind':'STATIC'}
    out=REPO_ROOT/'backend'/'scripts'/'reports'; out.mkdir(parents=True,exist_ok=True)
    (out/'pack_127_backend_no_startup_writes_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  no dangerous startup writes detected (static)')
    return 0

if __name__=='__main__': sys.exit(main())
