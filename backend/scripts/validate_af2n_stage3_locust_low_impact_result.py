#!/usr/bin/env python3
"""Validator for AF2-L-LOCUST-LOW-IMPACT V19 result."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

RESULT = Path('/app/data/design/affinity/af2n_stage3_locust_low_impact_result_v1.json')


def main():
    if not RESULT.exists():
        r = Path('/app/backend/scripts/run_af2n_stage3_locust_low_impact.py')
        if r.exists(): subprocess.run(['python3', str(r)], timeout=180)
    failures=[]
    def rec(n,c):
        print(f'  [{"OK" if c else "X"}] {n}')
        if not c: failures.append(n)
    print('='*70); print('AF2-L-LOCUST-LOW-IMPACT V19 — Validator'); print('='*70)
    if not RESULT.exists(): rec('result_present', False); print('Overall: FAIL'); return 1
    d = json.loads(RESULT.read_text())
    rec('overall_pass', d.get('overall_status') == 'PASS')
    rec('triggers_zero', d.get('triggers_total') == 0)
    rec('locust_binary_present', d.get('locust_binary_present') is True)
    lr = d.get('locust_run', {})
    rec('locust_exit_ok', lr.get('exit_code') in (0, None))
    dl = d.get('delta', {})
    rec('delta_ledger_zero', dl.get('ledger_total', 0) == 0)
    rec('delta_borea_hero_zero', dl.get('borea_hero', 0) == 0)
    rec('delta_buffs_zero', dl.get('buffs', 0) == 0)
    rec('delta_battle_wiring_zero', dl.get('battle_wiring', 0) == 0)
    rec('delta_negative_inventory_zero', dl.get('negative_inventory', 0) == 0)
    fb = d.get('python_fallback', {}).get('counters', {})
    rec('fb_http_5xx_zero', fb.get('http_5xx', -1) == 0)
    rec('fb_borea_bad_zero', fb.get('borea_bad', -1) == 0)
    rec('fb_na_bad_zero', fb.get('na_bad', -1) == 0)
    rec('fb_replay_bad_zero', fb.get('replay_bad', -1) == 0)
    sf = d.get('safety_flags', {})
    rec('broad_off', sf.get('broad_rollout_authorized') is False)
    rec('public_spend_off', sf.get('public_spend_ui') is False)
    rec('battle_off', sf.get('battle_runtime_attached') is False)
    rec('buffs_off', sf.get('buffs_enabled') is False)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
