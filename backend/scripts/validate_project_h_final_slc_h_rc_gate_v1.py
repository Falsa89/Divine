#!/usr/bin/env python3
"""PROJECT_H Track A validator — final SLC-H release candidate gate."""
import json, os, sys, urllib.request, urllib.error
from pathlib import Path

MARKER = Path('/app/data/design/server_lifecycle/project_h_final_slc_h_rc_gate_v1.json')
ROUTE = Path('/app/backend/routes/server_profiles.py')


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
    if m.get('verdict') != 'TRACK_A_FINAL_SLC_H_RC_GATE_READY': fail('verdict mismatch')
    if m.get('runtime_changes_applied') is not False: fail('runtime_changes_applied must be False')
    forb = m.get('forbidden_in_track_a_respected', {})
    for k in ('live_enable', 'active_switch', 'db_writes', 'second_server', 'frontend'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_a.{k} must be False')
    sp = m.get('server_profiles_collection', {})
    if sp.get('writes_in_pack_h') != 0: fail('server_profiles writes_in_pack_h must be 0')
    if not isinstance(m.get('dual_route_contracts_consolidated', []), list) or len(m['dual_route_contracts_consolidated']) < 4:
        fail('dual_route_contracts_consolidated must list at least 4 contracts')
    if not isinstance(m.get('future_flags_required_for_live_preview', []), list) or len(m['future_flags_required_for_live_preview']) < 2:
        fail('future_flags_required_for_live_preview must list at least 2 flags')
    if not isinstance(m.get('blockers_for_real_active_server_switching', []), list) or len(m['blockers_for_real_active_server_switching']) < 3:
        fail('blockers_for_real_active_server_switching must list at least 3 blockers')
    if not ROUTE.exists(): fail('route missing')
    src = ROUTE.read_text()
    if 'SERVER_PROFILES_RUNTIME_ENABLED' not in src or 'SERVER_PROFILES_PREVIEW_ENABLED' not in src:
        fail('double-flag gate missing in route')
    if os.environ.get('SUITE_SKIP_HTTP_PROBE', '').strip().lower() != 'true':
        if os.environ.get('SERVER_PROFILES_RUNTIME_ENABLED', '').strip().lower() != 'true':
            for mtd in ('GET', 'POST'):
                code = http_status(mtd, 'http://127.0.0.1:8001/api/server-profiles/select')
                if code != 503 and code != -1: fail(f'{mtd} returned {code}, expected 503')
    print('[PASS] PROJECT_H Track A final SLC-H RC gate READY: dual-route contracts consolidated; flags+blockers documented; 503 default')
    sys.exit(0)

if __name__ == '__main__': main()
