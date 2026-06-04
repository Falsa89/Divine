#!/usr/bin/env python3
"""validate_closed_alpha_wrap_summary_v1"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path('/app')
PREFIX = 'PROJECT-CLOSED-ALPHA-WRAP-SUMMARY'
TAG = 'PUBLIC_SYNC_TAG_v77_MEGA_RELEASE_ACCELERATION_26_FEEDBACK_AGGREGATION_TRIAGE_WRAP_v78_READINESS'
P = 'data/design/qa/closed_alpha_wrap_summary_v1.json'
M = 'data/design/qa/closed_alpha_wrap_summary_marker_v1.json'

def fail(msg): print(f'{PREFIX}: FAIL {msg}'); sys.exit(1)

def main():
    for r in (P, M):
        if not (ROOT / r).exists(): fail(f'missing {r}')
    w = json.loads((ROOT / P).read_text()); m = json.loads((ROOT / M).read_text())
    if w.get('public_sync_tag') != TAG: fail('tag mismatch')
    if w.get('closed_alpha_sessions_executed') != 0: fail('sessions must be 0')
    if w.get('closed_alpha_feedback_received') != 0: fail('feedback must be 0')
    if w.get('closed_alpha_bug_reports_received') != 0: fail('bugs must be 0')
    if w.get('closed_alpha_completion_state') != 'awaiting_manual_feedback': fail('completion_state mismatch')
    if w.get('go_no_go_decision') != 'DEFERRED_PENDING_FEEDBACK': fail('go_no_go_decision mismatch')
    if w.get('approved_to_proceed_to_beta') is not False: fail('approved_to_proceed_to_beta must be false')
    if w.get('approved_to_proceed_to_broader_alpha') is not False: fail('approved_to_proceed_to_broader_alpha must be false')
    if w.get('closed_alpha_rollback_required') is not False: fail('rollback_required must be false')
    if w.get('production_navigation_changed') is not False: fail('production_navigation_changed must be false')
    if w.get('invented_data') is not False: fail('invented_data must be false')
    if w.get('db_writes') != 0: fail('db_writes must be 0')
    if m.get('go_no_go_decision') != 'DEFERRED_PENDING_FEEDBACK': fail('marker.go_no_go_decision mismatch')
    print(f'{PREFIX}: PASS')

if __name__ == '__main__': main()
