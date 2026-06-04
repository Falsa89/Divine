#!/usr/bin/env python3
"""validate_closed_alpha_testing_plan_v1

Verifica closed alpha plan + onboarding template + feedback form + bug report workflow.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-CLOSED-ALPHA-TESTING-PLAN'
TAG = 'PUBLIC_SYNC_TAG_v73_MEGA_RELEASE_ACCELERATION_22_MENU_EXPOSURE_CLOSED_ALPHA'

FILES = [
    'data/design/qa/closed_alpha_testing_plan_v1.json',
    'data/design/qa/closed_alpha_tester_onboarding_template_v1.json',
    'data/design/qa/closed_alpha_feedback_form_template_v1.json',
    'data/design/qa/closed_alpha_bug_report_workflow_v1.json',
    'data/design/qa/closed_alpha_testing_plan_marker_v1.json',
]

REQUIRED_FLOWS = {
    'first_session_onboarding_preview',
    'training_preview',
    'story_alpha_slice',
    'boss_tower_alpha_loop',
    'event_arena_alpha_preview',
    'alpha_preview_hub',
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
    onb = json.loads((ROOT / FILES[1]).read_text())
    fb = json.loads((ROOT / FILES[2]).read_text())
    bug = json.loads((ROOT / FILES[3]).read_text())
    mrk = json.loads((ROOT / FILES[4]).read_text())

    if plan.get('closed_alpha_plan_only') is not True:
        fail('plan.closed_alpha_plan_only must be true')
    if plan.get('closed_alpha_invites_enabled') is not False:
        fail('plan.closed_alpha_invites_enabled must be false')
    if plan.get('live_invite_system') is not False:
        fail('plan.live_invite_system must be false')
    if plan.get('account_persistence_changes') is not False:
        fail('plan.account_persistence_changes must be false')
    if plan.get('backend_route_changes') is not False:
        fail('plan.backend_route_changes must be false')
    if plan.get('db_writes') != 0:
        fail('plan.db_writes must be 0')
    flows = {f.get('id') for f in plan.get('target_flows', [])}
    if not REQUIRED_FLOWS.issubset(flows):
        fail(f'plan target_flows missing: {REQUIRED_FLOWS - flows}')

    if onb.get('account_persistence') is not False:
        fail('onboarding.account_persistence must be false')
    if onb.get('db_writes') != 0:
        fail('onboarding.db_writes must be 0')
    if not onb.get('sections'):
        fail('onboarding.sections empty')

    if fb.get('db_writes') != 0:
        fail('feedback.db_writes must be 0')
    if fb.get('account_persistence') is not False:
        fail('feedback.account_persistence must be false')
    if not fb.get('fields'):
        fail('feedback.fields empty')

    if bug.get('db_writes') != 0:
        fail('bug.db_writes must be 0')
    if 'P0' not in bug.get('triage_buckets', []):
        fail('bug.triage_buckets must include P0')

    if mrk.get('public_sync_tag') != TAG:
        fail('marker.public_sync_tag mismatch')
    if mrk.get('closed_alpha_plan_only') is not True:
        fail('marker.closed_alpha_plan_only must be true')
    if mrk.get('closed_alpha_invites_enabled') is not False:
        fail('marker.closed_alpha_invites_enabled must be false')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
