#!/usr/bin/env python3
# SLC-H REJECTION/FAILURE MODES VALIDATOR (READ-ONLY)
import json, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
OUT = DESIGN_DIR / '_slc_h_rejection_failure_modes_v1_result.json'
SRC = DESIGN_DIR / 'slc_h_rejection_failure_modes_v1.json'

REQUIRED_CODES = {
    'second_server_locked':423,
    'server_not_available_for_account':403,
    'server_archived':410,
    'server_merged_redirect':308,
    'server_merge_pending':409,
    'route_patch_not_applied':423,
    'server_profiles_runtime_disabled':423,
    'auth_required':401,
    'rate_limited':429,
    'validation_error':422,
}

def main():
    errs = []
    if not SRC.exists():
        errs.append('source_missing')
    else:
        d = json.loads(SRC.read_text())
        if d.get('design_only') is not True: errs.append('design_only_not_true')
        if d.get('db_write') is not False: errs.append('db_write_not_false')
        modes = {m.get('error_code'): m for m in (d.get('failure_modes') or [])}
        for code, expected_status in REQUIRED_CODES.items():
            if code not in modes:
                errs.append(f'failure_mode_missing:{code}')
                continue
            if modes[code].get('http_status') != expected_status:
                errs.append(f'failure_mode_status_mismatch:{code}:expected={expected_status},got={modes[code].get("http_status")}')
            if 'retryable' not in modes[code]:
                errs.append(f'failure_mode_missing_retryable_flag:{code}')
        invs = d.get('invariants') or []
        if not any('retryable' in i for i in invs): errs.append('retryable_invariant_missing')
        if not any('merged_redirect' in i for i in invs): errs.append('merged_redirect_invariant_missing')
        if not any('route_patch_not_applied' in i for i in invs): errs.append('route_patch_gate_invariant_missing')

    out = {'task_origin':'SLC-H-REJECTION-MODES','timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'errors':errs,'verdict':'PASS' if not errs else 'FAIL'}
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-H-REJECTION-MODES {out['verdict']} errors={len(errs)}")
    for e in errs: print(' -', e)
    return 0 if out['verdict']=='PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
