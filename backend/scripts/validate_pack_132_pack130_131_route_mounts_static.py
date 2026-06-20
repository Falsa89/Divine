#!/usr/bin/env python3
"""Pack 132 — Static check: server.py mounts Pack 130 and Pack 131 routers.

Does NOT modify server.py. Read-only.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVER = REPO_ROOT / 'backend' / 'server.py'
REQUIRED_TOKENS = [
    ('v130_lobby_launch_context', 'Pack 130 lobby launch context router import'),
    ('v130_lobby_launch_router', 'Pack 130 router include'),
    ('v131_combat_preview', 'Pack 131 combat preview router import'),
    ('v131_combat_preview_router', 'Pack 131 router include'),
]


def main():
    errs = []
    if not SERVER.exists():
        return _emit(['server.py missing'])
    src = SERVER.read_text(encoding='utf-8')
    for tk, desc in REQUIRED_TOKENS:
        if tk not in src:
            errs.append(f'missing {desc}: token "{tk}" not found in server.py')
    return _emit(errs)


def _emit(errs):
    report = {'pack': 'PACK_132_PACK130_131_ROUTE_MOUNTS_STATIC',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'validation_kind': 'STATIC',
              'enforcement': 'VALIDATED_ONLY'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_132_pack130_131_route_mounts_static_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs:
            print(f'FAIL {e}')
        return 1
    print('PASS  Pack 130/131 routers mounted in server.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
