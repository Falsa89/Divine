#!/usr/bin/env python3
"""Validator for AF2-N-INVENTORY-EXTENDED-MONITORING V17."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

RESULT = Path('/app/data/design/affinity/af2n_inventory_extended_monitoring_v17_result.json')


def main():
    if not RESULT.exists():
        # Run the runner first
        runner = Path('/app/backend/scripts/run_af2n_inventory_extended_monitoring_v17.py')
        if not runner.exists():
            print('runner missing'); return 1
        subprocess.run(['python3', str(runner)], timeout=180)
    if not RESULT.exists():
        print('result not produced'); return 1
    data = json.loads(RESULT.read_text())
    failures = []
    def rec(n, c):
        print(f'  [{"OK" if c else "X"}] {n}')
        if not c: failures.append(n)
    print('='*70); print('AF2-N-INVENTORY-EXTENDED-MONITORING V17 — Validator'); print('='*70)
    rec('overall_pass', data.get('overall_status') == 'PASS')
    rec('runtime_stage1_only', data.get('runtime_attached_stage1_allowlist_only') is True)
    rec('triggers_total_zero', data.get('triggers_total') == 0)
    c = data.get('counters', {})
    rec('samples_total_>=120', c.get('samples_total', 0) >= 120)
    rec('borea_not_404_zero', c.get('borea_not_404', -1) == 0)
    rec('non_allowlist_other_zero', c.get('non_allowlist_other', -1) == 0)
    rec('idempotent_replay_bad_zero', c.get('idempotent_replay_bad', -1) == 0)
    rec('http_5xx_zero', c.get('http_5xx', -1) == 0)
    rec('fresh_spend_fail_zero', c.get('fresh_spend_fail', -1) == 0)
    post = data.get('post', {})
    rec('post_negative_inventory_zero', post.get('negative_inventory', -1) == 0)
    rec('post_buffs_zero', post.get('buffs', -1) == 0)
    rec('post_battle_zero', post.get('battle_wiring', -1) == 0)
    rec('inv_mut_delta_eq_aff_mut_delta', post.get('inv_mut_delta') == post.get('aff_mut_delta'))
    sf = data.get('safety_flags', {})
    rec('broad_rollout_off', sf.get('broad_rollout_authorized') is False)
    rec('buffs_off', sf.get('buffs_enabled') is False)
    rec('battle_off', sf.get('battle_runtime_attached') is False)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
