#!/usr/bin/env python3
"""Validator for V17 rollback readiness."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

RESULT = Path('/app/data/design/affinity/af2n_v17_rollback_readiness_result_v1.json')


def main():
    if not RESULT.exists():
        runner = Path('/app/backend/scripts/run_af2n_v17_rollback_readiness.py')
        if runner.exists():
            subprocess.run(['python3', str(runner)], timeout=60)
    failures = []
    def rec(n, c):
        print(f'  [{"OK" if c else "X"}] {n}')
        if not c: failures.append(n)
    print('='*70); print('V17 ROLLBACK READINESS — Validator'); print('='*70)
    if not RESULT.exists():
        rec('result_present', False); print('Overall: FAIL'); return 1
    data = json.loads(RESULT.read_text())
    rec('overall_pass', data.get('overall_status') == 'PASS')
    rec('all_scripts_present', data.get('all_scripts_present') is True)
    rec('backup_dir_writable', data.get('supervisor_backup_dir_writable') is True)
    for s in data.get('scripts', []):
        rec(f'script_present:{Path(s.get("path","?")).name}', s.get('present') is True)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
