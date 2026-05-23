#!/usr/bin/env python3
# SLC-F APPLY PREP STAGED PLAN VALIDATOR (READ-ONLY)
import json, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
OUT = DESIGN_DIR / '_slc_f_apply_prep_staged_plan_v1_result.json'
SRC = DESIGN_DIR / 'slc_f_apply_prep_staged_plan_v1.json'

REQUIRED_BATCH_IDS = {'BATCH-0','BATCH-1','BATCH-2','BATCH-3','BATCH-4'}

def main():
    errs = []
    if not SRC.exists():
        errs.append('plan_missing')
    else:
        d = json.loads(SRC.read_text())
        if d.get('design_only') is not True: errs.append('design_only_not_true')
        if d.get('db_write') is not False: errs.append('db_write_not_false')
        if d.get('route_patch_applied') is not False: errs.append('route_patch_applied_not_false')
        if d.get('explicit_apply_marker_required') != 'SLC_F_ROUTE_PATCH_APPLY_APPROVAL=true':
            errs.append('apply_marker_string_incorrect')
        if d.get('writes_to_protected_files_in_this_task') is not False: errs.append('writes_to_protected_files_must_be_false')
        if d.get('writes_to_runtime_routes_in_this_task') is not False: errs.append('writes_to_runtime_routes_must_be_false')
        if d.get('apply_script_status') != 'NOT_CREATED_IN_THIS_TASK': errs.append('apply_script_must_be_NOT_CREATED_IN_THIS_TASK')
        batches = {b.get('id'): b for b in (d.get('batches') or [])}
        for r in REQUIRED_BATCH_IDS:
            if r not in batches: errs.append(f'batch_missing:{r}')
        # Plan-only batches MUST have writes_to_routes=false
        for plan_only in ('BATCH-3','BATCH-4'):
            if plan_only in batches and batches[plan_only].get('writes_to_routes') is not False:
                errs.append(f'{plan_only}_must_be_plan_only_writes_to_routes_false')
        # BATCH-0 must be design-only
        if 'BATCH-0' in batches and batches['BATCH-0'].get('writes_to_routes') is not False:
            errs.append('BATCH-0_must_be_design_only_writes_to_routes_false')
        # Safety constraints present
        sc = d.get('safety_constraints') or []
        for need in ('AF2-N', 'API smoke', 'SLC_F_ROUTE_PATCH_APPLY_APPROVAL'):
            if not any(need in c for c in sc): errs.append(f'safety_constraint_missing_keyword:{need}')

    out = {'task_origin':'SLC-F-APPLY-PREP-STAGED-PLAN','timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'errors':errs,'verdict':'PASS' if not errs else 'FAIL'}
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-F-APPLY-PREP-STAGED-PLAN {out['verdict']} errors={len(errs)}")
    for e in errs: print(' -', e)
    return 0 if out['verdict']=='PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
