#!/usr/bin/env python3
"""SLC-C COMBO — orchestrates all SLC-C validators + audits + dry-run.

Read-only. Aggregates per-step PASS/FAIL into a single combo result.
Exit 0 only if every sub-step passes.
"""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import DESIGN_DIR  # noqa: E402

NAME = 'slc_c_combo_v1'
SCRIPTS_DIR = Path('/app/backend/scripts')

STEPS = [
    ('account_entity_schema',           'validate_slc_c_account_entity_schema_v1.py'),
    ('account_wide_doc_contract',       'validate_slc_c_account_wide_document_contract_v1.py'),
    ('server_bound_doc_contract',       'validate_slc_c_server_bound_document_contract_v1.py'),
    ('collection_scope_matrix',         'validate_slc_c_collection_scope_migration_matrix_v1.py'),
    ('multishard_index_plan',           'validate_slc_c_multishard_index_plan_v1.py'),
    ('paid_free_currency_split',        'validate_slc_c_paid_free_currency_split_plan_v1.py'),
    ('server_aware_route_patch',        'validate_slc_c_server_aware_route_patch_contract_v1.py'),
    ('server_profile_creation_contract','validate_slc_c_server_profile_creation_contract_v1.py'),
    ('migration_phase_plan',            'validate_slc_c_single_to_multishard_migration_phase_plan_v1.py'),
    ('multishard_rollback_plan',        'validate_slc_c_multishard_rollback_plan_v1.py'),
    ('repo_multishard_preflight',       'audit_slc_c_repo_multishard_preflight.py'),
    ('critical_files_no_diff',          'audit_slc_c_critical_files_no_diff.py'),
    ('migration_dryrun_simulation',     'simulate_slc_c_migration_dryrun.py'),
    ('api_smoke_readonly',              'audit_slc_c_api_smoke_readonly.py'),
]


def main() -> int:
    results = {}
    all_pass = True
    for key, script in STEPS:
        p = SCRIPTS_DIR / script
        if not p.exists():
            results[key] = {'present': False, 'status': 'FAIL'}
            all_pass = False
            continue
        try:
            proc = subprocess.run(['python3', str(p)], capture_output=True, text=True, timeout=45)
            status = 'PASS' if proc.returncode == 0 else 'FAIL'
            results[key] = {
                'present': True,
                'status': status,
                'exit_code': proc.returncode,
                'stdout_tail': proc.stdout.strip().splitlines()[-3:] if proc.stdout else [],
            }
            if status == 'FAIL':
                all_pass = False
        except subprocess.TimeoutExpired:
            results[key] = {'present': True, 'status': 'FAIL', 'error': 'timeout'}
            all_pass = False
        except Exception as ex:
            results[key] = {'present': True, 'status': 'FAIL', 'error': str(ex)}
            all_pass = False

    payload = {
        'task_origin': 'SLC-C-COMBO',
        'version': 'v1',
        'mode': 'DESIGN_ONLY',
        'utc': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS' if all_pass else 'FAIL',
        'results': results,
        'safety': {
            'no_db_write': True,
            'no_runtime_change': True,
            'no_borea_exposure': True,
        },
    }
    out = DESIGN_DIR / f'_{NAME}_result.json'
    with out.open('w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    print(f'[{NAME}] {payload["status"]}')
    for k, v in results.items():
        print(f'  {v["status"]:4s}  {k}')
    return 0 if all_pass else 1


if __name__ == '__main__':
    sys.exit(main())
