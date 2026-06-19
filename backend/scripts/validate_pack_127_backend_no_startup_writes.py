#!/usr/bin/env python3
"""Pack 127 — Backend startup writes detection (STATIC)."""
from __future__ import annotations
import json, sys, re
from pathlib import Path

REPO_ROOT=Path(__file__).resolve().parents[2]
SERVER=REPO_ROOT/'backend'/'server.py'

# FORBIDDEN = mutazioni vietate su user data / live economy a startup
FORBIDDEN_STARTUP=['db.users.insert','db.users.update','db.gacha_pulls.insert','db.transactions.insert','db.mail.insert','grant_starter_heroes(','seed_legacy_heroes(']
# WARNING = mutazioni catalogo a startup (non vietate ma da gate-are in Pack 128)
WARNING_STARTUP=['db.heroes.insert','db.heroes.delete','db.heroes.update','db.servers.insert','db.servers.update']


def _extract_startup_bodies(src: str) -> list:
    """Estrae i corpi delle funzioni decorate con @app.on_event("startup") o
    lifespan/asynccontextmanager. Si ferma alla prossima riga che inizia con
    '@' o 'def '/'async def ' a colonna 0, per non ingoiare le route adiacenti.
    """
    bodies = []
    lines = src.splitlines()
    i = 0
    decor_re = re.compile(r'^@.*on_event\(["\']startup["\']\)|^@asynccontextmanager|^.*lifespan\s*=\s*lifespan')
    while i < len(lines):
        if decor_re.search(lines[i]):
            # Trova def/async def successiva
            j = i + 1
            while j < len(lines) and not re.match(r'^(async\s+def|def)\s+', lines[j]):
                j += 1
            if j >= len(lines):
                i += 1; continue
            # Corpo: indentato. Termina alla prossima riga non vuota con indent 0.
            k = j + 1
            while k < len(lines):
                ln = lines[k]
                if ln.strip() == '':
                    k += 1; continue
                if re.match(r'^\S', ln):  # indent 0 → fine funzione
                    break
                k += 1
            bodies.append('\n'.join(lines[j:k]))
            i = k
        else:
            i += 1
    return bodies


def main()->int:
    errors=[]; src=SERVER.read_text(encoding='utf-8') if SERVER.exists() else ''
    if not src: errors.append('server.py missing'); return _emit(errors, [])
    bodies = _extract_startup_bodies(src)
    if not bodies:
        print('NOTE  no startup handler found')
    else:
        print(f'OK    startup handlers found: {len(bodies)}')
    for idx, blob in enumerate(bodies):
        for fp in FORBIDDEN_STARTUP:
            if fp in blob:
                errors.append(f'startup handler #{idx+1} contains forbidden write: `{fp}`')
    # Warning scan: catalog auto-seed sin gate (non FAIL, finding per Pack 128)
    warnings=[]
    for idx, blob in enumerate(bodies):
        # Check env gate presence in body
        env_gated = ('os.environ.get' in blob) and any(x in blob for x in ['ENABLED','DISABLED','KILL_SWITCH','ALLOWLIST'])
        for wp in WARNING_STARTUP:
            if wp in blob and not env_gated:
                warnings.append(f'startup handler #{idx+1}: catalog mutation `{wp}` without env gate (Pack 128 hardening required)')
    print(f'OK    startup write scan: {len(FORBIDDEN_STARTUP)} forbidden + {len(WARNING_STARTUP)} warning patterns checked against {len(bodies)} handler bodies')
    if warnings:
        for w in warnings: print(f'  NOTE  {w}')
    # Bot kill switch hint
    if 'BOTS_DISABLED' not in src and 'BOT_KILL_SWITCH' not in src:
        print('NOTE  server.py does not explicitly read BOTS_DISABLED/BOT_KILL_SWITCH — verify bot routes for env gate')
    return _emit(errors, warnings)


def _emit(errors, warnings):
    print('\n'+'='*72)
    report={'pack':'PACK_127_BACKEND_NO_STARTUP_WRITES','status':'PASS' if not errors else 'FAIL','errors':errors,'warnings':warnings,'validation_kind':'STATIC','enforcement':'forbidden_user_data_writes_blocked_catalog_seed_pending_pack_128'}
    out=REPO_ROOT/'backend'/'scripts'/'reports'; out.mkdir(parents=True,exist_ok=True)
    (out/'pack_127_backend_no_startup_writes_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    if warnings:
        print(f'PASS (con {len(warnings)} NOTE per Pack 128) — no forbidden user-data startup writes')
    else:
        print('PASS  no dangerous startup writes detected (static)')
    return 0

if __name__=='__main__': sys.exit(main())
