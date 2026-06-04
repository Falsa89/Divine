#!/usr/bin/env python3
"""validate_closed_alpha_post_session_triage_dry_run_v1"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path('/app')
PREFIX = 'PROJECT-CLOSED-ALPHA-POST-SESSION-TRIAGE-DRY-RUN'
TAG = 'PUBLIC_SYNC_TAG_v76_MEGA_RELEASE_ACCELERATION_25_MANUAL_KICKOFF_FEEDBACK_STORE_BETA_READINESS'
P = 'data/design/qa/closed_alpha_post_session_triage_dry_run_v1.json'
M = 'data/design/qa/closed_alpha_post_session_triage_dry_run_marker_v1.json'

def fail(msg): print(f'{PREFIX}: FAIL {msg}'); sys.exit(1)

def main():
    for r in (P, M):
        if not (ROOT / r).exists(): fail(f'missing {r}')
    p = json.loads((ROOT / P).read_text()); m = json.loads((ROOT / M).read_text())
    if p.get('public_sync_tag') != TAG: fail('tag mismatch')
    if p.get('dry_run') is not True: fail('dry_run must be true')
    if p.get('applied') is not False: fail('applied must be false')
    if p.get('input_sessions') != 0: fail('input_sessions must be 0')
    if p.get('input_feedback_submissions') != 0: fail('input_feedback_submissions must be 0')
    if p.get('input_bug_reports') != 0: fail('input_bug_reports must be 0')
    b = p.get('buckets', {})
    for k in ('P0','P1','P2','P3'):
        if b.get(k) != 0: fail(f'bucket.{k} must be 0')
    if p.get('halt_triggered') is not False: fail('halt_triggered must be false')
    if p.get('rollback_required') is not False: fail('rollback_required must be false')
    if p.get('verdict') != 'DRY_RUN_EMPTY_PIPELINE_READY_FOR_REAL_FEEDBACK': fail('verdict mismatch')
    if p.get('db_writes') != 0: fail('db_writes must be 0')
    if p.get('production_navigation_changed') is not False: fail('production_navigation_changed must be false')
    if m.get('verdict') != 'DRY_RUN_EMPTY_PIPELINE_READY_FOR_REAL_FEEDBACK': fail('marker.verdict mismatch')
    print(f'{PREFIX}: PASS')

if __name__ == '__main__': main()
