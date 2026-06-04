#!/usr/bin/env python3
"""validate_closed_alpha_feedback_input_discovery_v1

Verifica che la discovery sia coerente con lo stato reale dei path locali
safe. Ricalcola live l'esistenza per evitare fake PASS.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path('/app')
PREFIX = 'PROJECT-CLOSED-ALPHA-FEEDBACK-INPUT-DISCOVERY'
TAG = 'PUBLIC_SYNC_TAG_v77_MEGA_RELEASE_ACCELERATION_26_FEEDBACK_AGGREGATION_TRIAGE_WRAP_v78_READINESS'
P = 'data/design/qa/closed_alpha_feedback_input_discovery_v1.json'
M = 'data/design/qa/closed_alpha_feedback_input_discovery_marker_v1.json'
SAFE_PATHS = [
    'data/design/qa/external_feedback/',
    'data/design/qa/manual_feedback_input/',
    'data/design/qa/closed_alpha_feedback_input_v1.json',
    'data/design/qa/closed_alpha_bug_reports_input_v1.json',
]

def fail(msg): print(f'{PREFIX}: FAIL {msg}'); sys.exit(1)

def main():
    for r in (P, M):
        if not (ROOT / r).exists(): fail(f'missing {r}')
    d = json.loads((ROOT / P).read_text()); m = json.loads((ROOT / M).read_text())
    if d.get('public_sync_tag') != TAG: fail('tag mismatch')
    if d.get('discovery_method') != 'local_safe_path_only': fail('discovery_method mismatch')
    if d.get('network_fetch_performed') is not False: fail('network_fetch_performed must be false')
    if d.get('external_form_fetch_performed') is not False: fail('external_form_fetch_performed must be false')
    if d.get('invented_data') is not False: fail('invented_data must be false')
    if d.get('db_writes') != 0: fail('db_writes must be 0')
    # Re-check live
    live_exists = {p: (ROOT / p).exists() for p in SAFE_PATHS}
    actual_any = any(live_exists.values())
    paths = {p.get('path'): p for p in d.get('paths_checked', [])}
    if set(paths.keys()) != set(SAFE_PATHS): fail(f'paths_checked mismatch')
    for sp, expected_exists in live_exists.items():
        if paths[sp].get('exists') != expected_exists:
            fail(f'path {sp} exists={paths[sp].get("exists")} but live={expected_exists}')
    declared = d.get('actual_feedback_received')
    if declared != actual_any:
        fail(f'actual_feedback_received={declared} mismatches live={actual_any}')
    if not actual_any:
        if d.get('verdict') != 'AWAITING_MANUAL_FEEDBACK_SAFE':
            fail('verdict must be AWAITING_MANUAL_FEEDBACK_SAFE when no feedback')
        if d.get('input_sessions') != 0: fail('input_sessions must be 0')
        if d.get('input_feedback_submissions') != 0: fail('input_feedback_submissions must be 0')
        if d.get('input_bug_reports') != 0: fail('input_bug_reports must be 0')
    if m.get('actual_feedback_received') is not False and not actual_any: fail('marker actual_feedback_received mismatch')
    if m.get('invented_data') is not False: fail('marker invented_data must be false')
    print(f'{PREFIX}: PASS')

if __name__ == '__main__': main()
