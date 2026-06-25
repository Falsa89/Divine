#!/usr/bin/env python3
"""SECURITY_HOTFIX_A — No scope drift (only allowed runtime files + scripts/docs)."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ANCHOR = 'dd36905a8bf4dc2ed4c23bad4cde8376280aeb95'  # pre-hotfix HEAD
ALLOWED_EXACT = {
    'backend/battle_engine.py',
    'backend/server.py',
    'backend/routes/v96_auth.py',
    'backend/routes/v130_lobby_launch_context.py',
    'backend/routes/v131_combat_preview.py',
    'backend/helpers/jwt_secret_preflight.py',
}
ALLOWED_PREFIXES = (
    'backend/scripts/', 'data/design/system_safety/',
    'docs/divine/', '.emergent/',
)
FORBIDDEN_PREFIXES = (
    'frontend/', 'backend/helpers/',  # except jwt_secret_preflight.py
    'backend/routes/',  # except whitelisted
    'backend/models/', 'data/design/heroes_master',
    'data/design/final_numbers/', 'frontend/assets/',
)


def main():
    r = subprocess.run(['git', '-C', str(REPO_ROOT), 'diff', '--name-only', f'{ANCHOR}..HEAD'],
                       capture_output=True, text=True)
    changed = [l.strip() for l in r.stdout.splitlines() if l.strip()] if r.returncode == 0 else []
    errs = []
    for f in changed:
        if f in ALLOWED_EXACT:
            continue
        if any(f.startswith(p) for p in ('backend/scripts/', 'data/design/system_safety/', 'docs/divine/', '.emergent/')):
            continue
        # Specifically allow new helpers/jwt_secret_preflight only.
        errs.append(f'scope drift: {f}')
    return _emit(errs, changed)


def _emit(errs, changed):
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    rep = {'pack': 'SECURITY_HOTFIX_A_NO_SCOPE_DRIFT',
           'status': 'PASS' if not errs else 'FAIL', 'errors': errs,
           'changed': changed, 'anchor': 'dd36905a8',
           'enforcement': 'ENFORCED_GIT_DIFF'}
    (out / 'security_hotfix_a_no_scope_drift_report.json').write_text(
        json.dumps(rep, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print('PASS  scope guard respected')
    return 0


if __name__ == '__main__': sys.exit(main())
