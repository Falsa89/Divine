#!/usr/bin/env python3
"""LIVE-MODES + SLC-NEXT COMBO — orchestrate all live-mode + SLC-Next validators."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _live_modes_common import LIVE_MODES_DIR  # noqa: E402

NAME = 'live_modes_slc_next_combo_v1'
SCRIPTS = Path('/app/backend/scripts')

STEPS = [
    ('reconciliation',          'validate_live_mode_benchmark_reconciliation_v1.py'),
    ('calendar',                'validate_live_mode_calendar_v1.py'),
    ('reward_framework',        'validate_live_mode_reward_framework_v1.py'),
    ('broadcast_policy',        'validate_live_mode_broadcast_policy_v1.py'),
    ('benchmark_risk_policy',   'validate_live_mode_benchmark_risk_policy_v1.py'),
    ('sanctuary_housing_note',  'validate_sanctuary_housing_dimora_divina_note_v1.py'),
    ('runtime_safety_audit',    'audit_live_mode_reconciliation_runtime_safety_v1.py'),
    ('slc_next_plan',           'validate_slc_next_after_be_plan_v1.py'),
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
        'task': NAME, 'mode': 'DESIGN_ONLY',
        'utc': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS' if all_pass else 'FAIL',
        'results': results,
        'safety': {'no_db_write': True, 'no_runtime_change': True,
                   'no_borea_exposure_introduced': True,
                   'second_server_opening_allowed': False},
    }
    out = LIVE_MODES_DIR / f'_{NAME}_result.json'
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')
    print(f'[{NAME}] {payload["status"]}')
    for k, v in results.items():
        print(f'  {v.get("status","?"):4s}  {k}')
    return 0 if all_pass else 1


if __name__ == '__main__':
    sys.exit(main())
