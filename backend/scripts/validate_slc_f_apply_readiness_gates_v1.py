#!/usr/bin/env python3
# SLC-F APPLY READINESS GATES VALIDATOR (READ-ONLY)
import json, os, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
SAFETY_DIR = ROOT / 'data/design/system_safety'
OUT = DESIGN_DIR / '_slc_f_apply_readiness_gates_v1_result.json'
SRC = DESIGN_DIR / 'slc_f_apply_readiness_gates_v1.json'
SLC_G_MARKER = SAFETY_DIR / 'slc_g_default_s1_migration_apply_result_v1.json'

REQUIRED_GATES = {f'SF-AG-{i}' for i in range(1, 14)}

def main():
    errs = []
    if not SRC.exists():
        errs.append('source_missing')
    else:
        d = json.loads(SRC.read_text())
        if d.get('design_only') is not True: errs.append('design_only_not_true')
        if d.get('route_patch_applied') is not False: errs.append('route_patch_applied_not_false')
        if d.get('expected_default_verdict') != 'SLC_F_APPLY_READY_NOT_APPLIED':
            errs.append('expected_default_verdict_mismatch')
        ids = {g.get('id') for g in (d.get('gates_required_before_runtime_apply') or [])}
        for r in REQUIRED_GATES:
            if r not in ids: errs.append(f'gate_missing:{r}')

    # Verify SLC-G marker (SF-AG-1)
    if not SLC_G_MARKER.exists():
        errs.append('slc_g_migration_marker_missing')
    else:
        m = json.loads(SLC_G_MARKER.read_text())
        if not m.get('migration_applied'):
            errs.append('slc_g_migration_applied_not_true')

    # SF-AG-13: SECOND_SERVER_OPENING_ENABLED must be unset
    if os.environ.get('SECOND_SERVER_OPENING_ENABLED'):
        errs.append('SECOND_SERVER_OPENING_ENABLED_must_be_unset')

    out = {'task_origin':'SLC-F-APPLY-READINESS-GATES','timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'errors':errs,'verdict':'PASS' if not errs else 'FAIL'}
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-F-APPLY-READINESS-GATES {out['verdict']} errors={len(errs)}")
    for e in errs: print(' -', e)
    return 0 if out['verdict']=='PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
