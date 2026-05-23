#!/usr/bin/env python3
# SLC-G-GUILDS CLEANUP ROLLBACK PLAN VALIDATOR (READ-ONLY)
import json, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
OUT = DESIGN_DIR / '_slc_g_guilds_cleanup_rollback_plan_v1_result.json'
SRC = DESIGN_DIR / 'slc_g_guilds_cleanup_rollback_plan_v1.json'

REQUIRED_STEPS = [
    'freeze_writes_design_only_check',
    'verify_marker_field_present_only_on_2_targets',
    'unset_added_fields_only_where_marker_true_and_id_in_target_list',
    'verify_post_rollback_doc_keys_match_pre_cleanup_keys',
    'verify_members_array_unchanged',
    'verify_leader_id_unchanged',
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
        if d.get('cleanup_applied') is not False: errs.append('cleanup_applied_not_false')
        steps = set(d.get('rollback_steps') or [])
        for s in REQUIRED_STEPS:
            if s not in steps: errs.append(f'step_missing:{s}')
        if d.get('rollback_must_be_idempotent') is not True: errs.append('rollback_idempotent_not_true')
        if d.get('rollback_rehearsal_dry_run_required') is not True: errs.append('rollback_rehearsal_dry_run_not_required')
        if d.get('never_delete_documents') is not True: errs.append('never_delete_documents_not_true')
        if d.get('never_drop_collection_or_index') is not True: errs.append('never_drop_collection_or_index_not_true')
        strat = d.get('rollback_strategy') or {}
        if strat.get('marker_field') != '_slc_g_guilds_cleanup_marker':
            errs.append('marker_field_mismatch')
        fields = set(strat.get('fields_to_unset_if_marker_true') or [])
        for f in ('user_id','account_id','server_id','_slc_g_guilds_cleanup_marker','_slc_g_guilds_cleanup_classification'):
            if f not in fields: errs.append(f'fields_to_unset_missing:{f}')

    out = {'task_origin':'SLC-G-GUILDS-CLEANUP-ROLLBACK-PLAN','timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'errors':errs,'verdict':'PASS' if not errs else 'FAIL'}
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-G-GUILDS-CLEANUP-ROLLBACK-PLAN {out['verdict']} errors={len(errs)}")
    for e in errs: print(' -', e)
    return 0 if out['verdict']=='PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
