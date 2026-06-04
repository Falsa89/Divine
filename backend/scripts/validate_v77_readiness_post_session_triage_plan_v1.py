#!/usr/bin/env python3
"""validate_v77_readiness_post_session_triage_plan_v1"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path('/app')
PREFIX = 'PROJECT-v77-READINESS-POST-SESSION-TRIAGE-PLAN'
TAG = 'PUBLIC_SYNC_TAG_v76_MEGA_RELEASE_ACCELERATION_25_MANUAL_KICKOFF_FEEDBACK_STORE_BETA_READINESS'
P = 'data/design/release_acceleration/v77_readiness_post_session_triage_plan_v1.json'
M = 'data/design/release_acceleration/v77_readiness_post_session_triage_plan_marker_v1.json'
REQUIRED_LANES = {'closed_alpha_actual_feedback_intake_aggregation','closed_alpha_findings_triage_post_session','closed_alpha_wrap_summary'}

def fail(msg): print(f'{PREFIX}: FAIL {msg}'); sys.exit(1)

def main():
    for r in (P, M):
        if not (ROOT / r).exists(): fail(f'missing {r}')
    p = json.loads((ROOT / P).read_text()); m = json.loads((ROOT / M).read_text())
    if p.get('public_sync_tag') != TAG: fail('tag mismatch')
    lanes = set(p.get('v77_lanes_planned', []))
    if not REQUIRED_LANES.issubset(lanes): fail(f'lanes missing: {REQUIRED_LANES - lanes}')
    if p.get('manual_step_pending') is not True: fail('manual_step_pending must be true')
    if p.get('db_writes') != 0: fail('db_writes must be 0')
    if p.get('automated_live_invites') is not False: fail('automated_live_invites must be false')
    if p.get('store_upload_in_v77') is not False: fail('store_upload_in_v77 must be false')
    if p.get('broad_commercial_release') is not False: fail('broad_commercial_release must be false')
    if m.get('manual_step_pending') is not True: fail('marker.manual_step_pending must be true')
    print(f'{PREFIX}: PASS')

if __name__ == '__main__': main()
