#!/usr/bin/env python3
"""v103 — Rollup validator for all v103 sub-validators + marker emission."""
import os, sys, json, subprocess
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(ROOT, 'backend', 'scripts')
VALIDATORS = [
    'validate_v103_server_profile_backend_audit.py',
    'validate_v103_server_profiles_endpoint.py',
    'validate_v103_server_naming_status.py',
    'validate_v103_server_selection_persistence.py',
    'validate_v103_server_scoped_data_isolation.py',
    'validate_v103_logout_race_fix.py',
    'validate_v103_auth_context_unification.py',
    'validate_v103_device_retest_matrix.py',
]
results = []
for v in VALIDATORS:
    path = os.path.join(SCRIPTS, v)
    if not os.path.isfile(path): print(f'FAIL \u2014 validator missing: {v}'); sys.exit(1)
    r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=60)
    line = (r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '').strip()
    print(line)
    results.append({'validator': v, 'exit_code': r.returncode, 'last_line': line})
    if r.returncode != 0: print(f'FAIL \u2014 sub-validator {v} returned {r.returncode}'); sys.exit(1)
print('---')
print(f'v103 rollup: {len(results)}/{len(VALIDATORS)} PASS')
marker_dir = os.path.join(ROOT,'data','design','release_acceleration')
os.makedirs(marker_dir, exist_ok=True)
marker = os.path.join(marker_dir,'mega_release_acceleration_52_v103_rollup_marker_v1.json')
with open(marker,'w',encoding='utf-8') as f:
    json.dump({
        'pack':'MEGA_RELEASE_ACCELERATION_52_v103',
        'type':'v103_rollup_marker',
        'version':1,
        'generated_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'validators_total':len(VALIDATORS),
        'validators_pass':len(results),
        'results':results,
        'verdict_string':'MEGA_RELEASE_ACCELERATION_52_SERVER_PROFILE_BACKEND_DATA_ISOLATION_AND_LOGOUT_RACE_FIX_READY_WITH_BACKEND_ISOLATION_PENDING_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
    }, f, indent=2, ensure_ascii=False)
print(f'Rollup marker saved: {marker}')
sys.exit(0)
