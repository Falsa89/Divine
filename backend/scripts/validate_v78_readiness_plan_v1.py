#!/usr/bin/env python3
"""validate_v78_readiness_plan_v1"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path('/app')
PREFIX = 'PROJECT-v78-READINESS-PLAN'
TAG = 'PUBLIC_SYNC_TAG_v77_MEGA_RELEASE_ACCELERATION_26_FEEDBACK_AGGREGATION_TRIAGE_WRAP_v78_READINESS'
P = 'data/design/release_acceleration/v78_readiness_plan_v1.json'
M = 'data/design/release_acceleration/v78_readiness_plan_marker_v1.json'
REQUIRED_LANES = {'closed_alpha_manual_feedback_ingest_when_present','closed_alpha_findings_triage_apply_or_defer','closed_alpha_wrap_go_no_go_decision'}
REQUIRED_OPTIONS = {'PROCEED_TO_BROADER_ALPHA','PROCEED_TO_BETA_GATED','HOLD_AND_FIX_FINDINGS','ROLLBACK_CLOSED_ALPHA'}

def fail(msg): print(f'{PREFIX}: FAIL {msg}'); sys.exit(1)

def main():
    for r in (P, M):
        if not (ROOT / r).exists(): fail(f'missing {r}')
    p = json.loads((ROOT / P).read_text()); m = json.loads((ROOT / M).read_text())
    if p.get('public_sync_tag') != TAG: fail('tag mismatch')
    lanes = set(p.get('v78_lanes_planned', []))
    if not REQUIRED_LANES.issubset(lanes): fail(f'lanes missing: {REQUIRED_LANES - lanes}')
    opts = set(p.get('v78_decision_options', []))
    if not REQUIRED_OPTIONS.issubset(opts): fail(f'decision options missing: {REQUIRED_OPTIONS - opts}')
    if p.get('manual_step_pending') is not True: fail('manual_step_pending must be true')
    if p.get('db_writes') != 0: fail('db_writes must be 0')
    if p.get('automated_live_invites') is not False: fail('automated_live_invites must be false')
    if p.get('store_upload_in_v78') is not False: fail('store_upload_in_v78 must be false')
    if p.get('broad_commercial_release') is not False: fail('broad_commercial_release must be false')
    if m.get('manual_step_pending') is not True: fail('marker.manual_step_pending must be true')
    print(f'{PREFIX}: PASS')

if __name__ == '__main__': main()
