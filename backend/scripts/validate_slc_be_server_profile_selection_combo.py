#!/usr/bin/env python3
"""SLC-BE COMBO — orchestrate all SLC-BE validators + audit."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import DESIGN_DIR  # noqa: E402

NAME = 'slc_be_combo_v1'
SCRIPTS = Path('/app/backend/scripts')

STEPS = [
    ('preflight',                                'validate_slc_be_preflight_v1.py'),
    ('server_profile_creation_contract',         'validate_server_profile_creation_contract_v1.py'),
    ('server_profile_default_values',            'validate_server_profile_default_values_v1.py'),
    ('server_selection_endpoint_contract',       'validate_server_selection_endpoint_contract_v1.py'),
    ('server_status_transition_policy',          'validate_server_status_transition_policy_v1.py'),
    ('new_player_server_routing_policy',         'validate_new_player_server_routing_policy_v1.py'),
    ('active_server_resolution_contract',        'validate_active_server_resolution_contract_v1.py'),
    ('dry_run_scenarios',                        'validate_server_profile_creation_dry_run_scenarios_v1.py'),
    ('runtime_safety_audit',                     'audit_server_selection_runtime_safety_v1.py'),
    ('readiness_rollup',                         'validate_server_lifecycle_profile_selection_readiness_rollup_v1.py'),
]


def main() -> int:
    results = {}
    all_pass = True
    for key, script in STEPS:
        p = SCRIPTS / script
        if not p.exists():
            results[key] = {'present': False, 'status': 'FAIL'}
            all_pass = False
            continue
        try:
            proc = subprocess.run(['python3', str(p)], capture_output=True, text=True, timeout=45)
            status = 'PASS' if proc.returncode == 0 else 'FAIL'
            results[key] = {'status': status, 'exit_code': proc.returncode,
                            'stdout_tail': proc.stdout.strip().splitlines()[-3:] if proc.stdout else []}
            if status == 'FAIL':
                all_pass = False
        except Exception as ex:
            results[key] = {'status': 'FAIL', 'error': str(ex)}
            all_pass = False
    payload = {
        'task_origin': 'SLC-BE-COMBO', 'version': 'v1', 'mode': 'DESIGN_ONLY',
        'utc': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS' if all_pass else 'FAIL',
        'results': results,
        'safety': {'no_db_write': True, 'no_runtime_change': True, 'no_borea_exposure': True, 'second_server_opening_allowed': False},
    }
    out = DESIGN_DIR / f'_{NAME}_result.json'
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')
    print(f'[{NAME}] {payload["status"]}')
    for k, v in results.items():
        print(f'  {v.get("status","?"):4s}  {k}')
    return 0 if all_pass else 1


if __name__ == '__main__':
    sys.exit(main())
