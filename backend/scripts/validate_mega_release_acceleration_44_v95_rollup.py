#!/usr/bin/env python3
"""v95 — Rollup Validator: tutti i 9 validator v95."""
import os, sys, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VALIDATORS = [
    'validate_v95_battle_engine_runtime_apply.py',
    'validate_v95_engine_runtime_regression_tests.py',
    'validate_v95_readonly_catalog_endpoints_runtime.py',
    'validate_v95_inline_mirror_removal.py',
    'validate_v95_real_formation_runtime_fetch.py',
    'validate_v95_reward_score_canary_sandbox.py',
    'validate_v95_live_guild_runtime_gating.py',
    'validate_v95_live_announcement_sandbox_runtime.py',
    'validate_v95_release_candidate_prep_gate.py',
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
print(f'v95 rollup: {len(passed)}/{len(VALIDATORS)} PASS')
if failed:
    print('FAIL —')
    for v, msg in failed:
        print(f' [{v}] {msg.strip()}')
    sys.exit(1)
# Salva marker rollup
import json, datetime
marker = os.path.join(ROOT, 'data', 'design', 'release_acceleration', 'mega_release_acceleration_44_v95_rollup_marker_v1.json')
os.makedirs(os.path.dirname(marker), exist_ok=True)
with open(marker, 'w', encoding='utf-8') as f:
    json.dump({
        'pack': 'MEGA_RELEASE_ACCELERATION_44_v95',
        'public_sync_tag': 'PUBLIC_SYNC_TAG_v95_MEGA_RELEASE_ACCELERATION_44_RUNTIME_APPLY_AND_RELEASE_CANDIDATE_PREP_SUPERPACK',
        'rollup_validators_total': len(VALIDATORS),
        'rollup_validators_passed': len(passed),
        'verdict': 'MEGA_RELEASE_ACCELERATION_44_RUNTIME_APPLY_AND_RELEASE_CANDIDATE_PREP_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING',
        'safety': {'db_writes': 0, 'reward_live': False, 'production_broadcast': False},
        'timestamp_utc': datetime.datetime.utcnow().isoformat() + 'Z',
    }, f, ensure_ascii=False, indent=2)
print(f'Rollup marker saved: {marker}')
sys.exit(0)
