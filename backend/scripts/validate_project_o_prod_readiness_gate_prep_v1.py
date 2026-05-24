#!/usr/bin/env python3
"""PROJECT_O Track G validator — prod readiness gate prep."""
import json, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_o_prod_readiness_gate_prep_v1.json')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_G_PROD_READINESS_GATE_PREP_READY': fail('verdict mismatch')
    chk = m.get('required_green_checks_for_prod') or []
    if len(chk) < 6: fail(f'too few green checks: {len(chk)}')
    if not m.get('future_prod_rollout_approval_phrase'): fail('approval phrase missing')
    if m.get('prod_rollout_executed_in_pack_o') is not False: fail('prod rollout must NOT be executed')
    print(f'[PASS] PROJECT_O Track G prod readiness gate prep READY: {len(chk)} green-checks listed; no rollout')
    sys.exit(0)


if __name__ == '__main__': main()
