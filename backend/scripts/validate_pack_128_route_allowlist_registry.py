#!/usr/bin/env python3
"""Pack 128 — Route allowlist registry validator (STATIC).

Verifica che:
  1. `frontend/src/utils/preQaNavGuard.ts` esporti `PRE_QA_ROUTE_ALLOWLIST`
     e l'helper `isRouteInPreQaAllowlist`.
  2. La blocklist legacy `PRE_QA_BLOCKED_PLAYER_ROUTES` resti presente
     (no regressione Pack 112+).
  3. La nuova allowlist contenga route minime di bootstrap QA,
     **parsando la allowlist reale** (non cercando stringhe nel file intero,
     che farebbe match anche con commenti — bug Pack 128 truth fix).
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD = REPO_ROOT / 'frontend' / 'src' / 'utils' / 'preQaNavGuard.ts'

# `/safe-previews` rimossa da MIN_ALLOWED: in Pack 119B e' classificata come
# dev/QA-gated (visibile solo con EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE=true) e
# NON e' player-facing in pre-QA. Coerente con la blocklist precedence in
# classifyDeeplink().
MIN_ALLOWED = ['/login', '/servers', '/(tabs)/home']


def _parse_allowlist(src: str) -> set:
    """Estrae le route effettive da `PRE_QA_ROUTE_ALLOWLIST = new Set<string>([...])`.
    Ignora i commenti `//` per evitare falsi positivi su token in commento.
    """
    m = re.search(r'PRE_QA_ROUTE_ALLOWLIST.*?=\s*new Set<string>\(\[([^\]]+)\]\)', src, re.DOTALL)
    if not m:
        return set()
    body = m.group(1)
    routes = set()
    for raw_line in body.splitlines():
        # rimuove commento di linea
        line = raw_line.split('//', 1)[0].strip().rstrip(',').strip()
        if line.startswith("'") and line.endswith("'"):
            routes.add(line[1:-1])
        elif line.startswith('"') and line.endswith('"'):
            routes.add(line[1:-1])
    return routes


def main() -> int:
    errors = []
    notes = []
    if not GUARD.exists():
        errors.append('preQaNavGuard.ts missing'); return _emit(errors, notes, set())
    src = GUARD.read_text(encoding='utf-8')
    if 'PRE_QA_ROUTE_ALLOWLIST' not in src:
        errors.append('PRE_QA_ROUTE_ALLOWLIST not exported in preQaNavGuard.ts')
    if 'isRouteInPreQaAllowlist' not in src:
        errors.append('isRouteInPreQaAllowlist helper missing')
    if 'PRE_QA_BLOCKED_PLAYER_ROUTES' not in src:
        errors.append('legacy PRE_QA_BLOCKED_PLAYER_ROUTES blocklist removed (regression)')
    if 'classifyDeeplink' not in src:
        errors.append('classifyDeeplink function missing in preQaNavGuard.ts')

    # Truth check: parsa la allowlist reale, NON cerca stringhe nel file intero.
    real_allowlist = _parse_allowlist(src)
    if not real_allowlist:
        errors.append('PRE_QA_ROUTE_ALLOWLIST not parseable or empty')
    else:
        print(f'OK    PRE_QA_ROUTE_ALLOWLIST reale: {len(real_allowlist)} route parsate')

    for r in MIN_ALLOWED:
        if r not in real_allowlist:
            errors.append(f'MIN_ALLOWED bootstrap route `{r}` NOT in PRE_QA_ROUTE_ALLOWLIST reale')

    print(f'OK    preQaNavGuard.ts contains required exports')
    return _emit(errors, notes, real_allowlist)


def _emit(errors, notes, real_allowlist):
    print('\n' + '=' * 72)
    report = {
        'pack': 'PACK_128_ROUTE_ALLOWLIST_REGISTRY',
        'status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
        'notes': notes,
        'min_allowed_required': MIN_ALLOWED,
        'real_allowlist_size': len(real_allowlist),
        'real_allowlist': sorted(real_allowlist),
        'validation_kind': 'STATIC',
        'enforcement': 'ENFORCED_STATIC_REGISTRY_PRESENT_PARSED_REAL_NOT_STRING_MATCH',
    }
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_128_route_allowlist_registry_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    if notes:
        for n in notes: print(f'  NOTE  {n}')
    print('PASS  route allowlist registry present, MIN_ALLOWED verified against REAL allowlist set')
    return 0


if __name__ == '__main__': sys.exit(main())

