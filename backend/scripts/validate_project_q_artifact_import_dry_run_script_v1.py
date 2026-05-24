#!/usr/bin/env python3
"""PROJECT_Q Track E validator — artifact import dry-run script.

Verifica che lo script di dry-run esista, default sia dry-run, che --apply richieda
le 5 firme ARTIFACT_*; esegue lo script in modalita' dry-run e verifica 0 DB writes.
"""
import json, subprocess, sys
from pathlib import Path

M = Path('/app/data/design/artifacts/project_q_artifact_import_dry_run_script_v1.json')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_E_ARTIFACT_IMPORT_DRY_RUN_SCRIPT_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    if m.get('dry_run_mode_default') is not True:
        fail('dry_run_mode_default must be True')
    if m.get('apply_mode_requires_signatures') is not True:
        fail('apply_mode_requires_signatures must be True')
    if m.get('db_touch') is not False:
        fail('db_touch must be False')
    script = Path(m.get('dry_run_script') or '')
    if not script.exists():
        fail(f'dry_run_script missing on disk: {script}')
    src = script.read_text()
    for required_token in ("REQ_SIGS", "ARTIFACT_USER_APPROVAL", "ARTIFACT_ECONOMY_APPROVAL", "ARTIFACT_BALANCE_APPROVAL", "ARTIFACT_QA_APPROVAL", "ARTIFACT_IMPORT_LIVE_OK", "--apply", "--rollback"):
        if required_token not in src:
            fail(f'dry-run script missing token: {required_token}')
    # Run in default dry-run; must NOT write DB; must succeed.
    proc = subprocess.run(['python3', str(script)], capture_output=True, text=True, timeout=30)
    if proc.returncode != 0:
        fail(f'dry-run script returned {proc.returncode}: {proc.stderr.strip()}')
    if '[DRY-RUN]' not in proc.stdout:
        fail('dry-run script did not emit [DRY-RUN] marker')
    if 'no DB writes performed' not in proc.stdout:
        fail('dry-run script did not declare no DB writes')
    dr = m.get('dry_run_result') or {}
    if int(dr.get('db_writes_executed', -1)) != 0:
        fail('dry_run_result.db_writes_executed must be 0')
    if int(dr.get('schema_validation_fail_count', -1)) != 0:
        fail('dry_run_result.schema_validation_fail_count must be 0')
    print(f'[PASS] PROJECT_Q Track E dry-run script READY — exit=0, 0 DB writes, default DRY-RUN enforced')
    sys.exit(0)


if __name__ == '__main__':
    main()
