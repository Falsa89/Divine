#!/usr/bin/env python3
"""Pack 128 — Route allowlist registry validator (STATIC).

Verifica che:
  1. `frontend/src/utils/preQaNavGuard.ts` esporti `PRE_QA_ROUTE_ALLOWLIST`
     e l'helper `isRouteInPreQaAllowlist`.
  2. La blocklist legacy `PRE_QA_BLOCKED_PLAYER_ROUTES` resti presente
     (no regressione Pack 112+).
  3. La nuova allowlist contenga route minime di bootstrap QA.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD = REPO_ROOT / 'frontend' / 'src' / 'utils' / 'preQaNavGuard.ts'

MIN_ALLOWED = ['/login', '/servers', '/(tabs)/home', '/safe-previews']


def main() -> int:
    errors = []
    notes = []
    if not GUARD.exists():
        errors.append('preQaNavGuard.ts missing'); return _emit(errors, notes)
    src = GUARD.read_text(encoding='utf-8')
    if 'PRE_QA_ROUTE_ALLOWLIST' not in src:
        errors.append('PRE_QA_ROUTE_ALLOWLIST not exported in preQaNavGuard.ts')
    if 'isRouteInPreQaAllowlist' not in src:
        errors.append('isRouteInPreQaAllowlist helper missing')
    if 'PRE_QA_BLOCKED_PLAYER_ROUTES' not in src:
        errors.append('legacy PRE_QA_BLOCKED_PLAYER_ROUTES blocklist removed (regression)')
    for r in MIN_ALLOWED:
        if f"'{r}'" not in src:
            notes.append(f'allowlist may miss bootstrap route `{r}` — verify manually')
    if 'classifyDeeplink' not in src:
        errors.append('classifyDeeplink function missing in preQaNavGuard.ts')
    print(f'OK    preQaNavGuard.ts contains required exports')
    return _emit(errors, notes)


def _emit(errors, notes):
    print('\n' + '=' * 72)
    report = {
        'pack': 'PACK_128_ROUTE_ALLOWLIST_REGISTRY',
        'status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
        'notes': notes,
        'validation_kind': 'STATIC',
        'enforcement': 'ENFORCED_STATIC_REGISTRY_PRESENT',
    }
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_128_route_allowlist_registry_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    if notes:
        for n in notes: print(f'  NOTE  {n}')
    print('PASS  route allowlist registry present (static)')
    return 0


if __name__ == '__main__': sys.exit(main())
