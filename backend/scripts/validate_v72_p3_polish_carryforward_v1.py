#!/usr/bin/env python3
"""validate_v72_p3_polish_carryforward_v1

Verifica carry-forward dei 3 finding P3 in v74.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-v72-P3-POLISH-CARRYFORWARD'
TAG = 'PUBLIC_SYNC_TAG_v74_MEGA_RELEASE_ACCELERATION_23_MENU_EXPOSURE_APPLY_CLOSED_ALPHA_KICKOFF'

PLAN = 'data/design/qa/v72_p3_polish_carryforward_v1.json'
MRK = 'data/design/qa/v72_p3_polish_carryforward_marker_v1.json'

EXPECTED_IDS = {
    'p3_alpha_preview_hub_copy_shortening',
    'p3_first_session_state_label_line_height_margin',
    'p3_alpha_preview_hub_qa_priority_ordering',
}


def fail(msg: str) -> None:
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def main() -> None:
    for rel in (PLAN, MRK):
        if not (ROOT / rel).exists():
            fail(f'missing {rel}')
    plan = json.loads((ROOT / PLAN).read_text())
    mrk = json.loads((ROOT / MRK).read_text())

    if plan.get('public_sync_tag') != TAG:
        fail('plan.public_sync_tag mismatch')
    if plan.get('findings_count') != 3:
        fail('plan.findings_count must be 3')
    findings = plan.get('findings', [])
    ids = {f.get('id') for f in findings}
    if ids != EXPECTED_IDS:
        fail(f'plan.findings ids mismatch: {ids}')
    for f in findings:
        if f.get('severity') != 'P3':
            fail(f'finding {f.get("id")} severity must be P3')
        if f.get('apply_now') is not False:
            fail(f'finding {f.get("id")} apply_now must be false')
        if f.get('safe_to_fix_later') is not True:
            fail(f'finding {f.get("id")} safe_to_fix_later must be true')

    if plan.get('apply_now_default') is not False:
        fail('plan.apply_now_default must be false')
    if plan.get('aggregate_into_future_polish_batch') is not True:
        fail('plan.aggregate_into_future_polish_batch must be true')
    if plan.get('is_blocker') is not False:
        fail('plan.is_blocker must be false')
    if plan.get('safe_to_fix_later') is not True:
        fail('plan.safe_to_fix_later must be true')
    if plan.get('db_writes') != 0:
        fail('plan.db_writes must be 0')

    if mrk.get('findings_count') != 3:
        fail('marker.findings_count must be 3')
    if mrk.get('apply_now') is not False:
        fail('marker.apply_now must be false')
    if mrk.get('safe_to_fix_later') is not True:
        fail('marker.safe_to_fix_later must be true')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
