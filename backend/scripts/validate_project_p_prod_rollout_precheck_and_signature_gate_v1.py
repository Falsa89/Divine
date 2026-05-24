#!/usr/bin/env python3
"""PROJECT_P Track A validator — prod precheck + signature gate."""
import json, os, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_p_prod_rollout_precheck_and_signature_gate_v1.json')
REQUIRED_PROD_SIGS = ('PROD_ROLLOUT_USER_APPROVAL', 'PROD_ROLLOUT_QA_APPROVAL', 'PROD_ROLLOUT_OPS_APPROVAL', 'PROD_ROLLOUT_ROLLBACK_OWNER_APPROVAL', 'PROD_ROLLOUT_BALANCE_APPROVAL', 'STATUS_RUNTIME_BUFF_SLICE_PROD_OK')
ENV = Path('/app/backend/.env')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    allowed_verdicts = (
        'TRACK_A_PROD_ROLLOUT_PRECHECK_AND_SIGNATURE_GATE_READY_ALL_SIGNATURES_PRESENT',
        'TRACK_A_PROD_ROLLOUT_PRECHECK_AND_SIGNATURE_GATE_BLOCKING_MISSING_ALL_PROD_SIGNATURES',
        'TRACK_A_PROD_ROLLOUT_PRECHECK_AND_SIGNATURE_GATE_BLOCKING_PARTIAL_PROD_SIGNATURES',
    )
    if m.get('verdict') not in allowed_verdicts: fail(f'verdict not in allowed set: {m.get("verdict")}')
    # Independent verification: scan env + backend/.env + os.environ for the 6 prod signatures.
    env_txt = ENV.read_text() if ENV.exists() else ''
    actual_present = 0; missing = []
    for sig in REQUIRED_PROD_SIGS:
        line_true = any(ln.strip().startswith(sig + '=') and ln.split('=', 1)[1].strip().lower() == 'true' for ln in env_txt.splitlines())
        os_true = os.environ.get(sig, '').strip().lower() == 'true'
        if line_true or os_true: actual_present += 1
        else: missing.append(sig)
    declared_present = m.get('signatures_present_count', 0)
    if declared_present != actual_present: fail(f'declared signatures_present_count={declared_present} != actual {actual_present}')
    if actual_present < 6:
        if m.get('rollout_authorized') is not False: fail('rollout_authorized must be False when signatures missing')
        if m.get('backend_env_modified') is not False: fail('backend_env_modified must be False')
        if m.get('prod_runtime_touched') is not False: fail('prod_runtime_touched must be False')
    print(f'[PASS] PROJECT_P Track A precheck: {actual_present}/6 prod signatures detected; verdict={m.get("verdict")}')
    sys.exit(0)


if __name__ == '__main__': main()
