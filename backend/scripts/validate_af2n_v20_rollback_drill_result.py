#!/usr/bin/env python3
"""Validator for V20 rollback drills result."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

RESULT = Path('/app/data/design/affinity/af2n_v20_rollback_drill_result_v1.json')


def main():
    if not RESULT.exists():
        r = Path('/app/backend/scripts/run_af2n_v20_rollback_drills.py')
        if r.exists(): subprocess.run(['python3', str(r)], timeout=120)
    failures = []
    def rec(n, c):
        print(f'  [{"OK" if c else "X"}] {n}')
        if not c: failures.append(n)
    print('='*70); print('AF2-N-V20-ROLLBACK-DRILLS — Validator'); print('='*70)
    if not RESULT.exists(): rec('result_present', False); print('Overall: FAIL'); return 1
    d = json.loads(RESULT.read_text())
    rec('overall_pass', d.get('overall_status') == 'PASS')
    rec('mode_dry_run_only', d.get('mode') == 'dry_run_only')
    rec('no_state_change', d.get('no_actual_state_change') is True)
    drills = d.get('drills', {})
    rec('drill_stage3_present', 'stage3_rollback_dry_run' in drills)
    rec('drill_stage2_present', 'stage2_rollback_dry_run' in drills)
    rec('drill_inv_flag_plan_present', 'inventory_flag_rollback_plan' in drills)
    rec('drill_full_canary_plan_present', 'full_af2n_canary_rollback_plan' in drills)
    rec('drill_ui_preview_plan_present', 'ui_preview_rollback_plan' in drills)
    rec('drill_locust_stop_plan_present', 'locust_stop_abort_plan' in drills)
    rec('drill_db_backup_plan_present', 'db_backup_restore_plan' in drills)
    if 'stage3_rollback_dry_run' in drills:
        rec('stage3_dry_run_exit_ok', drills['stage3_rollback_dry_run'].get('exit_code') == 0)
    if 'stage2_rollback_dry_run' in drills:
        rec('stage2_dry_run_exit_ok', drills['stage2_rollback_dry_run'].get('exit_code') == 0)
    sf = d.get('safety_flags', {})
    rec('broad_off', sf.get('broad_rollout_authorized') is False)
    rec('public_spend_off', sf.get('public_spend_ui') is False)
    rec('stage4_applied_false', sf.get('stage4_applied') is False)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
