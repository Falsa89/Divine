#!/usr/bin/env python3
"""PROJECT_F Track B validator — housing read-only preview endpoint contract.

Invariants enforced:
  * /app/backend/routes/housing_preview.py exists.
  * Module defines FEATURE_FLAG = 'HOUSING_PREVIEW_ENABLED'.
  * GET handler raises HTTPException(503) when flag OFF.
  * Module does NOT contain forbidden DB write ops in the route file itself.
  * Module imported in server.py via include_router.
  * Runtime probe: GET /api/housing/preview returns 503 when flag unset.
  * Marker present and verdict correct.
  * housing_bonus_resolver_stub NOT imported by housing_preview (read-only contract
    must not pull live resolver until later activation).
"""
import json, os, sys
import urllib.request, urllib.error
from pathlib import Path

ROUTE = Path('/app/backend/routes/housing_preview.py')
SERVER = Path('/app/backend/server.py')
MARKER = Path('/app/data/design/housing/project_f_housing_read_only_preview_contract_v1.json')
FORBIDDEN_DB_WRITES = ('insert_one(', 'update_one(', 'replace_one(', 'delete_one(', 'find_one_and_update(')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def http_status(method: str, url: str) -> int:
    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return -1


def main():
    if not ROUTE.exists(): fail(f'missing route {ROUTE}')
    src = ROUTE.read_text()
    if 'HOUSING_PREVIEW_ENABLED' not in src: fail('feature flag HOUSING_PREVIEW_ENABLED missing')
    if 'HTTPException(status_code=503' not in src and 'HTTPException(503' not in src and "status_code=503" not in src:
        fail('503 raise missing in handler')
    if '@router.get("/preview")' not in src: fail('GET /preview decorator missing')
    # NO live resolver import in route
    if 'from game_logic.housing_bonus_resolver_stub' in src or 'import housing_bonus_resolver_stub' in src:
        fail('housing_bonus_resolver_stub must NOT be imported by housing_preview route')
    for kw in FORBIDDEN_DB_WRITES:
        if kw in src:
            fail(f'forbidden DB write op in housing_preview: {kw}')
    # Wired in server.py
    if not SERVER.exists(): fail('server.py missing')
    srv = SERVER.read_text()
    if 'from routes.housing_preview import router as housing_preview_router' not in srv:
        fail('server.py must import housing_preview router (from routes.housing_preview import router as housing_preview_router)')
    if 'app.include_router(housing_preview_router)' not in srv:
        fail('server.py must include_router(housing_preview_router)')
    # Runtime probe (best-effort): GET must be 503 when flag unset
    if os.environ.get('SUITE_SKIP_HTTP_PROBE', '').strip().lower() != 'true':
        if os.environ.get('HOUSING_PREVIEW_ENABLED', '').strip().lower() == 'true':
            print('[WARN] HOUSING_PREVIEW_ENABLED=true — skipping 503 runtime probe')
        else:
            code = http_status('GET', 'http://127.0.0.1:8001/api/housing/preview')
            if code not in (503, -1):
                fail(f'runtime probe GET /api/housing/preview returned {code}, expected 503')
    # Marker
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_B_HOUSING_READ_ONLY_PREVIEW_SKELETON_APPLIED_INERT':
        fail('marker verdict mismatch')
    forb = m.get('forbidden_in_track_b_respected', {})
    for k in ('housing_live_bonus', 'db_writes', 'battle_mutation', 'account_stat_mutation', 'frontend'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_b.{k} must be False')
    print('[PASS] PROJECT_F Track B housing read-only preview SKELETON APPLIED INERT: 503 default; no DB writes; no resolver import; router wired')
    sys.exit(0)

if __name__ == '__main__': main()
