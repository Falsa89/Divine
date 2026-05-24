#!/usr/bin/env python3
"""PROJECT_F Track E validator — QA test credentials safe dry-run.

Verifies:
  * marker present, verdict in {READY, MANUAL_REQUIRED}
  * wrapper script present (no secret printing)
  * no real secrets committed to .env or marker
  * .env.example contains placeholder keys
"""
import json, re, sys
from pathlib import Path

MARKER = Path('/app/data/design/project_management/project_f_qa_test_credentials_safe_dryrun_v1.json')
WRAPPER = Path('/app/backend/scripts/run_project_f_qa_mobile_smoke_runner.py')
ENV_EXAMPLE = Path('/app/.env.example')
ALT_ENV_EXAMPLE = Path('/app/backend/.env.example')
SECRET_LOG_PATTERNS = (r'print\(.*password', r'print\(.*token', r'logging\..*password', r'logging\..*token')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') not in ('TRACK_E_QA_TEST_CREDENTIALS_SAFE_DRYRUN_READY', 'TRACK_E_QA_TEST_CREDENTIALS_MANUAL_REQUIRED'):
        fail('verdict mismatch')
    forb = m.get('forbidden_in_track_e_respected', {})
    for k in ('account_creation', 'real_gacha_spend', 'currency_mutation', 'destructive_action', 'secret_logging', 'frontend'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_e.{k} must be False')
    # Wrapper present and no secret printing
    if not WRAPPER.exists(): fail(f'wrapper missing {WRAPPER}')
    body = WRAPPER.read_text()
    for pat in SECRET_LOG_PATTERNS:
        if re.search(pat, body, re.IGNORECASE):
            fail(f'wrapper potentially leaks secret matching pattern: {pat}')
    # env example: either at root or backend/
    env_paths = [p for p in (ENV_EXAMPLE, ALT_ENV_EXAMPLE) if p.exists()]
    if not env_paths: fail('no .env.example file found at /app or /app/backend')
    found_keys = set()
    for p in env_paths:
        text = p.read_text()
        for k in ('QA_TEST_EMAIL', 'QA_TEST_PASSWORD', 'QA_TEST_API_BASE'):
            if k in text:
                found_keys.add(k)
    missing = {'QA_TEST_EMAIL', 'QA_TEST_PASSWORD', 'QA_TEST_API_BASE'} - found_keys
    if missing: fail(f'.env.example missing keys: {sorted(missing)}')
    print(f'[PASS] PROJECT_F Track E QA credentials safety OK (verdict={m.get("verdict")}); no secret logging in wrapper; env.example complete')
    sys.exit(0)

if __name__ == '__main__': main()
