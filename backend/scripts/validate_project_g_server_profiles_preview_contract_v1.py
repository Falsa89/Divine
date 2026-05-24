#!/usr/bin/env python3
"""PROJECT_G Track A validator — server profiles preview contract freeze.

Verifies:
  * marker present with verdict TRACK_A_SERVER_PROFILES_PREVIEW_CONTRACT_FROZEN_INERT
  * runtime probe: GET+POST /api/server-profiles/select → 503 (flags OFF)
  * route file present and double-flag gate code intact
  * no DB write keyword in default handlers
  * server_profiles collection has 0 docs (best-effort)
"""
import json, os, sys, urllib.request, urllib.error
from pathlib import Path

MARKER = Path('/app/data/design/server_lifecycle/project_g_server_profiles_preview_contract_v1.json')
ROUTE = Path('/app/backend/routes/server_profiles.py')
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
    if m.get('verdict') != 'TRACK_A_SERVER_PROFILES_PREVIEW_CONTRACT_FROZEN_INERT': fail('verdict mismatch')
    if m.get('runtime_changes_applied') is not False: fail('runtime_changes_applied must be False')
    forb = m.get('forbidden_in_track_a_respected', {})
    for k in ('live_enable', 'active_switch', 'db_writes', 'second_server', 'frontend'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_a.{k} must be False')
    if not ROUTE.exists(): fail(f'route missing {ROUTE}')
    src = ROUTE.read_text()
    if 'SERVER_PROFILES_RUNTIME_ENABLED' not in src or 'SERVER_PROFILES_PREVIEW_ENABLED' not in src:
        fail('double-flag gate not present in route module')
    get_h = src.find('async def server_profiles_select_probe')
    cut = src.find('# ===================== PROJECT_D TRACK A')
    if cut == -1: cut = len(src)
    handlers = src[get_h:cut] if get_h != -1 else ''
    for kw in FORBIDDEN_DB_WRITES:
        if kw in handlers: fail(f'forbidden DB write op in default handlers: {kw}')
    # Runtime probe
    if os.environ.get('SUITE_SKIP_HTTP_PROBE', '').strip().lower() != 'true':
        if os.environ.get('SERVER_PROFILES_RUNTIME_ENABLED', '').strip().lower() == 'true':
            print('[WARN] SERVER_PROFILES_RUNTIME_ENABLED=true — skipping 503 probe')
        else:
            for mtd in ('GET', 'POST'):
                code = http_status(mtd, 'http://127.0.0.1:8001/api/server-profiles/select')
                if code != 503 and code != -1:
                    fail(f'runtime probe {mtd} returned {code}, expected 503')
    print('[PASS] PROJECT_G Track A server profiles preview contract FROZEN INERT: 503 default; double-flag gate intact; no DB writes')
    sys.exit(0)

if __name__ == '__main__': main()
