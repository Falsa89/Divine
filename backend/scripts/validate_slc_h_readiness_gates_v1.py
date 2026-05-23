#!/usr/bin/env python3
# SLC-H READINESS GATES VALIDATOR (READ-ONLY)
import json, os, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
SAFETY_DIR = ROOT / 'data/design/system_safety'
OUT = DESIGN_DIR / '_slc_h_readiness_gates_v1_result.json'
SRC = DESIGN_DIR / 'slc_h_readiness_gates_v1.json'
SLC_G_MARKER = SAFETY_DIR / 'slc_g_default_s1_migration_apply_result_v1.json'

REQUIRED_GATES = {f'SH-G{i}' for i in range(1,13)}

def main():
    errs = []
    if not SRC.exists():
        errs.append('readiness_gates_missing')
    else:
        d = json.loads(SRC.read_text())
        if d.get('design_only') is not True: errs.append('design_only_not_true')
        if d.get('db_write') is not False: errs.append('db_write_not_false')
        if d.get('implementation_status') != 'DESIGN_READY_NOT_IMPLEMENTED': errs.append('implementation_status_not_DESIGN_READY_NOT_IMPLEMENTED')
        if d.get('expected_default_verdict') != 'SLC_H_DESIGN_READY_NOT_IMPLEMENTED': errs.append('expected_default_verdict_mismatch')
        ids = {g.get('id') for g in (d.get('gates_required_before_any_runtime_implementation') or [])}
        for r in REQUIRED_GATES:
            if r not in ids: errs.append(f'gate_missing:{r}')

    # Verify SLC-G marker exists with migration_applied=true (SH-G1 prerequisite)
    if not SLC_G_MARKER.exists():
        errs.append('slc_g_migration_marker_missing')
    else:
        m = json.loads(SLC_G_MARKER.read_text())
        if not m.get('migration_applied'):
            errs.append('slc_g_migration_applied_not_true')
        if m.get('route_patch_applied') is not False:
            errs.append('slc_g_route_patch_applied_must_be_false')
        if m.get('second_server_opening_allowed') is not False:
            errs.append('slc_g_second_server_opening_must_be_false')

    # Verify runtime flags are STILL unset (SH-G5)
    if os.environ.get('SERVER_PROFILES_RUNTIME_ENABLED'):
        errs.append('SERVER_PROFILES_RUNTIME_ENABLED_must_be_unset')
    if os.environ.get('SECOND_SERVER_OPENING_ENABLED'):
        errs.append('SECOND_SERVER_OPENING_ENABLED_must_be_unset')

    # Verify no runtime route registered for the 5 future paths (SH-G10)
    routes_dir = ROOT / 'backend' / 'routes'
    forbidden_routes = ['/api/servers','/api/account/server-profiles','/api/account/active-server']
    if routes_dir.exists():
        import re
        for f in routes_dir.glob('*.py'):
            text = f.read_text(errors='ignore')
            for fr in forbidden_routes:
                # look for decorators that mention the exact path string
                if re.search(r'["\']' + re.escape(fr) + r'["\']', text):
                    errs.append(f'runtime_route_already_registered:{fr}_in_{f.name}')

    out = {'task_origin':'SLC-H-READINESS-GATES','timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'errors':errs,'verdict':'PASS' if not errs else 'FAIL'}
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-H-READINESS-GATES {out['verdict']} errors={len(errs)}")
    for e in errs: print(' -', e)
    return 0 if out['verdict']=='PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
