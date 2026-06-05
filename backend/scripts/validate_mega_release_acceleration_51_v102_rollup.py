#!/usr/bin/env python3
"""v102 — Rollup validator for all v102 sub-validators + marker emission."""
import os, sys, json, subprocess
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(ROOT, 'backend', 'scripts')
VALIDATORS = [
    'validate_v102_server_select_audit.py',
    'validate_v102_server_list_source.py',
    'validate_v102_server_select_ui.py',
    'validate_v102_selected_server_persistence.py',
    'validate_v102_logout_change_server.py',
    'validate_v102_auth_context_unification.py',
    'validate_v102_device_retest_matrix.py',
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
print(f'v102 rollup: {len(results)}/{len(VALIDATORS)} PASS')
marker_dir = os.path.join(ROOT,'data','design','release_acceleration')
os.makedirs(marker_dir, exist_ok=True)
marker = os.path.join(marker_dir,'mega_release_acceleration_51_v102_rollup_marker_v1.json')
with open(marker,'w',encoding='utf-8') as f:
    json.dump({
        'pack':'MEGA_RELEASE_ACCELERATION_51_v102',
        'type':'v102_rollup_marker',
        'version':1,
        'generated_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'validators_total':len(VALIDATORS),
        'validators_pass':len(results),
        'results':results,
        'verdict_string':'MEGA_RELEASE_ACCELERATION_51_SERVER_SELECT_RUNTIME_WIRING_AND_AUTH_UNIFICATION_FIX_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
    }, f, indent=2, ensure_ascii=False)
print(f'Rollup marker saved: {marker}')
sys.exit(0)
