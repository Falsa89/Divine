#!/usr/bin/env python3
"""SLC-D combo orchestrator."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_d_common import SLC_DIR  # noqa: E402

NAME = 'slc_d_merge_tooling_combo_v1'
SCRIPTS = Path('/app/backend/scripts')

STEPS = [
    ('preflight',                       'validate_slc_d_preflight_v1.py'),
    ('tooling_offline_plan',            'validate_server_merge_tooling_offline_plan_v1.py'),
    ('eligibility_policy',              'validate_server_merge_eligibility_policy_v1.py'),
    ('group_planning_contract',         'validate_server_merge_group_planning_contract_v1.py'),
    ('conflict_resolution_contract',    'validate_server_merge_conflict_resolution_contract_v1.py'),
    ('recovery_season_contract',        'validate_server_merge_recovery_season_contract_v1.py'),
    ('calendar_harmonization_policy',   'validate_server_merge_calendar_harmonization_policy_v1.py'),
    ('dryrun_scenarios',                'validate_server_merge_dryrun_scenarios_v1.py'),
    ('offline_simulation',              'simulate_slc_d_merge_tooling_offline_v1.py'),
    ('risk_matrix',                     'validate_server_merge_risk_matrix_v1.py'),
    ('abort_rollback_policy',           'validate_server_merge_abort_rollback_policy_v1.py'),
    ('runtime_safety_audit',            'audit_slc_d_runtime_safety_v1.py'),
    ('readiness_rollup',                'validate_slc_d_merge_tooling_offline_readiness_rollup_v1.py'),
]


def main() -> int:
    results = {}
    all_pass = True
    for key, script in STEPS:
        p = SCRIPTS / script
        if not p.exists():
            results[key] = {'status': 'FAIL', 'present': False}
            all_pass = False
            continue
        try:
            proc = subprocess.run(['python3', str(p)], capture_output=True, text=True, timeout=60)
            status = 'PASS' if proc.returncode == 0 else 'FAIL'
            results[key] = {'status': status, 'exit_code': proc.returncode,
                            'stdout_tail': proc.stdout.strip().splitlines()[-3:] if proc.stdout else []}
            if status == 'FAIL':
                all_pass = False
        except Exception as ex:
            results[key] = {'status': 'FAIL', 'error': str(ex)}
            all_pass = False
    payload = {
        'task': NAME, 'mode': 'DESIGN_ONLY',
        'utc': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS' if all_pass else 'FAIL', 'results': results,
        'safety': {'no_db_write': True, 'no_runtime_change': True,
                   'merge_execution_allowed': False,
                   'second_server_opening_allowed': False, 'borea_safe': True},
    }
    (SLC_DIR / f'_{NAME}_result.json').write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')
    print(f'[{NAME}] {payload["status"]}')
    for k, v in results.items():
        print(f'  {v.get("status","?"):4s}  {k}')
    return 0 if all_pass else 1


if __name__ == '__main__':
    sys.exit(main())
