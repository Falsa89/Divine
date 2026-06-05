#!/usr/bin/env python3
"""v99 — Rollup validator for all v99 sub-validators + marker emission."""
import os, sys, json, subprocess
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(ROOT, 'backend', 'scripts')
VALIDATORS = [
    'validate_v99_optional_fail_cleanup.py',
    'validate_v99_provider_id_token_verification.py',
    'validate_v99_privacy_terms_urls.py',
    'validate_v99_physical_mobile_qa.py',
    'validate_v99_full_locust.py',
    'validate_v99_store_internal_testing_readiness.py',
    'validate_v99_closed_alpha_final_gate.py',
]
results = []
for v in VALIDATORS:
    path = os.path.join(SCRIPTS, v)
    if not os.path.isfile(path):
        print(f'FAIL \u2014 validator missing: {v}'); sys.exit(1)
    r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=60)
    line = (r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '').strip()
    print(line)
    results.append({'validator': v, 'exit_code': r.returncode, 'last_line': line})
    if r.returncode != 0:
        print(f'FAIL \u2014 sub-validator {v} returned {r.returncode}'); sys.exit(1)
print('---')
print(f'v99 rollup: {len(results)}/{len(VALIDATORS)} PASS')
marker_dir = os.path.join(ROOT, 'data', 'design', 'release_acceleration')
os.makedirs(marker_dir, exist_ok=True)
marker_path = os.path.join(marker_dir, 'mega_release_acceleration_48_v99_rollup_marker_v1.json')
with open(marker_path, 'w', encoding='utf-8') as f:
    json.dump({
        'pack': 'MEGA_RELEASE_ACCELERATION_48_v99',
        'type': 'v99_rollup_marker',
        'version': 1,
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'validators_total': len(VALIDATORS),
        'validators_pass': len(results),
        'results': results,
        'verdict_string': 'MEGA_RELEASE_ACCELERATION_48_CLOSED_ALPHA_BLOCKER_CLEANUP_AND_PUBLIC_TEST_GATE_CONDITIONAL_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
    }, f, indent=2, ensure_ascii=False)
print(f'Rollup marker saved: {marker_path}')
sys.exit(0)
