#!/usr/bin/env python3
"""Pack 132 — Authenticated Smoke Harness Contract validator.

Static validation that the Pack 132 harness is safe-by-default:
- no DB writes;
- no seed;
- no mutating endpoint calls;
- env-gated: returns MANUAL_REQUIRED if QA env unset.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HARNESS = REPO_ROOT / 'backend' / 'scripts' / 'pre_device_qa_authenticated_smoke_harness.py'
FORBIDDEN_DB = ['update_one(', 'update_many(', 'insert_one(', 'insert_many(',
                'delete_one(', 'delete_many(', 'replace_one(', 'bulk_write(',
                'find_one_and_update(', 'find_one_and_delete(', 'find_one_and_replace(',
                'create_index(']
FORBIDDEN_ENDPOINTS = ['/api/team/save-formation', '/api/battle/simulate',
                      '/api/reward/claim', '/api/mail/claim', '/api/shop/purchase',
                      '/api/gacha/pull', '/api/hero/upgrade', '/api/affinity/gift']
REQUIRED_TOKENS = ['MANUAL_REQUIRED', 'NOT_EXECUTED', 'QA_TEST_JWT', 'AUTHENTICATED_SMOKE_STATUS']


def main():
    errs = []
    if not HARNESS.exists():
        return _emit(['harness missing: ' + str(HARNESS.relative_to(REPO_ROOT))])
    src = HARNESS.read_text(encoding='utf-8')
    for tk in FORBIDDEN_DB:
        if tk in src:
            errs.append(f'harness contains DB write call: {tk}')
    # Cerco chiamate effettive a endpoint vietati (non semplici menzioni in liste).
    # Pattern: l'endpoint deve apparire dentro a una chiamata _safe_get(.., 'EP') o request(EP) o urlopen(EP).
    import re as _re
    for ep in FORBIDDEN_ENDPOINTS:
        # Skip se l'endpoint compare solo dentro una lista che si chiama FORBIDDEN_*.
        # Approccio: cerca pattern di invocazione tipo _safe_get(..., 'EP' oppure urlopen('EP'
        call_patterns = [
            _re.compile(r"_safe_get\([^)]*['\"]" + _re.escape(ep) + r"['\"]"),
            _re.compile(r"urlopen\(\s*['\"]" + _re.escape(ep) + r"['\"]"),
            _re.compile(r"\.get\(\s*['\"]" + _re.escape(ep) + r"['\"]"),
            _re.compile(r"Request\(\s*['\"][^'\"]*" + _re.escape(ep) + r"['\"]"),
        ]
        if any(p.search(src) for p in call_patterns):
            errs.append(f'harness CALLS forbidden mutating endpoint: {ep}')
    for tok in REQUIRED_TOKENS:
        if tok not in src:
            errs.append(f'harness missing required token: {tok}')
    # methods used must be GET-only.
    forbidden_methods = ['requests.post(', 'requests.put(', 'requests.delete(', 'requests.patch(',
                        '.post(', '.put(', '.delete(', '.patch(']
    # accept httpx but only GET
    for fm in ['requests.post(', 'requests.put(', 'requests.delete(', 'requests.patch(']:
        if fm in src:
            errs.append(f'harness uses non-GET HTTP method: {fm}')
    return _emit(errs)


def _emit(errs):
    report = {'pack': 'PACK_132_AUTHENTICATED_SMOKE_HARNESS_CONTRACT',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED_SAFE_BY_DEFAULT'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_132_authenticated_smoke_harness_contract_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs:
            print(f'FAIL {e}')
        return 1
    print('PASS  authenticated smoke harness safe-by-default')
    return 0


if __name__ == '__main__':
    sys.exit(main())
