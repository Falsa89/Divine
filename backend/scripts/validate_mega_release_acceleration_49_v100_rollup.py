#!/usr/bin/env python3
"""v100 — Rollup validator for all v100 sub-validators + marker emission."""
import os, sys, json, subprocess
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(ROOT, 'backend', 'scripts')
VALIDATORS = [
    'validate_v100_md5_forensic_audit.py',
    'validate_v100_runtime_md5_baseline.py',
    'validate_v100_supersede_review.py',
    'validate_v100_optional_fail_cleanup.py',
    'validate_v100_required_invariant_protection.py',
    'validate_v100_external_blocker_checklist.py',
    'validate_v100_closed_alpha_candidate_gate.py',
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
print(f'v100 rollup: {len(results)}/{len(VALIDATORS)} PASS')
marker_dir = os.path.join(ROOT, 'data', 'design', 'release_acceleration')
os.makedirs(marker_dir, exist_ok=True)
marker_path = os.path.join(marker_dir, 'mega_release_acceleration_49_v100_rollup_marker_v1.json')
with open(marker_path,'w',encoding='utf-8') as f:
    json.dump({
        'pack': 'MEGA_RELEASE_ACCELERATION_49_v100',
        'type': 'v100_rollup_marker',
        'version': 1,
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'validators_total': len(VALIDATORS),
        'validators_pass': len(results),
        'results': results,
        'verdict_string': 'MEGA_RELEASE_ACCELERATION_49_MD5_SUPERSEDE_AND_CLOSED_ALPHA_READINESS_UNLOCK_CONDITIONAL_EXTERNAL_BLOCKERS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
    }, f, indent=2, ensure_ascii=False)
print(f'Rollup marker saved: {marker_path}')
sys.exit(0)
