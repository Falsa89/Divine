#!/usr/bin/env python3
"""PROJECT_P Track F validator — no-leak + load + rollback final."""
import json, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_p_prod_rollout_no_leak_load_and_rollback_final_v1.json')
ENV = Path('/app/backend/.env')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    allowed = ('TRACK_F_PROD_ROLLOUT_NO_LEAK_LOAD_AND_ROLLBACK_FINAL_GREEN', 'TRACK_F_PROD_ROLLOUT_NO_LEAK_LOAD_AND_ROLLBACK_FINAL_READY_NOT_APPLIED_PENDING_APPROVAL', 'TRACK_F_PROD_ROLLOUT_NO_LEAK_LOAD_AND_ROLLBACK_FINAL_BLOCKED_PRIOR_GATE_RED')
    if m.get('verdict') not in allowed: fail(f'verdict not in allowed set: {m.get("verdict")}')
    # If not applied: there must be a documented plan and the env must not have the prod flag active.
    if not m.get('applied', False):
        if 'planned_no_leak_audit' not in m: fail('planned_no_leak_audit missing in READY_NOT_APPLIED marker')
        if 'planned_rollback' not in m: fail('planned_rollback missing')
        txt = ENV.read_text() if ENV.exists() else ''
        if any(ln.strip().startswith('STATUS_RUNTIME_BUFF_SLICE_ENABLED=') and ln.split('=', 1)[1].strip().lower() == 'true' for ln in txt.splitlines()):
            fail('flag must NOT be active in env when stages not applied')
    print(f'[PASS] PROJECT_P Track F: applied={m.get("applied")} verdict={m.get("verdict")}')
    sys.exit(0)


if __name__ == '__main__': main()
