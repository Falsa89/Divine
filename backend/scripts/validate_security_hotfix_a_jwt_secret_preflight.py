#!/usr/bin/env python3
"""SECURITY_HOTFIX_A — Validate JWT_SECRET preflight (no legacy fallback in runtime)."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_FILES = [
    REPO_ROOT / 'backend' / 'server.py',
    REPO_ROOT / 'backend' / 'routes' / 'v96_auth.py',
    REPO_ROOT / 'backend' / 'routes' / 'v130_lobby_launch_context.py',
    REPO_ROOT / 'backend' / 'routes' / 'v131_combat_preview.py',
]
HELPER = REPO_ROOT / 'backend' / 'helpers' / 'jwt_secret_preflight.py'
LEGACY = 'divine_waifus_secret_key_2025'


def main():
    errs = []
    if not HELPER.exists():
        errs.append('helpers/jwt_secret_preflight.py missing')
    else:
        helper_src = HELPER.read_text(encoding='utf-8')
        for tok in ['LEGACY_FALLBACK', 'RuntimeError', 'ALLOW_INSECURE_DEV_JWT', 'ENV_PROFILE']:
            if tok not in helper_src:
                errs.append(f'helper missing token: {tok}')
    for f in RUNTIME_FILES:
        if not f.exists():
            errs.append(f'missing: {f.relative_to(REPO_ROOT)}')
            continue
        src = f.read_text(encoding='utf-8')
        rel = str(f.relative_to(REPO_ROOT))
        if 'resolve_jwt_secret' not in src:
            errs.append(f'{rel}: does not import/use resolve_jwt_secret()')
        if 'os.getenv("JWT_SECRET", "' + LEGACY + '")' in src or "os.getenv('JWT_SECRET', '" + LEGACY + "')" in src:
            errs.append(f'{rel}: still uses legacy fallback')
        if LEGACY in src and 'jwt_secret_preflight' not in rel:
            errs.append(f'{rel}: legacy literal still present in runtime file')
    return _emit(errs)


def _emit(errs):
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    rep = {'pack': 'SECURITY_HOTFIX_A_JWT_SECRET_PREFLIGHT',
           'status': 'PASS' if not errs else 'FAIL', 'errors': errs,
           'enforcement': 'ENFORCED_STATIC'}
    (out / 'security_hotfix_a_jwt_secret_preflight_report.json').write_text(
        json.dumps(rep, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print('PASS  JWT_SECRET preflight active; no legacy fallback in runtime files')
    return 0


if __name__ == '__main__': sys.exit(main())
