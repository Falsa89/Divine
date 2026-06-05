#!/usr/bin/env python3
"""v104 — Rollup validator for all v104 sub-validators + marker emission."""
import os, sys, json, subprocess
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(ROOT, 'backend', 'scripts')
VALIDATORS = [
    'validate_v104_server_scoped_data_flow_audit.py',
    'validate_v104_server_profile_backend_contract.py',
    'validate_v104_server_naming_canonicalization.py',
    'validate_v104_server_scoped_user_data_model.py',
    'validate_v104_frontend_server_id_propagation.py',
    'validate_v104_backend_server_id_filtering.py',
    'validate_v104_chat_server_isolation.py',
    'validate_v104_server_profile_creation_policy.py',
    'validate_v104_device_retest_matrix.py',
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
print(f'v104 rollup: {len(results)}/{len(VALIDATORS)} PASS')
marker_dir = os.path.join(ROOT, 'data', 'design', 'release_acceleration')
os.makedirs(marker_dir, exist_ok=True)
marker = os.path.join(marker_dir, 'mega_release_acceleration_53_v104_rollup_marker_v1.json')
with open(marker, 'w', encoding='utf-8') as f:
    json.dump({
        'pack': 'MEGA_RELEASE_ACCELERATION_53_v104',
        'type': 'v104_rollup_marker',
        'version': 1,
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'validators_total': len(VALIDATORS),
        'validators_pass': len(results),
        'results': results,
        'verdict_string': 'MEGA_RELEASE_ACCELERATION_53_SERVER_SCOPED_RUNTIME_DATA_AND_CHAT_ISOLATION_FIX_READY_WITH_BACKEND_ISOLATION_PENDING_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
    }, f, indent=2, ensure_ascii=False)
print(f'Rollup marker saved: {marker}')
sys.exit(0)
