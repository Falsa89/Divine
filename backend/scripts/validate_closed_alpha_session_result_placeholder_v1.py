#!/usr/bin/env python3
"""validate_closed_alpha_session_result_placeholder_v1"""
from __future__ import annotations
import json, re, sys
from pathlib import Path
ROOT = Path('/app')
PREFIX = 'PROJECT-CLOSED-ALPHA-SESSION-RESULT-PLACEHOLDER'
TAG = 'PUBLIC_SYNC_TAG_v76_MEGA_RELEASE_ACCELERATION_25_MANUAL_KICKOFF_FEEDBACK_STORE_BETA_READINESS'
P = 'data/design/qa/closed_alpha_session_result_placeholder_v1.json'
M = 'data/design/qa/closed_alpha_session_result_placeholder_marker_v1.json'
ALIAS_RE = re.compile(r'^alpha_tester_0[1-8]$')

def fail(msg): print(f'{PREFIX}: FAIL {msg}'); sys.exit(1)

def main():
    for r in (P, M):
        if not (ROOT / r).exists(): fail(f'missing {r}')
    p = json.loads((ROOT / P).read_text()); m = json.loads((ROOT / M).read_text())
    if p.get('public_sync_tag') != TAG: fail('tag mismatch')
    if p.get('slot_count') != 8: fail('slot_count must be 8')
    if p.get('alias_only') is not True: fail('alias_only must be true')
    if p.get('pii_in_repo') is not False: fail('pii_in_repo must be false')
    if p.get('db_writes') != 0: fail('db_writes must be 0')
    if p.get('in_app_persistence') is not False: fail('in_app_persistence must be false')
    if p.get('async_storage_persistence') is not False: fail('async_storage_persistence must be false')
    sessions = p.get('sessions', [])
    if len(sessions) != 8: fail('sessions must have 8 entries')
    for s in sessions:
        if not ALIAS_RE.match(s.get('tester_alias', '')): fail(f'invalid alias {s.get("tester_alias")}')
        if s.get('session_state') != 'not_started': fail('session_state must be not_started')
        if s.get('feedback_form_submitted') is not False: fail('feedback_form_submitted must be false')
        if s.get('bug_reports_count') != 0: fail('bug_reports_count must be 0')
    if m.get('alias_only') is not True: fail('marker.alias_only must be true')
    print(f'{PREFIX}: PASS')

if __name__ == '__main__': main()
