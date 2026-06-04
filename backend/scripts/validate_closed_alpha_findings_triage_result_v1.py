#!/usr/bin/env python3
"""validate_closed_alpha_findings_triage_result_v1"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path('/app')
PREFIX = 'PROJECT-CLOSED-ALPHA-FINDINGS-TRIAGE-RESULT'
TAG = 'PUBLIC_SYNC_TAG_v77_MEGA_RELEASE_ACCELERATION_26_FEEDBACK_AGGREGATION_TRIAGE_WRAP_v78_READINESS'
P = 'data/design/qa/closed_alpha_findings_triage_result_v1.json'
M = 'data/design/qa/closed_alpha_findings_triage_result_marker_v1.json'

def fail(msg): print(f'{PREFIX}: FAIL {msg}'); sys.exit(1)

def main():
    for r in (P, M):
        if not (ROOT / r).exists(): fail(f'missing {r}')
    t = json.loads((ROOT / P).read_text()); m = json.loads((ROOT / M).read_text())
    if t.get('public_sync_tag') != TAG: fail('tag mismatch')
    if t.get('input_feedback_count') != 0: fail('input_feedback_count must be 0')
    if t.get('input_bug_reports_count') != 0: fail('input_bug_reports_count must be 0')
    if t.get('open_findings_count') != 0: fail('open_findings_count must be 0')
    b = t.get('buckets', {})
    for k in ('P0','P1','P2','P3'):
        if b.get(k, {}).get('count') != 0: fail(f'bucket.{k}.count must be 0')
        if b.get(k, {}).get('items') != []: fail(f'bucket.{k}.items must be empty')
    if t.get('halt_triggered') is not False: fail('halt_triggered must be false')
    if t.get('rollback_required') is not False: fail('rollback_required must be false')
    if t.get('actions_planned') != []: fail('actions_planned must be empty')
    if t.get('invented_data') is not False: fail('invented_data must be false')
    if t.get('db_writes') != 0: fail('db_writes must be 0')
    if t.get('verdict') != 'TRIAGE_EMPTY_AWAITING_MANUAL_FEEDBACK_SAFE': fail('verdict mismatch')
    if m.get('open_findings_count') != 0: fail('marker open_findings_count must be 0')
    print(f'{PREFIX}: PASS')

if __name__ == '__main__': main()
