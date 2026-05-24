#!/usr/bin/env python3
"""PROJECT_G Track E validator — QA safe login env contract.

Verifies:
  * marker present with verdict TRACK_E_QA_SAFE_LOGIN_ENV_CONTRACT_READY
  * required env vars list contains QA_TEST_EMAIL/QA_TEST_PASSWORD/QA_TEST_LIVE_LOGIN_OK
  * none of these env vars are populated as committed secrets in marker JSON
  * wrapper script present and contains no secret-print patterns
  * runbook doc present
  * runner default state is MANUAL_REQUIRED
"""
import json, re, sys
from pathlib import Path

MARKER = Path('/app/data/design/project_management/project_g_qa_safe_login_env_contract_v1.json')
WRAPPER = Path('/app/backend/scripts/run_project_f_qa_mobile_smoke_runner.py')
RUNBOOK = Path('/app/docs/divine/129E_QA_SAFE_LOGIN_ENV_CONTRACT.md')
SECRET_PATTERNS = (r'print\(.*password', r'print\(.*token', r'logging\..*password', r'logging\..*token')
REQUIRED_ENV_NAMES = {'QA_TEST_EMAIL', 'QA_TEST_PASSWORD', 'QA_TEST_LIVE_LOGIN_OK'}


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_E_QA_SAFE_LOGIN_ENV_CONTRACT_READY': fail('verdict mismatch')
    if m.get('runner_default_state') != 'MANUAL_REQUIRED': fail('runner_default_state must be MANUAL_REQUIRED')
    env_vars = m.get('required_env_vars', [])
    names = {v.get('name') for v in env_vars}
    if not REQUIRED_ENV_NAMES.issubset(names): fail(f'required_env_vars missing: {sorted(REQUIRED_ENV_NAMES - names)}')
    for v in env_vars:
        if v.get('committed') is not False: fail(f'env var {v.get("name")} committed must be False')
    forb = m.get('forbidden_in_track_e_respected', {})
    for k in ('account_creation', 'real_gacha_spend', 'currency_mutation', 'destructive_action', 'secret_logging', 'frontend'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_e.{k} must be False')
    if not WRAPPER.exists(): fail(f'wrapper missing {WRAPPER}')
    body = WRAPPER.read_text()
    for pat in SECRET_PATTERNS:
        if re.search(pat, body, re.IGNORECASE):
            fail(f'wrapper potentially leaks secret pattern: {pat}')
    if not RUNBOOK.exists(): fail(f'runbook missing {RUNBOOK}')
    print('[PASS] PROJECT_G Track E QA safe login env contract READY: 3+ env vars defined; no committed secrets; wrapper safe; runbook present')
    sys.exit(0)

if __name__ == '__main__': main()
