#!/usr/bin/env python3
"""POST_CHAIN — No runtime scope drift validator.

Uses git diff vs Pack 133 micro doc fix (1735a03c7) to ensure post-chain
changes stay within: backend/scripts/, data/design/system_safety/,
docs/divine/, .emergent/ (timestamp only).
"""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ANCHOR = '1735a03c7562a18a255503eac8a95defcf16f92b'  # Pack 133 micro doc fix
ALLOWED_PREFIXES = (
    'backend/scripts/',
    'data/design/system_safety/',
    'docs/divine/',
    '.emergent/',
)
FORBIDDEN_EXACT = {
    'backend/server.py', 'backend/.env',
    'backend/battle_engine.py', 'backend/battle_core.py', 'backend/game_systems.py',
}
FORBIDDEN_PREFIXES = (
    'backend/helpers/', 'backend/routes/', 'backend/models/',
    'frontend/', 'data/design/final_numbers/',
    'data/design/heroes_master',
    'frontend/assets/audio/', 'frontend/assets/images/',
)


def main():
    errs = []
    r = subprocess.run(['git', '-C', str(REPO_ROOT), 'diff', '--name-only', f'{ANCHOR}..HEAD'],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return _emit([f'git diff failed: {r.stderr.strip()}'], [])
    changed = [l.strip() for l in r.stdout.splitlines() if l.strip()]
    for f in changed:
        if f in FORBIDDEN_EXACT or any(f.startswith(p) for p in FORBIDDEN_PREFIXES):
            errs.append(f'forbidden runtime: {f}')
            continue
        if not any(f.startswith(p) for p in ALLOWED_PREFIXES):
            errs.append(f'outside allowed scope: {f}')
    return _emit(errs, changed)


def _emit(errs, changed):
    report = {'pack': 'POST_CHAIN_NO_RUNTIME_SCOPE_DRIFT',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'changed_since_pack133_final': changed,
              'anchor': '1735a03c7562a18a255503eac8a95defcf16f92b',
              'validation_kind': 'STATIC+GIT_DIFF',
              'enforcement': 'ENFORCED_GIT_DIFF'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'post_chain_no_runtime_scope_drift_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print('PASS  no runtime scope drift since Pack 133 final')
    return 0


if __name__ == '__main__': sys.exit(main())
