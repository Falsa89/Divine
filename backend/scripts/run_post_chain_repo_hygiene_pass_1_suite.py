#!/usr/bin/env python3
"""POST_CHAIN_REPO_HYGIENE_PASS_1 — Hygiene Suite Runner (lightweight).

Runs the 6 hygiene validators. Does NOT re-run the 73-validator Pre-QA
chain suite; that suite is preserved as-is in
run_pack_127_128_129_130_131_132_133_safety_suite.py.
"""
from __future__ import annotations
import json, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / 'backend' / 'scripts'
REPORTS = REPO_ROOT / 'backend' / 'reports'
REPORTS.mkdir(parents=True, exist_ok=True)

HYGIENE = [
    'validate_post_chain_artifact_policy_doc.py',
    'validate_post_chain_future_pack_leak_guard.py',
    'validate_post_chain_no_runtime_scope_drift.py',
    'validate_post_chain_no_release_ready_claim.py',
    'validate_post_chain_no_secret_leak_in_reports.py',
    'validate_post_chain_marker_truth.py',
]


def run_one(script):
    path = SCRIPTS / script
    if not path.exists():
        return {'name': script, 'status': 'MISSING', 'rc': -1, 'duration_s': 0.0}
    t0 = time.time()
    r = subprocess.run(['python3', str(path)], capture_output=True, text=True, timeout=120)
    return {'name': script, 'status': 'PASS' if r.returncode == 0 else 'FAIL',
            'rc': r.returncode, 'duration_s': round(time.time() - t0, 3),
            'stdout_tail': '\n'.join(r.stdout.splitlines()[-5:]),
            'stderr_tail': '\n'.join(r.stderr.splitlines()[-3:]) if r.stderr else ''}


def main():
    print('POST_CHAIN_REPO_HYGIENE_PASS_1 — hygiene suite')
    print('=' * 64)
    results = []
    for s in HYGIENE:
        res = run_one(s)
        results.append(res)
        print(f'  {res["status"]:6s} rc={res["rc"]} {res["duration_s"]}s  {s}')
        if res['status'] == 'FAIL':
            print(f'    stdout: {res.get("stdout_tail", "")[:300]}')
            if res.get('stderr_tail'):
                print(f'    stderr: {res["stderr_tail"][:200]}')
    fails = [r for r in results if r['status'] == 'FAIL']
    print('=' * 64)
    print(f'TOTAL: {len(results)} | PASS: {len(results) - len(fails)} | FAIL: {len(fails)}')
    suite_status = 'PASS' if not fails else 'FAIL'
    suite_report = {'suite': 'POST_CHAIN_REPO_HYGIENE_PASS_1_SUITE',
                    'status': suite_status,
                    'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                    'results': results}
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    (REPORTS / f'post_chain_repo_hygiene_pass_1_suite_{ts}.json').write_text(
        json.dumps(suite_report, indent=2, ensure_ascii=False), encoding='utf-8')
    (REPORTS / 'post_chain_repo_hygiene_pass_1_suite_latest.json').write_text(
        json.dumps(suite_report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Suite status: {suite_status}')
    return 0 if suite_status == 'PASS' else 1


if __name__ == '__main__': sys.exit(main())
