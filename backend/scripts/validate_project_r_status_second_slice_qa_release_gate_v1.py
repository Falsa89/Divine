#!/usr/bin/env python3
"""PROJECT_R Track G validator — QA + release gate.

Verifica che QA requirements coprano fixture/regression deterministica/no-leak/mobile,
e che il release gate elenchi rollback_owner, balance/qa/ops/user signoff + 6 firme prod.
"""
import json, sys
from pathlib import Path

M = Path('/app/data/design/project_management/project_r_status_second_slice_qa_release_gate_v1.json')
REQUIRED_PROD_SIGS = {'PROD_ROLLOUT_USER_APPROVAL', 'PROD_ROLLOUT_QA_APPROVAL', 'PROD_ROLLOUT_OPS_APPROVAL', 'PROD_ROLLOUT_ROLLBACK_OWNER_APPROVAL', 'PROD_ROLLOUT_BALANCE_APPROVAL', 'STATUS_RUNTIME_SECOND_SLICE_PROD_OK'}


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_G_STATUS_SECOND_SLICE_QA_AND_RELEASE_GATE_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    if m.get('design_only') is not True or m.get('runtime_activated') is not False:
        fail('design_only/runtime_activated invariants violated')
    qa = m.get('qa_requirements') or {}
    for k in ('fixture_requirements', 'deterministic_regression', 'no_leak_checks', 'mobile_qa_needs'):
        if not qa.get(k):
            fail(f'qa_requirements.{k} missing')
    rg = m.get('release_gate') or {}
    for k in ('rollback_owner', 'balance_signoff', 'qa_signoff', 'ops_signoff', 'user_signoff'):
        if rg.get(k) != 'required':
            fail(f'release_gate.{k} must be "required"')
    declared_sigs = set(rg.get('prod_gate_signatures') or [])
    missing = REQUIRED_PROD_SIGS - declared_sigs
    if missing:
        fail(f'release_gate.prod_gate_signatures missing: {sorted(missing)}')
    if m.get('live_rollout_executed') is not False or m.get('db_writes') is not False:
        fail('live_rollout_executed/db_writes must be False')
    print('[PASS] PROJECT_R Track G QA + release gate READY — 4 QA categories covered, 6 prod signatures listed, no live rollout')
    sys.exit(0)


if __name__ == '__main__':
    main()
