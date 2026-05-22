#!/usr/bin/env python3
# SLC-G IDEMPOTENCY CONTRACT VALIDATOR (READ-ONLY)
import json, os, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
OUT = DESIGN_DIR / '_slc_g_idempotency_contract_v1_result.json'
SRC = DESIGN_DIR / 'slc_g_idempotency_contract_v1.json'

REQUIRED_RULES = [
    'backfill_uses_set_only_if_missing_for_server_id_and_account_id',
    'marker_field_slc_g_default_s1_set_only_added_when_field_was_missing',
    'rerun_must_produce_zero_additional_writes_when_state_already_consistent',
    'rerun_must_be_safe_against_partial_failures',
    'no_duplicate_documents_inserted_ever',
    'no_pre_existing_server_id_overwritten',
    'no_pre_existing_account_id_overwritten',
]

def main():
    errs = []
    if not SRC.exists():
        errs.append('contract_missing')
    else:
        d = json.loads(SRC.read_text())
        if d.get('design_only') is not True: errs.append('design_only_not_true')
        if d.get('db_write') is not False: errs.append('db_write_not_false')
        if d.get('migration_applied') is not False: errs.append('migration_applied_not_false')
        rules = set(d.get('idempotency_rules') or [])
        for r in REQUIRED_RULES:
            if r not in rules: errs.append(f'rule_missing:{r}')
        if 'idempotency_verification' not in d:
            errs.append('idempotency_verification_missing')
        if 'failure_modes_handled' not in d:
            errs.append('failure_modes_handled_missing')
        if d.get('on_failure_action') != 'return_FAILED_SAFE_AND_TRIGGER_ROLLBACK_PLAN':
            errs.append('on_failure_action_must_be_failed_safe_and_trigger_rollback')

    out = {'task_origin':'SLC-G-IDEMPOTENCY-CONTRACT','timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'errors':errs,'verdict':'PASS' if not errs else 'FAIL'}
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-G-IDEMPOTENCY-CONTRACT {out['verdict']} errors={len(errs)}")
    for e in errs: print(' -', e)
    return 0 if out['verdict']=='PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
