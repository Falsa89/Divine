#!/usr/bin/env python3
"""Pack 130 — Pack 128 mutation guard interaction (STATIC).

Pack 130 endpoint è GET. Verifica che il middleware Pack 128 (POST/PUT/PATCH/DELETE)
non lo blocchi. La route NON deve essere POST.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTE = REPO_ROOT / 'backend' / 'routes' / 'v130_lobby_launch_context.py'


def main() -> int:
    errors = []; notes = []
    if not ROUTE.exists(): errors.append('route missing'); return _emit(errors, notes)
    src = ROUTE.read_text(encoding='utf-8')
    if '@router.post(' in src:
        errors.append('Pack 130 route uses POST — should be GET (no Pack 128 allowlist needed)')
    if '@router.get("/launch-context/preview")' not in src:
        errors.append('expected GET /launch-context/preview not found')
    print('OK    Pack 130 route is GET — NOT subject to Pack 128 mutation middleware')
    notes.append('Pack 128 middleware DORMANT by default in pod (PRE_QA_MUTATION_GUARD_ENABLED unset). When active, it intercepts only POST/PUT/PATCH/DELETE — Pack 130 GET passes naturally.')
    return _emit(errors, notes)


def _emit(errors, notes):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_130_PACK128_MUTATION_GUARD_INTERACTION',
              'status': 'PASS' if not errors else 'FAIL', 'errors': errors, 'notes': notes,
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED_PACK_130_IS_GET_ONLY_BYPASSES_POST_MIDDLEWARE'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_130_pack128_mutation_guard_interaction_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    for n in notes: print(f'  NOTE  {n}')
    print('PASS  Pack 130 route is GET; no Pack 128 allowlist modification required')
    return 0


if __name__ == '__main__': sys.exit(main())
