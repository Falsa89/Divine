#!/usr/bin/env python3
"""PROJECT_I Track G validator — drift DB cleanup freeze-window plan."""
import json, sys
from pathlib import Path

MARKER = Path('/app/data/design/system_safety/project_i_drift_db_cleanup_freeze_window_plan_v1.json')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_G_DRIFT_DB_CLEANUP_FREEZE_WINDOW_PLAN_READY': fail('verdict mismatch')
    if m.get('db_cleanup_executed') is not False: fail('db_cleanup_executed must be False')
    if m.get('db_cleanup_authorized') is not False: fail('db_cleanup_authorized must be False')
    cats = m.get('target_drift_categories', [])
    if len(cats) < 3: fail('at least 3 target drift categories required')
    fw = m.get('freeze_window_plan', {})
    for k in ('window_duration_hours', 'required_operator_approval', 'required_rollback_script', 'required_backup_snapshot', 'required_metrics_sink_paused', 'steps'):
        if k not in fw: fail(f'freeze_window_plan missing {k}')
    if fw.get('required_operator_approval') is not True: fail('required_operator_approval must be True')
    if fw.get('required_rollback_script') is not True: fail('required_rollback_script must be True')
    if len(fw.get('steps', [])) < 6: fail('freeze_window_plan.steps must have at least 6 entries')
    forb = m.get('forbidden_in_track_g_respected', {})
    for k in ('db_cleanup_in_pack_i', 'roster_mutation', 'gacha_summon_behavior_change', 'borea_activation'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_g.{k} must be False')
    print('[PASS] PROJECT_I Track G drift DB cleanup freeze-window plan READY: 3 target categories; 6+ plan steps; no cleanup executed')
    sys.exit(0)

if __name__ == '__main__': main()
