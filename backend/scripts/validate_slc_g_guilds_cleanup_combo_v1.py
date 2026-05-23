#!/usr/bin/env python3
# SLC-G-GUILDS CLEANUP COMBO
import json, os, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
SCRIPTS_DIR = ROOT / 'backend/scripts'
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
OUT = DESIGN_DIR / '_slc_g_guilds_cleanup_combo_v1_result.json'

SUB = [
    ('live_audit', 'audit_slc_g_guilds_unsafe_readonly_v1.py'),
    ('cleanup_plan', 'validate_slc_g_guilds_cleanup_plan_v1.py'),
    ('gate_contract', 'validate_slc_g_guilds_cleanup_gate_contract_v1.py'),
    ('rollback_plan', 'validate_slc_g_guilds_cleanup_rollback_plan_v1.py'),
]

def main():
    results = []
    overall = 'PASS'
    for name, script in SUB:
        p = SCRIPTS_DIR / script
        if not p.exists():
            results.append({'name':name,'script':script,'verdict':'MISS'})
            overall = 'FAIL'
            continue
        proc = subprocess.run(['python3', str(p)], capture_output=True, text=True, timeout=60)
        v = 'PASS' if proc.returncode == 0 else 'FAIL'
        if v == 'FAIL': overall = 'FAIL'
        results.append({'name':name,'script':script,'verdict':v,'exit_code':proc.returncode})

    marker = os.environ.get('SLC_G_GUILDS_UNSAFE_CLEANUP_WRITE_APPROVAL','').lower() == 'true'
    final = 'CLEANUP_APPLIED_SAFE' if (overall == 'PASS' and marker) else (
        'READY_TO_CLEANUP_NOT_APPLIED' if overall == 'PASS' else 'FAILED_SAFE_READY_NOT_APPLIED'
    )
    out = {'task_origin':'SLC-G-GUILDS-CLEANUP-COMBO','version':'v1',
           'timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'mode':'READ_ONLY_FIRST_GATED_CLEANUP_PLAN',
           'db_write':False,'cleanup_applied':False,
           'combo_status':overall,'final_status':final,
           'explicit_write_approval_marker_present':marker,
           'results':results}
    OUT.write_text(json.dumps(out, indent=2))
    print(f'[slc_g_guilds_cleanup_combo_v1] {overall} final={final}')
    for r in results: print(f"  {r['verdict']:5s}  {r['name']}")
    return 0 if overall == 'PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
