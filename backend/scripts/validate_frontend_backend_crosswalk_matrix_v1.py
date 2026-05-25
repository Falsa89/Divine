#!/usr/bin/env python3
# PROJECT_MODE_WIRING_REGISTRY / TRACK D
import json, sys
from pathlib import Path

P = Path('/app/data/design/frontend/frontend_backend_crosswalk_matrix_v1.json')
REQUIRED = ['frontend_route','backend_calls','mutations','all_endpoints_exist','legacy_used','handles_503','exposes_live_action']

def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_D_FRONTEND_BACKEND_CROSSWALK_MATRIX_READY'
    assert d['audit_mode'] == 'audit_only'
    assert d['db_writes'] == 0
    assert d['global_markers']['TRACK_D_FRONTEND_BACKEND_CROSSWALK_MATRIX_APPROVAL'] == 'true'
    cw = d['crosswalk']
    assert isinstance(cw, list) and len(cw) >= 25, f'crosswalk too small: {len(cw)}'
    for row in cw:
        for f in REQUIRED:
            assert f in row, f"row {row.get('frontend_route')} missing {f}"
    # core routes must be present
    routes = [r['frontend_route'] for r in cw]
    for r in ['/(tabs)/home','/(tabs)/heroes','/(tabs)/battle','/(tabs)/gacha','/combat','/safe-previews','/daily-hub','/artifacts-preview','/housing-preview','/status-codex','/servers']:
        assert r in routes, f'missing route in crosswalk: {r}'
    # /servers must be flagged legacy_used true
    srv = next(r for r in cw if r['frontend_route']=='/servers')
    assert srv['legacy_used'] is True, '/servers must be flagged legacy_used'
    s = d['summary']
    assert s['routes_with_legacy_endpoints'] >= 1
    print(f"[PASS] Track D frontend\u2192backend crosswalk READY \u2014 routes={s['total_frontend_routes_audited']}, legacy_routes={s['routes_with_legacy_endpoints']}")
    return 0
if __name__ == '__main__': sys.exit(main())
