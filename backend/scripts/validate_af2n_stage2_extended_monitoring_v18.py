#!/usr/bin/env python3
"""Validator for AF2-N-STAGE2-EXTENDED-MONITORING V18."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

RESULT = Path('/app/data/design/affinity/af2n_stage2_extended_monitoring_v18_result.json')


def main():
    if not RESULT.exists():
        r = Path('/app/backend/scripts/run_af2n_stage2_extended_monitoring_v18.py')
        if r.exists(): subprocess.run(['python3', str(r)], timeout=180)
    if not RESULT.exists(): print('result missing'); return 1
    d = json.loads(RESULT.read_text())
    failures=[]
    def rec(n,c):
        print(f'  [{"OK" if c else "X"}] {n}')
        if not c: failures.append(n)
    print('='*70); print('AF2-N-STAGE2-EXTENDED-MONITORING V18 — Validator'); print('='*70)
    rec('overall_pass', d.get('overall_status') == 'PASS')
    rec('triggers_zero', d.get('triggers_total') == 0)
    c = d.get('counters', {})
    rec('samples_>=160', c.get('samples_total', 0) >= 160)
    rec('borea_bad_zero', c.get('borea_bad', -1) == 0)
    rec('non_allow_bad_zero', c.get('non_allowlist_bad', -1) == 0)
    rec('replay_bad_zero', c.get('replay_bad', -1) == 0)
    rec('fresh_spend_fail_zero', c.get('fresh_spend_fail', -1) == 0)
    rec('http_5xx_zero', c.get('http_5xx', -1) == 0)
    p = d.get('post', {})
    rec('post_neg_inv_zero', p.get('negative_inventory') == 0)
    rec('inv_delta_eq_aff_delta', p.get('inv_mut_delta') == p.get('aff_mut_delta'))
    rec('post_buffs_zero', p.get('buffs') == 0)
    rec('post_battle_zero', p.get('battle_wiring') == 0)
    sf = d.get('safety_flags', {})
    rec('broad_off', sf.get('broad_rollout_authorized') is False)
    rec('public_spend_off', sf.get('public_spend_ui') is False)
    rec('battle_off', sf.get('battle_runtime_attached') is False)
    rec('buffs_off', sf.get('buffs_enabled') is False)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
