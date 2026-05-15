#!/usr/bin/env python3
"""
RM1.33-D — Runtime Debug Snapshot Contract Validator (READ-ONLY)
──────────────────────────────────────────────────────────────────────
Loads the snapshot fixtures and validates that each debug preview
response from the live server respects the canonical safety contract.

Volatile fields (timestamps, flag-derived booleans, runtime IDs) are
intentionally NOT compared. The validator compares only stable
contract fields (the "shape" of the safety envelope, disabled
runtime candidate, Borea catalog-only markers, etc).

Exit 0 on PASS, 1 on FAIL.
"""
from __future__ import annotations
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

FIXTURES = Path('/app/data/design/hero_skill_kits/hero_skill_kit_runtime_debug_snapshot_fixtures_v1.json')
BASE = 'http://localhost:8001'
DEBUG_PATH = '/api/hero-skill-kits/runtime/debug/preview'

failures: list[str] = []
infos: list[str] = []


def fail(case: str, msg: str) -> None:
    failures.append(f'[{case}] {msg}')


def info(msg: str) -> None:
    infos.append(msg)


def _http_get(qs: dict) -> tuple[int, dict | None]:
    q = urllib.parse.urlencode({k: v for k, v in qs.items() if v is not None})
    url = f'{BASE}{DEBUG_PATH}?{q}'
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            body = r.read()
            return r.status, (json.loads(body) if body else None)
    except urllib.error.HTTPError as e:
        try:
            body = e.read()
            data = json.loads(body) if body else None
        except Exception:
            data = None
        return e.code, data
    except Exception as e:
        return 0, {'_exception': repr(e)}


def _deep_subset_match(expected, actual, path: str, case_name: str) -> bool:
    """Verify that every key in `expected` exists in `actual` with a
    matching value (deeply). `actual` may have extra fields.

    - dict vs dict: recurse on each expected key
    - list vs list: index-wise recurse for as many items as in expected
    - scalar: direct equality
    """
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            fail(case_name, f'{path}: expected dict, got {type(actual).__name__}')
            return False
        ok = True
        for k, v in expected.items():
            if k not in actual:
                fail(case_name, f'{path}.{k}: missing key in response')
                ok = False
                continue
            ok &= _deep_subset_match(v, actual[k], f'{path}.{k}', case_name)
        return ok
    if isinstance(expected, list):
        if not isinstance(actual, list):
            fail(case_name, f'{path}: expected list, got {type(actual).__name__}')
            return False
        ok = True
        for i, v in enumerate(expected):
            if i >= len(actual):
                fail(case_name, f'{path}[{i}]: response list shorter than expected')
                ok = False
                continue
            ok &= _deep_subset_match(v, actual[i], f'{path}[{i}]', case_name)
        return ok
    if expected != actual:
        fail(case_name, f'{path}: expected {expected!r}, got {actual!r}')
        return False
    return True


def main() -> int:
    if not FIXTURES.exists():
        fail('io', f'fixtures missing: {FIXTURES}')
        return emit()
    spec = json.loads(FIXTURES.read_text(encoding='utf-8'))
    cases = spec.get('cases') or []
    if not cases:
        fail('io', 'no cases in fixtures')
        return emit()

    case_results: list[tuple[str, str]] = []
    for case in cases:
        name = case.get('name') or '<unnamed>'
        req = case.get('request') or {}
        expected = case.get('expected') or {}
        st, body = _http_get(req)
        exp_status = expected.get('http_status')
        if exp_status is not None and st != exp_status:
            fail(name, f'http_status: expected {exp_status}, got {st}')
            case_results.append((name, f'http_status mismatch ({st})'))
            continue
        if st == 200:
            exp_body = expected.get('response') or {}
            if not isinstance(body, dict):
                fail(name, 'response not a JSON object')
                case_results.append((name, 'bad shape'))
                continue
            ok = _deep_subset_match(exp_body, body, 'response', name)
            case_results.append((name, 'OK' if ok else 'contract mismatch'))
        else:
            # 4xx → verify detail subset
            exp_detail = expected.get('detail') or {}
            if not isinstance(body, dict):
                fail(name, '4xx response not a JSON object')
                case_results.append((name, 'bad 4xx shape'))
                continue
            actual_detail = body.get('detail') if isinstance(body.get('detail'), dict) else body
            ok = _deep_subset_match(exp_detail, actual_detail, 'detail', name)
            case_results.append((name, f'{st} OK' if ok else f'{st} contract mismatch'))

    # Summary line
    info(f'cases evaluated: {len(cases)} → {len([r for r in case_results if r[1].startswith(("OK","200","404","400")) or "OK" in r[1]])} passing')

    if failures:
        print('FAIL: RM1.33-D — Runtime Debug Snapshot Contract Validator')
        for f in failures:
            print(f'  - {f}')
        if infos:
            for i in infos:
                print(f'  i {i}')
        print('Per-case results:')
        for n, r in case_results:
            print(f'  - {n}: {r}')
        return 1

    print('PASS: RM1.33-D — Runtime Debug Snapshot Contract Validator')
    for i in infos:
        print(f'  i {i}')
    print('Per-case results:')
    for n, r in case_results:
        print(f'  - {n}: {r}')
    return 0


def emit() -> int:
    if failures:
        print('FAIL: RM1.33-D — Runtime Debug Snapshot Contract Validator')
        for f in failures:
            print(f'  - {f}')
        return 1
    print('PASS: RM1.33-D — Runtime Debug Snapshot Contract Validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
