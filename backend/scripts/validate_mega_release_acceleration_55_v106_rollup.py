#!/usr/bin/env python3
"""v106 — Rollup validator for all v106 sub-validators + marker emission."""
import os, sys, json, subprocess
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(ROOT, 'backend', 'scripts')
VALIDATORS = [
    'validate_v106_existing_data_model_audit.py',
    'validate_v106_player_server_profiles_schema.py',
    'validate_v106_account_global_vs_server_scoped_matrix.py',
    'validate_v106_backup_manifest.py',
    'validate_v106_dry_run_migration_result.py',
    'validate_v106_apply_script_gated.py',
    'validate_v106_rollback_script_gated.py',
    'validate_v106_server_scoped_read_contract.py',
    'validate_v106_bot_server_actor_migration_policy.py',
    'validate_v106_staging_apply_readiness_gate.py',
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
print(f'v106 rollup: {len(results)}/{len(VALIDATORS)} PASS')
marker_dir = os.path.join(ROOT, 'data', 'design', 'release_acceleration')
os.makedirs(marker_dir, exist_ok=True)
marker = os.path.join(marker_dir, 'mega_release_acceleration_55_v106_rollup_marker_v1.json')
with open(marker, 'w', encoding='utf-8') as f:
    json.dump({
        'pack': 'MEGA_RELEASE_ACCELERATION_55_v106',
        'type': 'v106_rollup_marker',
        'version': 1,
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'validators_total': len(VALIDATORS),
        'validators_pass': len(results),
        'results': results,
        'verdict_string': 'MEGA_RELEASE_ACCELERATION_55_SERVER_SCOPED_DB_SCHEMA_AND_PLAYER_SERVER_PROFILES_GATED_MIGRATION_PREP_DRY_RUN_READY_APPLY_GATED_NOT_EXECUTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
    }, f, indent=2, ensure_ascii=False)
print(f'Rollup marker saved: {marker}')
sys.exit(0)
