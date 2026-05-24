#!/usr/bin/env python3
"""PROJECT_V Track A validator — dev-live env precheck."""
import json, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_v_second_slice_dev_live_precheck_v1.json')
ALLOWED = ('DEV_LIVE_CONFIRMED', 'NON_PROD_LOCAL_ONLY')
FORBIDDEN = ('PROD_LIKE_BLOCKED',)
ENV = Path('/app/backend/.env')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    if not M.exists(): fail('marker missing')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_A_SECOND_SLICE_DEV_LIVE_PRECHECK_READY': fail('verdict mismatch')
    if m.get('classification') in FORBIDDEN: fail(f'classification forbidden')
    if m.get('classification') not in ALLOWED: fail(f'classification invalid')
    if m.get('classification') == 'NON_PROD_LOCAL_ONLY':
        env_audit = m.get('env_audit', {})
        if env_audit.get('mongo_is_local') is not True: fail('mongo_is_local must be True')
        if env_audit.get('production_traffic') is not False: fail('production_traffic must be False')
        if ENV.exists():
            for line in ENV.read_text().splitlines():
                if line.strip().startswith('MONGO_URL=') and 'localhost' not in line and '127.0.0.1' not in line:
                    fail(f'MONGO_URL not local: {line!r}')
    prereq = m.get('prerequisites_satisfied', {})
    for k in ('project_u_complete', 'canary_smoke_green', 'canary_load_green', 'canary_rollback_green', 'suite_baseline_527_pass'):
        if prereq.get(k) is not True: fail(f'prereq.{k} must be True')
    if m.get('db_writes') is not False: fail('db_writes must be False')
    print(f'[PASS] PROJECT_V Track A dev-live precheck READY — classification={m.get("classification")}; ELIGIBLE')
    sys.exit(0)
if __name__ == '__main__': main()
