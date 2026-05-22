#!/usr/bin/env python3
"""Combo orchestrator for benchmark canonical pack."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _benchmark_canonical_common import CANON_DIR  # noqa: E402

NAME = 'benchmark_canonical_combo_v1'
SCRIPTS = Path('/app/backend/scripts')

STEPS = [
    ('index',                         'validate_benchmark_canonical_index_v1.py'),
    ('live_special_modes',            'validate_live_special_modes_canonical_v1.py'),
    ('system_library',                'validate_benchmark_system_library_v1.py'),
    ('risk_policy_expanded',          'validate_benchmark_risk_policy_expanded_v1.py'),
    ('sanctuary_housing',             'validate_sanctuary_housing_dimora_divina_canonical_v1.py'),
    ('summon_pity_fragment',          'validate_summon_pity_fragment_canonical_v1.py'),
    ('server_lifecycle_cal_merge',    'validate_server_lifecycle_calendar_merge_canonical_v1.py'),
    ('event_hub_daily_guide',         'validate_event_hub_daily_guide_canonical_v1.py'),
    ('guild_social_coop',             'validate_guild_social_coop_canonical_v1.py'),
    ('equipment_forge_relic',         'validate_equipment_forge_relic_canonical_v1.py'),
    ('battle_stats_reporting',        'validate_battle_stats_reporting_canonical_v1.py'),
    ('slc_f_next_checkpoint',         'validate_slc_f_next_checkpoint_canonical_v1.py'),
    ('runtime_safety_audit',          'audit_benchmark_canonical_runtime_safety_v1.py'),
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
        'status': 'PASS' if all_pass else 'FAIL', 'results': results,
        'safety': {'no_db_write': True, 'no_runtime_change': True,
                   'second_server_opening_allowed': False, 'borea_safe': True},
    }
    (CANON_DIR / f'_{NAME}_result.json').write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')
    print(f'[{NAME}] {payload["status"]}')
    for k, v in results.items():
        print(f'  {v.get("status","?"):4s}  {k}')
    return 0 if all_pass else 1


if __name__ == '__main__':
    sys.exit(main())
