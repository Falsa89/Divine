#!/usr/bin/env python3
# SLC-F APPLY PREP + HOUSING ADDENDUM COMBO (READ-ONLY)
import json, os, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
SCRIPTS = ROOT / 'backend/scripts'
OUT = ROOT / 'data/design/server_lifecycle/_slc_f_apply_prep_housing_addendum_combo_v1_result.json'

SUB = [
    ('slc_f_apply_prep_staged_plan','validate_slc_f_apply_prep_staged_plan_v1.py'),
    ('slc_f_apply_readiness_gates','validate_slc_f_apply_readiness_gates_v1.py'),
    ('housing_dimora_divina_v2','validate_sanctuary_housing_dimora_divina_v2.py'),
    ('housing_runtime_safety_audit','audit_dimora_divina_runtime_safety_v1.py'),
]

def main():
    results = []
    overall = 'PASS'
    for name, script in SUB:
        p = SCRIPTS / script
        if not p.exists():
            results.append({'name':name,'script':script,'verdict':'MISS'})
            overall = 'FAIL'; continue
        proc = subprocess.run(['python3', str(p)], capture_output=True, text=True, timeout=60)
        v = 'PASS' if proc.returncode == 0 else 'FAIL'
        if v == 'FAIL': overall = 'FAIL'
        results.append({'name':name,'script':script,'verdict':v,'exit_code':proc.returncode})

    apply_marker = os.environ.get('SLC_F_ROUTE_PATCH_APPLY_APPROVAL','').lower() == 'true'
    final = 'SLC_F_APPLY_READY_NOT_APPLIED_WITH_HOUSING_ADDENDUM_READY' if overall == 'PASS' and not apply_marker else (
        'SLC_F_APPLY_READY_WITH_MARKER_PRESENT_WITH_HOUSING_ADDENDUM_READY' if overall == 'PASS' and apply_marker else
        'FAILED_SAFE_READY_NOT_APPLIED'
    )
    out = {'task_origin':'SLC-F-APPLY-PREP-HOUSING-ADDENDUM-COMBO','version':'v1',
           'timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'combo_status':overall,'final_status':final,
           'slc_f_apply_marker_present':apply_marker,
           'route_patch_applied':False,'housing_runtime_implemented':False,
           'results':results}
    OUT.write_text(json.dumps(out, indent=2))
    print(f'[slc_f_apply_prep_housing_addendum_combo_v1] {overall} final={final}')
    for r in results: print(f"  {r['verdict']:5s}  {r['name']}")
    return 0 if overall == 'PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
