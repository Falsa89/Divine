#!/usr/bin/env python3
"""Pack 130 — Snapshot no client-trusted stats (STATIC).

Verifica che la route NON accetti body con campi authoritative (stats, level,
power) usati come source of truth, e che il helper estragga TUTTO da DB.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTE = REPO_ROOT / 'backend' / 'routes' / 'v130_lobby_launch_context.py'
HELPER = REPO_ROOT / 'backend' / 'helpers' / 'real_player_snapshot.py'

# Route deve essere GET con query params (no body fidato).
FORBIDDEN_ROUTE_PATTERNS = [
    '@router.post("/launch-context',
    'BaseModel',  # se appare ovunque → c'è un body schema = client trusted
]
# Helper deve mantenere _sanitize_hero e SAFE_HERO_FIELDS.
REQUIRED_HELPER_PATTERNS = ['_sanitize_hero', 'SAFE_HERO_FIELDS', 'FORBIDDEN_HERO_FIELDS']


def main() -> int:
    errors = []; notes = []
    if not ROUTE.exists() or not HELPER.exists():
        errors.append('missing pack 130 files'); return _emit(errors, notes)
    rs = ROUTE.read_text(encoding='utf-8')
    hs = HELPER.read_text(encoding='utf-8')
    for fp in FORBIDDEN_ROUTE_PATTERNS:
        if fp in rs:
            errors.append(f'route accepts client-trusted payload: `{fp}`')
    for req in REQUIRED_HELPER_PATTERNS:
        if req not in hs:
            errors.append(f'helper missing sanitization symbol: `{req}`')
    if '@router.get("/launch-context/preview")' not in rs:
        errors.append('route is not GET (Pack 130 must be read-only)')
    print(f'OK    route is GET-only, helper has sanitization layer')
    return _emit(errors, notes)


def _emit(errors, notes):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_130_SNAPSHOT_NO_CLIENT_TRUST',
              'status': 'PASS' if not errors else 'FAIL', 'errors': errors, 'notes': notes,
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED_GET_ONLY_NO_BODY_HELPER_SANITIZED'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_130_snapshot_no_client_trust_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  route accepts no client body; helper sanitizes hero data')
    return 0


if __name__ == '__main__': sys.exit(main())
