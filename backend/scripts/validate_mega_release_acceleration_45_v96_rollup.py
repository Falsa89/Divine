#!/usr/bin/env python3
"""v96 — Rollup validator (all 11 v96 sub-validators)."""
import os, sys, subprocess, json, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VALIDATORS = [
    'validate_v96_auth_account_audit.py',
    'validate_v96_login_provider_contract.py',
    'validate_v96_auth_endpoints.py',
    'validate_v96_frontend_session.py',
    'validate_v96_real_formation_account_bridge.py',
    'validate_v96_account_privacy_compliance.py',
    'validate_v96_mobile_qa_matrix.py',
    'validate_v96_load_engine_smoke.py',
    'validate_v96_optional_fail_reconciliation.py',
    'validate_v96_md5_baseline_lock.py',
    'validate_v96_release_candidate_final_gate.py',
]
failed = []
passed = []
for v in VALIDATORS:
    path = os.path.join(ROOT, 'backend', 'scripts', v)
    r = subprocess.run([sys.executable, path], capture_output=True, text=True)
    if r.returncode != 0:
        failed.append((v, r.stdout + r.stderr))
    else:
        passed.append(v)
        print(r.stdout.strip())
print('---')
print(f'v96 rollup: {len(passed)}/{len(VALIDATORS)} PASS')
if failed:
    print('FAIL —')
    for v, msg in failed: print(f' [{v}] {msg.strip()}')
    sys.exit(1)
marker = os.path.join(ROOT, 'data', 'design', 'release_acceleration', 'mega_release_acceleration_45_v96_rollup_marker_v1.json')
os.makedirs(os.path.dirname(marker), exist_ok=True)
with open(marker, 'w', encoding='utf-8') as f:
    json.dump({
        'pack': 'MEGA_RELEASE_ACCELERATION_45_v96',
        'public_sync_tag': 'PUBLIC_SYNC_TAG_v96_MEGA_RELEASE_ACCELERATION_45_AUTH_ACCOUNT_AND_RELEASE_CANDIDATE_FINAL_SUPERPACK',
        'rollup_validators_total': len(VALIDATORS),
        'rollup_validators_passed': len(passed),
        'verdict': 'MEGA_RELEASE_ACCELERATION_45_AUTH_ACCOUNT_AND_RELEASE_CANDIDATE_FINAL_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING',
        'safety': {'db_writes_scope': 'users_collection_auth_only', 'reward_live': False, 'production_broadcast': False},
        'timestamp_utc': datetime.datetime.utcnow().isoformat() + 'Z',
    }, f, ensure_ascii=False, indent=2)
print(f'Rollup marker saved: {marker}')
sys.exit(0)
