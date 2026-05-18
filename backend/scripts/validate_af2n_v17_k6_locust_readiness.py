#!/usr/bin/env python3
"""Validator for AF2-L-K6/LOCUST READINESS V17."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

RESULT = Path('/app/data/design/affinity/af2n_v17_k6_locust_readiness_result_v1.json')


def main():
    if not RESULT.exists():
        runner = Path('/app/backend/scripts/run_af2n_v17_k6_locust_readiness.py')
        if runner.exists():
            subprocess.run(['python3', str(runner)], timeout=240)
    failures = []
    def rec(n, c):
        print(f'  [{"OK" if c else "X"}] {n}')
        if not c: failures.append(n)
    print('='*70); print('K6/LOCUST READINESS V17 — Validator'); print('='*70)
    if not RESULT.exists():
        rec('result_present', False); print('Overall: FAIL'); return 1
    data = json.loads(RESULT.read_text())
    rec('overall_pass', data.get('overall_status') == 'PASS')
    rec('install_instructions_present', isinstance(data.get('install_instructions'), dict))
    fb = data.get('python_fallback_probe', {})
    rec('fb_requests_>=2000', fb.get('requests_total', 0) >= 2000)
    rec('fb_http_5xx_zero', fb.get('http_5xx', -1) == 0)
    rec('fb_borea_bad_zero', fb.get('borea_bad', -1) == 0)
    rec('fb_non_allowlist_bad_zero', fb.get('non_allowlist_bad', -1) == 0)
    sf = data.get('safety_flags', {})
    rec('sf_no_fresh_spend', sf.get('no_fresh_spend_attempted_in_fallback') is True)
    rec('sf_battle_off', sf.get('battle_runtime_attached') is False)
    rec('sf_buffs_off', sf.get('buffs_enabled') is False)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
