#!/usr/bin/env python3
"""PROJECT_I Track D validator — QA live login canary.

Verifies:
  * marker present with verdict in {EXECUTED_SAFE, MANUAL_REQUIRED}
  * if env vars missing → verdict must be MANUAL_REQUIRED
  * wrapper still passes secret-logging audit
"""
import json, os, re, sys
from pathlib import Path

MARKER = Path('/app/data/design/project_management/project_i_qa_live_login_canary_v1.json')
WRAPPER = Path('/app/backend/scripts/run_project_f_qa_mobile_smoke_runner.py')
SECRET_PATTERNS = (r'print\(.*password', r'print\(.*token', r'logging\..*password', r'logging\..*token')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') not in ('TRACK_D_QA_LIVE_LOGIN_CANARY_EXECUTED_SAFE', 'TRACK_D_QA_LIVE_LOGIN_CANARY_MANUAL_REQUIRED'):
        fail('verdict mismatch')
    # Honest gating: if env vars missing now, marker MUST be MANUAL_REQUIRED
    email_present = bool(os.environ.get('QA_TEST_EMAIL', '').strip())
    password_present = bool(os.environ.get('QA_TEST_PASSWORD', '').strip())
    live_ok = os.environ.get('QA_TEST_LIVE_LOGIN_OK', '').strip().lower() == 'true'
    if not (email_present and password_present and live_ok):
        if m.get('verdict') != 'TRACK_D_QA_LIVE_LOGIN_CANARY_MANUAL_REQUIRED':
            fail('env vars missing → verdict MUST be MANUAL_REQUIRED (honest gating)')
    forb = m.get('forbidden_in_track_d_respected', {})
    for k in ('account_creation', 'real_gacha_spend', 'currency_mutation', 'destructive_action', 'secret_logging', 'frontend'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_d.{k} must be False')
    if not WRAPPER.exists(): fail(f'wrapper missing {WRAPPER}')
    body = WRAPPER.read_text()
    for pat in SECRET_PATTERNS:
        if re.search(pat, body, re.IGNORECASE):
            fail(f'wrapper potentially leaks secret pattern: {pat}')
    print(f'[PASS] PROJECT_I Track D QA live login canary OK (verdict={m.get("verdict")}); no secret logging in wrapper')
    sys.exit(0)

if __name__ == '__main__': main()
