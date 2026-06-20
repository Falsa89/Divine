#!/usr/bin/env python3
"""Pack 133 — No runtime/frontend/backend changes validator (git diff)."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ANCHOR = 'a15915ca16c31332df35b89f0f365d48fcffc7ca'  # Pack 132 micro doc fix
ALLOWED_PREFIXES = (
    'backend/scripts/', 'data/design/system_safety/', 'docs/divine/',
    '.emergent/',
)
FORBIDDEN_PATHS = {
    'backend/server.py', 'backend/.env', 'backend/battle_engine.py',
    'backend/battle_core.py', 'backend/game_systems.py',
}


def main():
    errs = []
    r = subprocess.run(['git', '-C', str(REPO_ROOT), 'diff', '--name-only', f'{ANCHOR}..HEAD'],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return _emit([f'git diff failed: {r.stderr.strip()}'], [])
    changed = [l.strip() for l in r.stdout.splitlines() if l.strip()]
    for f in changed:
        if f in FORBIDDEN_PATHS:
            errs.append(f'forbidden runtime: {f}')
            continue
        if f.startswith('frontend/'):
            errs.append(f'frontend modified: {f}')
            continue
        if f.startswith('backend/helpers/') or f.startswith('backend/routes/') or f.startswith('backend/models/'):
            errs.append(f'backend runtime modified: {f}')
            continue
        if not any(f.startswith(p) for p in ALLOWED_PREFIXES):
            errs.append(f'file outside allowed scope: {f}')
    return _emit(errs, changed)


def _emit(errs, changed):
    report = {'pack': 'PACK_133_NO_RUNTIME_FRONTEND_BACKEND_CHANGES',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs, 'changed_since_pack132_final': changed,
              'anchor': 'a15915ca16c31332df35b89f0f365d48fcffc7ca',
              'validation_kind': 'STATIC+GIT_DIFF', 'enforcement': 'ENFORCED_GIT_DIFF'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_133_no_runtime_frontend_backend_changes_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print('PASS  no runtime/frontend/backend changes since Pack 132 final')
    return 0


if __name__ == '__main__': sys.exit(main())
