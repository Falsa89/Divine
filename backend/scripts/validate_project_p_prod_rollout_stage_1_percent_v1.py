#!/usr/bin/env python3
"""PROJECT_P Track B validator — stage 1%."""
import json, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_p_prod_rollout_stage_1_percent_v1.json')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    allowed = ('TRACK_B_PROD_ROLLOUT_STAGE_1_PERCENT_GREEN', 'TRACK_B_PROD_ROLLOUT_STAGE_1_PERCENT_READY_NOT_APPLIED_PENDING_APPROVAL', 'TRACK_B_PROD_ROLLOUT_STAGE_1_PERCENT_BLOCKED_PRIOR_GATE_RED')
    if m.get('verdict') not in allowed: fail(f'verdict not in allowed set: {m.get("verdict")}')
    if not m.get('applied', False):
        if m.get('prod_flag_set') is not False: fail('prod_flag_set must be False if not applied')
        if m.get('backend_env_modified') is not False: fail('backend_env_modified must be False if not applied')
        if m.get('prod_traffic_routed_to_flag_on_percent', -1) != 0.0: fail('traffic percent must be 0.0 if not applied')
        if m.get('db_write') is not False: fail('db_write must be False')
    print(f'[PASS] PROJECT_P Track B stage 1%: applied={m.get("applied")} verdict={m.get("verdict")}')
    sys.exit(0)


if __name__ == '__main__': main()
