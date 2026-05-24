#!/usr/bin/env python3
"""PROJECT_N Track G validator — dev-live readiness gate."""
import json, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_n_status_first_slice_dev_live_readiness_gate_v1.json')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_G_STATUS_FIRST_SLICE_DEV_LIVE_READINESS_GATE_READY': fail('verdict mismatch')
    chk = m.get('required_green_checks_for_dev_live') or []
    if len(chk) < 5: fail(f'too few required green checks: {len(chk)}')
    if not m.get('future_dev_live_rollout_approval_phrase'): fail('approval phrase missing')
    if m.get('dev_live_rollout_executed_in_pack_n') is not False: fail('dev-live rollout must NOT be executed in this pack')
    if m.get('prod_rollout_executed_in_pack_n') is not False: fail('prod rollout must NOT be executed in this pack')
    print(f'[PASS] PROJECT_N Track G dev-live readiness gate READY: {len(chk)} green-checks listed; no rollout executed')
    sys.exit(0)


if __name__ == '__main__': main()
