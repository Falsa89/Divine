#!/usr/bin/env python3
"""PROJECT_Q Track F validator — import approval gate + rollback design.

Verifica indipendentemente lo stato delle 5 firme ARTIFACT_*:
- scansiona /app/backend/.env e os.environ
- riporta onestamente count present/missing
- assicura: live_import_authorized == false quando signatures_present < 5
- assicura: live_import_executed == false, db_writes == false
- planned_rollback presente.
"""
import json, os, sys
from pathlib import Path

M = Path('/app/data/design/artifacts/project_q_artifact_import_approval_gate_rollback_v1.json')
ENV = Path('/app/backend/.env')
REQ_SIGS = ('ARTIFACT_USER_APPROVAL', 'ARTIFACT_ECONOMY_APPROVAL', 'ARTIFACT_BALANCE_APPROVAL', 'ARTIFACT_QA_APPROVAL', 'ARTIFACT_IMPORT_LIVE_OK')
ALLOWED_VERDICTS = (
    'TRACK_F_ARTIFACT_IMPORT_APPROVAL_GATE_AND_ROLLBACK_READY_PENDING_APPROVAL',
    'TRACK_F_ARTIFACT_IMPORT_APPROVAL_GATE_AND_ROLLBACK_READY_ALL_SIGNATURES_PRESENT',
    'TRACK_F_ARTIFACT_IMPORT_APPROVAL_GATE_AND_ROLLBACK_BLOCKING_PARTIAL_SIGNATURES',
)


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') not in ALLOWED_VERDICTS:
        fail(f'verdict not allowed: {m.get("verdict")}')
    env_txt = ENV.read_text() if ENV.exists() else ''
    actual_present = 0
    missing = []
    for sig in REQ_SIGS:
        line_true = any(
            ln.strip().startswith(sig + '=') and ln.split('=', 1)[1].strip().lower() == 'true'
            for ln in env_txt.splitlines()
        )
        os_true = os.environ.get(sig, '').strip().lower() == 'true'
        if line_true or os_true:
            actual_present += 1
        else:
            missing.append(sig)
    declared = int(m.get('signatures_present_count', -1))
    if declared != actual_present:
        fail(f'signatures_present_count declared {declared} != actual {actual_present}')
    declared_missing = int(m.get('signatures_missing_count', -1))
    if declared_missing != len(missing):
        fail(f'signatures_missing_count declared {declared_missing} != actual {len(missing)}')
    if actual_present < 5:
        if m.get('live_import_authorized') is not False:
            fail('live_import_authorized must be False when signatures missing')
        if m.get('live_import_executed') is not False:
            fail('live_import_executed must be False')
        if m.get('db_writes') is not False:
            fail('db_writes must be False when signatures missing')
    rb = m.get('planned_rollback') or {}
    if not rb.get('strategy') or not rb.get('safety_guards'):
        fail('planned_rollback strategy/safety_guards missing')
    print(f'[PASS] PROJECT_Q Track F approval gate READY — {actual_present}/5 ARTIFACT_* signatures detected; live_import_authorized={m.get("live_import_authorized")}; db_writes={m.get("db_writes")}')
    sys.exit(0)


if __name__ == '__main__':
    main()
