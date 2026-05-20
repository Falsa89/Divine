#!/usr/bin/env python3
"""V26 PART B — Validator for Managed Redis readiness."""
import json, sys
from pathlib import Path
PLAN = Path('/app/data/design/affinity/affinity_managed_redis_readiness_plan_v1.json')
PROBE = Path('/app/data/design/affinity/affinity_managed_redis_probe_result_v1.json')


def main():
    if not PLAN.exists(): print('FAIL: plan_missing'); return 2
    p = json.loads(PLAN.read_text())
    if p.get('verdict') != 'PASS': print('FAIL: plan_verdict'); return 2
    if p.get('status') != 'PLAN_ONLY': print('FAIL: plan_must_be_plan_only'); return 2
    if p.get('live_switch_in_v26') is True: print('FAIL: live_switch_forbidden'); return 2
    if p.get('broad_rollout_authorized') is True: print('FAIL: broad_rollout_must_false'); return 2
    if p.get('secrets_in_repo') is True: print('FAIL: secrets_in_repo'); return 2
    if len(p.get('options_evaluated', [])) < 4: print('FAIL: insufficient_options'); return 2
    if not PROBE.exists(): print('FAIL: probe_result_missing'); return 2
    pr = json.loads(PROBE.read_text())
    if pr.get('verdict') != 'PASS': print('FAIL: probe_verdict (expected PASS even if READY_NOT_APPLIED)'); return 2
    print(f"PASS: AF2-N-V26-MANAGED-REDIS-READINESS (probe_status={pr.get('status')})"); return 0


if __name__ == '__main__':
    sys.exit(main())
