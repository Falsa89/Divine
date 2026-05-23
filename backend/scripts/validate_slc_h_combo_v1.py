#!/usr/bin/env python3
# SLC-H COMBO ORCHESTRATOR (READ-ONLY)
import json, os, sys, subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
SCRIPTS_DIR = ROOT / 'backend/scripts'
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
OUT = DESIGN_DIR / '_slc_h_combo_v1_result.json'

SUB = [
    ('endpoint_contract', 'validate_slc_h_endpoint_contract_v1.py'),
    ('rejection_modes', 'validate_slc_h_rejection_modes_v1.py'),
    ('server_status_contract', 'validate_slc_h_server_status_contract_v1.py'),
    ('readiness_gates', 'validate_slc_h_readiness_gates_v1.py'),
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

    final = 'SLC_H_DESIGN_READY_NOT_IMPLEMENTED' if overall == 'PASS' else 'FAILED_SAFE_READY_NOT_APPLIED'
    out = {'task_origin':'SLC-H-COMBO','version':'v1',
           'timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'mode':'DESIGN_ONLY_CONTRACT_ONLY_READ_ONLY','db_write':False,
           'runtime_implementation_status':'NOT_IMPLEMENTED',
           'combo_status':overall,'final_status':final,'results':results}
    OUT.write_text(json.dumps(out, indent=2))
    print(f'[slc_h_combo_v1] {overall} final={final}')
    for r in results: print(f"  {r['verdict']:5s}  {r['name']}")
    return 0 if overall == 'PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
