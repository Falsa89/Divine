#!/usr/bin/env python3
"""validate_v72_p3_polish_backlog_v1

Verifica 3 finding P3 deferred, apply_now=false, safe_to_fix_later=true.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-v72-P3-POLISH-BACKLOG'
TAG = 'PUBLIC_SYNC_TAG_v73_MEGA_RELEASE_ACCELERATION_22_MENU_EXPOSURE_CLOSED_ALPHA'

FILES = [
    'data/design/qa/v72_p3_polish_backlog_plan_v1.json',
    'data/design/qa/v72_p3_polish_deferred_decision_v1.json',
    'data/design/qa/v72_p3_polish_backlog_marker_v1.json',
]

EXPECTED_FINDING_IDS = {
    'p3_alpha_preview_hub_copy_shortening',
    'p3_first_session_state_label_line_height_margin',
    'p3_alpha_preview_hub_qa_priority_ordering',
}


def fail(msg: str) -> None:
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def main() -> None:
    for rel in FILES:
        p = ROOT / rel
        if not p.exists():
            fail(f'missing {rel}')
        try:
            json.loads(p.read_text())
        except Exception as e:
            fail(f'invalid JSON {rel}: {e}')

    plan = json.loads((ROOT / FILES[0]).read_text())
    dec = json.loads((ROOT / FILES[1]).read_text())
    mrk = json.loads((ROOT / FILES[2]).read_text())

    findings = plan.get('findings', [])
    if len(findings) != 3:
        fail('plan.findings must have exactly 3 entries')
    ids = {f.get('id') for f in findings}
    if ids != EXPECTED_FINDING_IDS:
        fail(f'plan.findings ids mismatch: got {ids}')
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

    if dec.get('decision') != 'defer':
        fail('decision.decision must be defer')
    if dec.get('apply_now') is not False:
        fail('decision.apply_now must be false')
    if dec.get('safe_to_fix_later') is not True:
        fail('decision.safe_to_fix_later must be true')

    if mrk.get('public_sync_tag') != TAG:
        fail('marker.public_sync_tag mismatch')
    if mrk.get('findings_count') != 3:
        fail('marker.findings_count must be 3')
    if mrk.get('apply_now') is not False:
        fail('marker.apply_now must be false')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
