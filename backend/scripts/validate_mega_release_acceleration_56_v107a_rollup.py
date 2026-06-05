#!/usr/bin/env python3
"""v107A — Rollup validator + marker emission."""
import os, sys, json, subprocess
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(ROOT, 'backend', 'scripts')
VALIDATORS = [
    'validate_v107a_v106_public_sync_snapshot.py',
    'validate_v107a_battle_launch_contract_schema.py',
    'validate_v107a_battle_launch_endpoint.py',
    'validate_v107a_pre_battle_lobby_contract.py',
    'validate_v107a_combat_contract_consumer.py',
    'validate_v107a_backend_loader_server_id_adoption.py',
    'validate_v107a_frontend_loader_server_id_propagation.py',
    'validate_v107a_story_autoresolve_deprecation.py',
    'validate_v107a_encounter_source_adapter_contract.py',
    'validate_v107a_idempotency_reward_progress_guard.py',
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
print(f'v107A rollup: {len(results)}/{len(VALIDATORS)} PASS')
marker_dir = os.path.join(ROOT, 'data', 'design', 'release_acceleration')
os.makedirs(marker_dir, exist_ok=True)
marker = os.path.join(marker_dir, 'mega_release_acceleration_56_v107a_rollup_marker_v1.json')
with open(marker, 'w', encoding='utf-8') as f:
    json.dump({
        'pack':'MEGA_RELEASE_ACCELERATION_56_v107A',
        'type':'v107a_rollup_marker',
        'version':1,
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'validators_total': len(VALIDATORS),
        'validators_pass': len(results),
        'results': results,
        'verdict_string':'MEGA_RELEASE_ACCELERATION_56_BATTLE_LAUNCH_CONTRACT_AND_SERVER_ID_LOADER_ADOPTION_FLAGGED_READY_WITH_CONTRACT_ONLY_GAPS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
    }, f, indent=2, ensure_ascii=False)
print(f'Rollup marker saved: {marker}')
sys.exit(0)
