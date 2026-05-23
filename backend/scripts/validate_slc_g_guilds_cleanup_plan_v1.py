#!/usr/bin/env python3
# SLC-G-GUILDS CLEANUP PLAN VALIDATOR (READ-ONLY)
import json, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
OUT = DESIGN_DIR / '_slc_g_guilds_cleanup_plan_v1_result.json'
SRC = DESIGN_DIR / 'slc_g_guilds_cleanup_plan_v1.json'

REQUIRED_CONSTRAINTS = [
    'only the 2 specifically targeted _id values may be touched',
    'only fields that are absent may be set',
    'NO update on any document not in target list',
    'NO delete operation at any phase',
    'NO change to existing leader_id, members, name, created_at, level, exp',
    'NO change to AF2-N collections (user_gift_inventory, gift_transaction_ledger, user_affinity_state)',
    'NO change to protected runtime files',
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
        if d.get('never_delete_any_document') is not True: errs.append('never_delete_any_document_not_true')
        if d.get('never_drop_collection') is not True: errs.append('never_drop_collection_not_true')
        if d.get('never_drop_index') is not True: errs.append('never_drop_index_not_true')
        if d.get('never_overwrite_existing_fields') is not True: errs.append('never_overwrite_existing_fields_not_true')
        if d.get('set_only_if_missing') is not True: errs.append('set_only_if_missing_not_true')
        if d.get('target_docs_count') != 2: errs.append('target_docs_count_must_be_2')
        if d.get('target_collection') != 'guilds': errs.append('target_collection_must_be_guilds')
        per = d.get('per_doc_proposed_action') or []
        if len(per) != 2: errs.append('per_doc_proposed_action_must_have_2_entries')
        for i, doc in enumerate(per):
            if not doc.get('_id'): errs.append(f'doc[{i}]_id_missing')
            if doc.get('writes_only_if_field_absent') is not True:
                errs.append(f'doc[{i}]_writes_only_if_field_absent_not_true')
            for vk in ('user_id_present_and_equal_leader_id','account_id_present_and_equal_leader_id','server_id_equals_s1','members_array_unchanged','leader_id_unchanged','created_at_unchanged'):
                if not (doc.get('verification_after') or {}).get(vk):
                    errs.append(f'doc[{i}]_verification_missing:{vk}')
        constraints = set(d.get('safety_constraints') or [])
        for c in REQUIRED_CONSTRAINTS:
            if c not in constraints: errs.append(f'safety_constraint_missing:{c}')
        if d.get('apply_script_creation_is_separate_gated_step') is not True:
            errs.append('apply_script_must_be_separate_gated_step')

    out = {'task_origin':'SLC-G-GUILDS-CLEANUP-PLAN','timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'errors':errs,'verdict':'PASS' if not errs else 'FAIL'}
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-G-GUILDS-CLEANUP-PLAN {out['verdict']} errors={len(errs)}")
    for e in errs: print(' -', e)
    return 0 if out['verdict']=='PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
