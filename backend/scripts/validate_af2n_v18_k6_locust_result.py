#!/usr/bin/env python3
"""Validator for AF2-L-K6/LOCUST V18."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

RESULT = Path('/app/data/design/affinity/af2n_v18_k6_locust_result_v1.json')


def main():
    if not RESULT.exists():
        r = Path('/app/backend/scripts/run_af2n_v18_k6_locust.py')
        if r.exists(): subprocess.run(['python3', str(r)], timeout=420)
    failures = []
    def rec(n,c):
        print(f'  [{"OK" if c else "X"}] {n}')
        if not c: failures.append(n)
    print('='*70); print('AF2-L-K6/LOCUST V18 — Validator'); print('='*70)
    if not RESULT.exists(): rec('result_present', False); print('Overall: FAIL'); return 1
    d = json.loads(RESULT.read_text())
    rec('overall_pass', d.get('overall_status') == 'PASS')
    fb = d.get('python_fallback_probe', {})
    rec('fb_requests_>=3500', fb.get('requests_total', 0) >= 3500)
    rec('fb_http_5xx_zero', fb.get('http_5xx', -1) == 0)
    rec('fb_borea_bad_zero', fb.get('borea_bad', -1) == 0)
    rec('fb_non_allow_bad_zero', fb.get('non_allowlist_bad', -1) == 0)
    sf = d.get('safety_flags', {})
    rec('no_fresh_spend', sf.get('no_fresh_spend_attempted') is True)
    rec('broad_off', sf.get('broad_rollout_authorized') is False)
    rec('public_spend_off', sf.get('public_spend_ui') is False)
    rec('battle_off', sf.get('battle_runtime_attached') is False)
    rec('buffs_off', sf.get('buffs_enabled') is False)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
