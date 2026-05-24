#!/usr/bin/env python3
"""PROJECT_H Track B validator — final Housing MVP release candidate gate."""
import json, os, sys, urllib.request, urllib.error
from pathlib import Path

MARKER = Path('/app/data/design/housing/project_h_final_housing_mvp_rc_gate_v1.json')
ROUTE = Path('/app/backend/routes/housing_preview.py')
FORBIDDEN_DB_WRITES = ('insert_one(', 'update_one(', 'replace_one(', 'delete_one(', 'find_one_and_update(')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def http_status(method, url):
    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as r: return r.status
    except urllib.error.HTTPError as e: return e.code
    except Exception: return -1


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_B_FINAL_HOUSING_MVP_RC_GATE_READY': fail('verdict mismatch')
    if m.get('runtime_changes_applied') is not False: fail('runtime_changes_applied must be False')
    forb = m.get('forbidden_in_track_b_respected', {})
    for k in ('housing_live_bonus', 'db_writes', 'battle_mutation', 'account_stat_mutation', 'frontend'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_b.{k} must be False')
    if not isinstance(m.get('blockers_for_live_bonus_application', []), list) or len(m['blockers_for_live_bonus_application']) < 3:
        fail('blockers_for_live_bonus_application must list at least 3 blockers')
    inv = m.get('route_invariants_at_rc', {})
    if inv.get('default_status') != 503: fail('route_invariants_at_rc.default_status must be 503')
    if inv.get('housing_bonus_resolver_stub_imported_by_route') is not False:
        fail('route_invariants_at_rc.housing_bonus_resolver_stub_imported_by_route must be False')
    if inv.get('live_bonus_applied') is not False: fail('route_invariants_at_rc.live_bonus_applied must be False')
    # Route hygiene check
    if not ROUTE.exists(): fail('housing_preview route missing')
    rsrc = ROUTE.read_text()
    for bad in ('from game_logic.housing_bonus_resolver_stub', 'from backend.game_logic.housing_bonus_resolver_stub', 'import housing_bonus_resolver_stub'):
        if bad in rsrc: fail(f'forbidden import in housing_preview: {bad}')
    for kw in FORBIDDEN_DB_WRITES:
        if kw in rsrc: fail(f'forbidden DB write op in housing_preview: {kw}')
    if os.environ.get('SUITE_SKIP_HTTP_PROBE', '').strip().lower() != 'true':
        if os.environ.get('HOUSING_PREVIEW_ENABLED', '').strip().lower() != 'true':
            code = http_status('GET', 'http://127.0.0.1:8001/api/housing/preview')
            if code not in (503, -1): fail(f'GET /api/housing/preview returned {code}, expected 503')
    print('[PASS] PROJECT_H Track B final Housing MVP RC gate READY: 503 default; resolver not imported; no DB writes; blockers documented')
    sys.exit(0)

if __name__ == '__main__': main()
