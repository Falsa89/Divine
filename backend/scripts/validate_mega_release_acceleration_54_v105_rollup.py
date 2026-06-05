#!/usr/bin/env python3
"""v105 — Rollup validator for all v105 sub-validators + marker emission."""
import os, sys, json, subprocess
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(ROOT, 'backend', 'scripts')
VALIDATORS = [
    'validate_v105_frontend_route_inventory.py',
    'validate_v105_backend_endpoint_inventory.py',
    'validate_v105_server_scope_audit.py',
    'validate_v105_mode_runtime_audit.py',
    'validate_v105_battle_launch_contract_audit.py',
    'validate_v105_encounter_source_audit.py',
    'validate_v105_legacy_data_runtime_audit.py',
    'validate_v105_bot_server_actor_audit.py',
    'validate_v105_chat_live_guild_audit.py',
    'validate_v105_economy_reward_claim_audit.py',
    'validate_v105_auth_account_server_profile_audit.py',
    'validate_v105_design_compliance_matrix.py',
    'validate_v105_runtime_consolidation_roadmap.py',
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
print(f'v105 rollup: {len(results)}/{len(VALIDATORS)} PASS')
marker_dir = os.path.join(ROOT, 'data', 'design', 'release_acceleration')
os.makedirs(marker_dir, exist_ok=True)
marker = os.path.join(marker_dir, 'mega_release_acceleration_54_v105_rollup_marker_v1.json')
with open(marker, 'w', encoding='utf-8') as f:
    json.dump({
        'pack': 'MEGA_RELEASE_ACCELERATION_54_v105',
        'type': 'v105_rollup_marker',
        'version': 1,
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'validators_total': len(VALIDATORS),
        'validators_pass': len(results),
        'results': results,
        'verdict_string': 'MEGA_RELEASE_ACCELERATION_54_MASTER_REPO_DESIGN_CONSISTENCY_AUDIT_AND_RUNTIME_CONSOLIDATION_PLAN_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
    }, f, indent=2, ensure_ascii=False)
print(f'Rollup marker saved: {marker}')
sys.exit(0)
