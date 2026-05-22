#!/usr/bin/env python3
# SLC-G COMBO — esegue tutti i sub-validator SLC-G in sequenza (read-only)
import subprocess, sys, json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
SCRIPTS_DIR = ROOT / 'backend/scripts'
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
OUT = DESIGN_DIR / '_slc_g_combo_v1_result.json'

SUB = [
    ('preflight', 'validate_slc_g_preflight_v1.py'),
    ('backfill_dryrun', 'simulate_slc_g_default_s1_backfill_dryrun.py'),
    ('write_gate_contract', 'validate_slc_g_write_gate_contract_v1.py'),
    ('rollback_plan', 'validate_slc_g_rollback_plan_v1.py'),
    ('idempotency_contract', 'validate_slc_g_idempotency_contract_v1.py'),
]

def main():
    results = []
    overall = 'PASS'
    for name, script in SUB:
        path = SCRIPTS_DIR / script
        if not path.exists():
            results.append({'name':name,'script':script,'verdict':'MISS'})
            overall = 'FAIL'
            continue
        proc = subprocess.run(['python3', str(path)], capture_output=True, text=True, timeout=60)
        verdict = 'PASS' if proc.returncode == 0 else 'FAIL'
        if verdict == 'FAIL': overall = 'FAIL'
        results.append({'name':name,'script':script,'verdict':verdict,'exit_code':proc.returncode})

    # Final status determination: dry-run-first default outcome must be READY_TO_COMMIT_NOT_APPLIED
    # unless explicit approval marker is in current environment (NOT a runtime change, just a status indicator)
    import os
    explicit_marker = os.environ.get('SLC_G_WRITE_GATE_EXPLICIT_APPROVAL', '').lower() == 'true'
    final_status = 'READY_TO_COMMIT' if (overall == 'PASS' and explicit_marker) else (
        'READY_TO_COMMIT_NOT_APPLIED' if overall == 'PASS' else 'FAILED_SAFE_READY_NOT_APPLIED'
    )

    out = {
        'task_origin':'SLC-G-COMBO','version':'v1',
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'mode':'PRE_COMMIT_GATED_DRY_RUN_FIRST','db_write':False,'migration_applied':False,
        'combo_status':overall,'final_status':final_status,
        'explicit_user_write_approval_present':explicit_marker,
        'results':results,
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"[slc_g_combo_v1] {overall} final_status={final_status}")
    for r in results:
        print(f"  {r['verdict']:5s}  {r['name']}")
    return 0 if overall == 'PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
