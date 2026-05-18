#!/usr/bin/env python3
"""V21 — Validate Stage4 internal beta apply result."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/af2n_stage4_internal_beta_apply_result_v1.json')


def main():
    if not R.exists():
        print(f'FAIL: missing {R}'); return 2
    d = json.loads(R.read_text())
    fails = []
    status = d.get('overall_status')
    if status not in ('APPLIED', 'READY_NOT_APPLIED'):
        fails.append(f'bad_status:{status}')
    if d.get('broad_rollout_authorized') is not False:
        fails.append('broad_rollout_true')
    if d.get('public_spend_ui') is not False:
        fails.append('public_spend_ui_true')
    if d.get('battle_wiring') is not False:
        fails.append('battle_wiring_true')
    if status == 'APPLIED':
        if d.get('stage4_applied') is not True:
            fails.append('applied_but_flag_false')
        if d.get('target_cap', 0) > 10000:
            fails.append('cap_above_hard_max')
        if d.get('target_allowlist_size', 0) > 1500:
            fails.append('allowlist_above_hard_max')
        snap = d.get('post_apply_canary_status', {})
        if snap.get('canary_allowlist_size', 0) < 700:
            fails.append('post_apply_allowlist_too_small')
        if snap.get('canary_ledger_cap', 0) != d.get('target_cap'):
            fails.append('post_apply_cap_mismatch')
        # invariants
        if 'borea' in str(snap.get('last_canary_tx', {})).lower():
            fails.append('borea_in_last_tx')
    if fails:
        for f in fails: print(f'FAIL: {f}')
        return 2
    print(f'PASS: AF2-N-V21-STAGE4-APPLY ({status})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
