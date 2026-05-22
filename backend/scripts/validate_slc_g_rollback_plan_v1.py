#!/usr/bin/env python3
# SLC-G ROLLBACK PLAN VALIDATOR (READ-ONLY)
import json, os, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
OUT = DESIGN_DIR / '_slc_g_rollback_plan_v1_result.json'
SRC = DESIGN_DIR / 'slc_g_rollback_plan_v1.json'

REQUIRED_STEPS = [
    'freeze_writes_design_only_check',
    'verify_marker_field_present_count',
    'unset_server_id_where_marker_true',
    'unset_account_id_where_marker_true_and_was_default',
    'verify_post_rollback_counts_match_pre_migration_counts',
    'verify_af2n_state_unchanged',
    'verify_api_smoke_unchanged',
    'emit_rollback_report',
]

def main():
    errs = []
    if not SRC.exists():
        errs.append('plan_missing')
    else:
        d = json.loads(SRC.read_text())
        if d.get('design_only') is not True: errs.append('design_only_not_true')
        if d.get('db_write') is not False: errs.append('db_write_not_false')
        if d.get('migration_applied') is not False: errs.append('migration_applied_not_false')
        steps = set(d.get('rollback_steps') or [])
        for s in REQUIRED_STEPS:
            if s not in steps: errs.append(f'step_missing:{s}')
        if d.get('rollback_must_be_idempotent') is not True:
            errs.append('rollback_must_be_idempotent_not_true')
        if d.get('rollback_must_be_rehearsed_dry_run_before_real_run') is not True:
            errs.append('rollback_rehearsal_dry_run_not_required')
        if d.get('never_drops_collections') is not True:
            errs.append('never_drops_collections_not_true')
        if d.get('never_drops_indexes_without_explicit_approval') is not True:
            errs.append('never_drops_indexes_safety_missing')
        strat = d.get('rollback_strategy') or {}
        if 'marker_field' not in strat:
            errs.append('marker_field_missing')

    out = {'task_origin':'SLC-G-ROLLBACK-PLAN','timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'errors':errs,'verdict':'PASS' if not errs else 'FAIL'}
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-G-ROLLBACK-PLAN {out['verdict']} errors={len(errs)}")
    for e in errs: print(' -', e)
    return 0 if out['verdict']=='PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
