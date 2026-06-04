#!/usr/bin/env python3
"""validate_closed_alpha_feedback_aggregation_result_v1"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path('/app')
PREFIX = 'PROJECT-CLOSED-ALPHA-FEEDBACK-AGGREGATION-RESULT'
TAG = 'PUBLIC_SYNC_TAG_v77_MEGA_RELEASE_ACCELERATION_26_FEEDBACK_AGGREGATION_TRIAGE_WRAP_v78_READINESS'
P = 'data/design/qa/closed_alpha_feedback_aggregation_result_v1.json'
M = 'data/design/qa/closed_alpha_feedback_aggregation_result_marker_v1.json'
FLOWS = {'alpha_preview_hub','first_session_onboarding','training_combat_onboarding','story_alpha_slice','boss_tower_alpha_loop','event_arena_alpha_gate','event_arena_first_alpha_slice'}

def fail(msg): print(f'{PREFIX}: FAIL {msg}'); sys.exit(1)

def main():
    for r in (P, M):
        if not (ROOT / r).exists(): fail(f'missing {r}')
    a = json.loads((ROOT / P).read_text()); m = json.loads((ROOT / M).read_text())
    if a.get('public_sync_tag') != TAG: fail('tag mismatch')
    if a.get('actual_feedback_received') is not False: fail('actual_feedback_received must be false')
    if a.get('input_sessions') != 0: fail('input_sessions must be 0')
    if a.get('input_feedback_submissions') != 0: fail('input_feedback_submissions must be 0')
    if a.get('input_bug_reports') != 0: fail('input_bug_reports must be 0')
    if a.get('aggregation_state') != 'empty_pipeline_ready': fail('aggregation_state mismatch')
    for k, v in a.get('aggregated_metrics', {}).items():
        if v is not None: fail(f'metric {k} must be null')
    flows = a.get('per_flow_breakdown', {})
    if set(flows.keys()) != FLOWS: fail(f'flows mismatch')
    for fid, d in flows.items():
        if d.get('submissions') != 0 or d.get('completions') != 0 or d.get('crashes') != 0:
            fail(f'flow {fid} counts must be 0')
    if a.get('pii_in_repo') is not False: fail('pii_in_repo must be false')
    if a.get('alias_only') is not True: fail('alias_only must be true')
    if a.get('invented_data') is not False: fail('invented_data must be false')
    if a.get('db_writes') != 0: fail('db_writes must be 0')
    if a.get('verdict') != 'AGGREGATION_EMPTY_AWAITING_MANUAL_FEEDBACK_SAFE': fail('verdict mismatch')
    if m.get('input_feedback_submissions') != 0: fail('marker input_feedback_submissions must be 0')
    print(f'{PREFIX}: PASS')

if __name__ == '__main__': main()
