#!/usr/bin/env python3
"""PROJECT_S Track C validator — golden fixture matrix.

Carica le 14 fixture, esegue il resolver puro su ciascuna, confronta con expected.
Fallisce alla prima mismatch.
"""
import json, sys
from pathlib import Path

M = Path('/app/data/design/status_effects/project_s_second_slice_golden_fixture_matrix_v1.json')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_C_SECOND_SLICE_GOLDEN_FIXTURE_MATRIX_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    fixtures = m.get('fixtures') or []
    if len(fixtures) < 12:
        fail(f'fixture count {len(fixtures)} < 12 (spec requires at least 12)')
    if int(m.get('fixture_count', -1)) != len(fixtures):
        fail('fixture_count != len(fixtures)')
    sys.path.insert(0, '/app/backend')
    try:
        from game_logic.status_second_slice_resolver_pure import resolve_second_slice
    except Exception as e:
        fail(f'cannot import resolver: {e}')
    matched = 0
    for f in fixtures:
        out = resolve_second_slice(f['input'], f.get('mode', 'campaign'))
        exp = f['expected']
        for k in ('atk_pct', 'def_pct', 'speed_pct'):
            if abs(float(out.get(k, 0.0)) - float(exp.get(k, 0.0))) > 1e-9:
                fail(f'fixture {f["id"]} ({f["name"]}): got {out} expected {exp}')
        matched += 1
    if m.get('runtime_imported') is not False or m.get('db_writes') is not False:
        fail('runtime_imported/db_writes must be False')
    print(f'[PASS] PROJECT_S Track C golden fixture matrix READY — {matched}/{len(fixtures)} fixtures match resolver output')
    sys.exit(0)


if __name__ == '__main__': main()
