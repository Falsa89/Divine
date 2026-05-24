#!/usr/bin/env python3
"""PROJECT_P Track C validator — stage 5%."""
import json, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_p_prod_rollout_stage_5_percent_v1.json')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    allowed = ('TRACK_C_PROD_ROLLOUT_STAGE_5_PERCENT_GREEN', 'TRACK_C_PROD_ROLLOUT_STAGE_5_PERCENT_READY_NOT_APPLIED_PENDING_APPROVAL', 'TRACK_C_PROD_ROLLOUT_STAGE_5_PERCENT_BLOCKED_PRIOR_GATE_RED')
    if m.get('verdict') not in allowed: fail(f'verdict not in allowed set: {m.get("verdict")}')
    if not m.get('applied', False):
        if m.get('prod_flag_set') is not False: fail('prod_flag_set must be False')
        if m.get('backend_env_modified') is not False: fail('backend_env_modified must be False')
    print(f'[PASS] PROJECT_P Track C stage 5%: applied={m.get("applied")} verdict={m.get("verdict")}')
    sys.exit(0)


if __name__ == '__main__': main()
