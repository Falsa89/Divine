#!/usr/bin/env python3
"""V26 PART C — Validator for cap raise plan."""
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_cap_raise_plan_v1.json')


def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if d.get('status') != 'PLAN_ONLY': print('FAIL: must_be_plan_only'); return 2
    if d.get('live_cap_change_in_v26') is True: print('FAIL: live_change_forbidden'); return 2
    if d.get('broad_rollout_authorized') is True: print('FAIL: broad_rollout_must_false'); return 2
    stages = d.get('stages', [])
    if len(stages) < 4: print('FAIL: insufficient_stages'); return 2
    target = d.get('target_cap', 0)
    if target < 100000: print('FAIL: target_cap_too_low'); return 2
    print(f'PASS: AF2-N-V26-CAP-RAISE-PLAN (stages={len(stages)} target_cap={target})'); return 0


if __name__ == '__main__':
    sys.exit(main())
