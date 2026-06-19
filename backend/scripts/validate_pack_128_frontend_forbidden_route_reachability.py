#!/usr/bin/env python3
"""Pack 128 — Frontend forbidden route reachability (STATIC + blocklist coherence).

Verifica che le route player-dangerous nella blocklist Pack 112+
(PRE_QA_BLOCKED_PLAYER_ROUTES) NON siano nell'allowlist Pack 128.
Protegge contro contraddizioni dichiarative.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD = REPO_ROOT / 'frontend' / 'src' / 'utils' / 'preQaNavGuard.ts'


def _extract_set(src: str, name: str) -> set:
    m = re.search(rf'{name}.*?=\s*new Set<string>\(\[([^\]]+)\]\)', src, re.DOTALL)
    if not m: return set()
    body = m.group(1)
    routes = set()
    for line in body.splitlines():
        s = line.strip().strip(',').strip()
        if s.startswith("'") and s.endswith("'"):
            routes.add(s[1:-1])
    return routes


def main() -> int:
    errors = []; notes = []
    if not GUARD.exists(): errors.append('preQaNavGuard.ts missing'); return _emit(errors, notes, {})
    src = GUARD.read_text(encoding='utf-8')
    blocklist = _extract_set(src, 'PRE_QA_BLOCKED_PLAYER_ROUTES')
    allowlist = _extract_set(src, 'PRE_QA_ROUTE_ALLOWLIST')
    if not blocklist: notes.append('blocklist not parseable')
    if not allowlist: errors.append('PRE_QA_ROUTE_ALLOWLIST not parseable or empty')
    contradictions = blocklist & allowlist
    if contradictions:
        for c in sorted(contradictions):
            errors.append(f'route `{c}` is BOTH in blocklist AND allowlist (contradiction)')
    print(f'OK    blocklist size={len(blocklist)}, allowlist size={len(allowlist)}, contradictions={len(contradictions)}')
    return _emit(errors, notes, {'blocklist_size': len(blocklist), 'allowlist_size': len(allowlist), 'contradictions': sorted(contradictions)})


def _emit(errors, notes, info):
    print('\n' + '=' * 72)
    report = {
        'pack': 'PACK_128_FRONTEND_FORBIDDEN_ROUTE_REACHABILITY',
        'status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
        'notes': notes,
        'info': info,
        'validation_kind': 'STATIC',
        'enforcement': 'ENFORCED_BLOCKLIST_PRECEDENCE_OVER_ALLOWLIST',
    }
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_128_frontend_forbidden_route_reachability_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    for n in notes: print(f'  NOTE  {n}')
    print('PASS  blocklist/allowlist coherent (no route in both)')
    return 0


if __name__ == '__main__': sys.exit(main())
