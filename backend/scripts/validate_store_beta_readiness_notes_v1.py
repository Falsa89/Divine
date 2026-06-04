#!/usr/bin/env python3
"""validate_store_beta_readiness_notes_v1"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path('/app')
PREFIX = 'PROJECT-STORE-BETA-READINESS-NOTES'
TAG = 'PUBLIC_SYNC_TAG_v76_MEGA_RELEASE_ACCELERATION_25_MANUAL_KICKOFF_FEEDBACK_STORE_BETA_READINESS'
P = 'data/design/release_acceleration/store_beta_readiness_notes_v1.json'
M = 'data/design/release_acceleration/store_beta_readiness_notes_marker_v1.json'
FORBIDDEN = {'store_upload','play_console_changes','appstore_connect_changes','testflight_changes','build_generation','signing_key_handling','privacy_policy_publication'}

def fail(msg): print(f'{PREFIX}: FAIL {msg}'); sys.exit(1)

def main():
    for r in (P, M):
        if not (ROOT / r).exists(): fail(f'missing {r}')
    p = json.loads((ROOT / P).read_text()); m = json.loads((ROOT / M).read_text())
    if p.get('public_sync_tag') != TAG: fail('tag mismatch')
    if p.get('scope') != 'notes_and_checklist_only': fail('scope mismatch')
    for k in ('applied','store_upload_performed','play_console_changes_performed','appstore_connect_changes_performed','testflight_changes_performed','build_generation_performed'):
        if p.get(k) is not False: fail(f'{k} must be false')
    gp = p.get('google_play', {})
    if gp.get('action_in_v76') != 'no_action': fail('google_play.action_in_v76 must be no_action')
    if gp.get('required_min_tester_count_personal') != 12: fail('google_play min testers must be 12')
    if gp.get('required_min_days_personal') != 14: fail('google_play min days must be 14')
    tf = p.get('apple_testflight', {})
    if tf.get('action_in_v76') != 'no_action': fail('apple_testflight.action_in_v76 must be no_action')
    if tf.get('review_required_for_external') is not True: fail('testflight review_required_for_external must be true')
    fb = set(p.get('forbidden_in_v76', []))
    if not FORBIDDEN.issubset(fb): fail(f'forbidden missing: {FORBIDDEN - fb}')
    if p.get('db_writes') != 0: fail('db_writes must be 0')
    if p.get('broad_commercial_release') is not False: fail('broad_commercial_release must be false')
    if m.get('applied') is not False: fail('marker.applied must be false')
    if m.get('store_upload_performed') is not False: fail('marker.store_upload_performed must be false')
    print(f'{PREFIX}: PASS')

if __name__ == '__main__': main()
