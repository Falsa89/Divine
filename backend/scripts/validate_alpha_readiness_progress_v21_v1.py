#!/usr/bin/env python3
"""validate_alpha_readiness_progress_v21_v1"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path('/app')
PREFIX = 'PROJECT-ALPHA-READINESS-PROGRESS-v21'
TAG = 'PUBLIC_SYNC_TAG_v77_MEGA_RELEASE_ACCELERATION_26_FEEDBACK_AGGREGATION_TRIAGE_WRAP_v78_READINESS'
P = 'data/design/release_acceleration/alpha_readiness_progress_report_v21.json'
M = 'data/design/release_acceleration/alpha_readiness_progress_report_v21_marker_v1.json'
EXPECTED = {
    'closed_alpha_feedback_input_discovery': 'AWAITING_MANUAL_FEEDBACK_SAFE',
    'closed_alpha_feedback_aggregation': 'AGGREGATION_EMPTY_AWAITING_MANUAL_FEEDBACK_SAFE',
    'closed_alpha_findings_triage': 'TRIAGE_EMPTY_AWAITING_MANUAL_FEEDBACK_SAFE',
    'closed_alpha_wrap_summary': 'awaiting_manual_feedback',
    'closed_alpha_go_no_go_decision': 'DEFERRED_PENDING_FEEDBACK',
    'v78_readiness_plan': 'ready_v77',
    'actual_feedback_received': False,
    'input_sessions': 0,
    'open_findings_count': 0,
    'pii_collected_in_repo': False,
    'alias_only': True,
    'invented_data': False,
    'store_upload_performed': False,
    'production_navigation_changed': False,
    'db_writes': 0,
    'broad_commercial_release': False,
}

def fail(msg): print(f'{PREFIX}: FAIL {msg}'); sys.exit(1)

def main():
    for r in (P, M):
        if not (ROOT / r).exists(): fail(f'missing {r}')
    p = json.loads((ROOT / P).read_text()); m = json.loads((ROOT / M).read_text())
    if p.get('public_sync_tag') != TAG: fail('tag mismatch')
    for k, v in EXPECTED.items():
        if p.get(k) != v: fail(f'{k}={p.get(k)!r} expected {v!r}')
    if m.get('closed_alpha_go_no_go_decision') != 'DEFERRED_PENDING_FEEDBACK': fail('marker mismatch')
    print(f'{PREFIX}: PASS')

if __name__ == '__main__': main()
