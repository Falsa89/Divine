#!/usr/bin/env python3
"""Validator for Stage2 monitoring V17.

Accepts:
  - PASS (Stage2 applied and monitoring clean)
  - NOT_APPLICABLE_READY_NOT_APPLIED (Stage2 NOT applied, valid safe path)
  - NOT_APPLICABLE_NO_APPLY_RESULT (no apply attempted)
"""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

RESULT = Path('/app/data/design/affinity/af2n_stage2_monitoring_v17_result.json')
VALID = {'PASS', 'NOT_APPLICABLE_READY_NOT_APPLIED', 'NOT_APPLICABLE_NO_APPLY_RESULT'}


def main():
    if not RESULT.exists():
        runner = Path('/app/backend/scripts/run_af2n_stage2_monitoring_v17.py')
        if runner.exists():
            subprocess.run(['python3', str(runner)], timeout=180)
    failures = []
    def rec(n, c):
        print(f'  [{"OK" if c else "X"}] {n}')
        if not c: failures.append(n)
    print('='*70); print('AF2-N-STAGE2-MONITORING V17 — Validator'); print('='*70)
    if not RESULT.exists():
        rec('result_present', False); print('Overall: FAIL'); return 1
    data = json.loads(RESULT.read_text())
    status = data.get('overall_status')
    rec('status_known', status in VALID)
    if status == 'PASS':
        c = data.get('counters', {})
        rec('borea_bad_zero', c.get('borea_bad', -1) == 0)
        rec('non_allowlist_bad_zero', c.get('non_allowlist_bad', -1) == 0)
        rec('stage2_fresh_fail_zero', c.get('stage2_fresh_fail', -1) == 0)
        rec('http_5xx_zero', c.get('http_5xx', -1) == 0)
        post = data.get('post', {})
        rec('post_negative_inventory_zero', post.get('negative_inventory') == 0)
        rec('inv_mut_delta_eq_aff', post.get('inv_mut_delta') == post.get('aff_mut_delta'))
        rec('post_buffs_zero', post.get('buffs') == 0)
        rec('post_battle_zero', post.get('battle_wiring') == 0)
        sf = data.get('safety_flags', {})
        rec('broad_off', sf.get('broad_rollout_authorized') is False)
        rec('buffs_off', sf.get('buffs_enabled') is False)
        rec('battle_off', sf.get('battle_runtime_attached') is False)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
