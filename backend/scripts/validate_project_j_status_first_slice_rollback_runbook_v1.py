#!/usr/bin/env python3
"""PROJECT_J REQUIRED-candidate 5 — rollback runbook documented."""
import json, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_j_status_rollback_kill_switch_plan_v1.json')
DOC = Path('/app/docs/divine/132F_STATUS_ROLLBACK_AND_KILL_SWITCH_PLAN.md')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    mm = json.loads(M.read_text())
    if len(mm.get('rollback_steps', [])) < 5: fail('rollback steps < 5')
    if mm.get('kill_switch_flag') != 'STATUS_RUNTIME_BUFF_SLICE_ENABLED': fail('kill_switch_flag mismatch')
    if not DOC.exists(): fail('rollback runbook doc missing')
    print('[PASS] rollback runbook documented'); sys.exit(0)
if __name__ == '__main__': main()
