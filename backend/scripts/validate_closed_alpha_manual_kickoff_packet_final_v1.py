#!/usr/bin/env python3
"""validate_closed_alpha_manual_kickoff_packet_final_v1"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path('/app')
PREFIX = 'PROJECT-CLOSED-ALPHA-MANUAL-KICKOFF-PACKET-FINAL'
TAG = 'PUBLIC_SYNC_TAG_v76_MEGA_RELEASE_ACCELERATION_25_MANUAL_KICKOFF_FEEDBACK_STORE_BETA_READINESS'
P = 'data/design/qa/closed_alpha_manual_kickoff_packet_final_v1.json'
M = 'data/design/qa/closed_alpha_manual_kickoff_packet_final_marker_v1.json'
REQUIRED_SECTIONS = {'welcome', 'how_to_access', 'target_flows', 'what_is_not_real', 'feedback_intake', 'halt_and_safety'}

def fail(msg): print(f'{PREFIX}: FAIL {msg}'); sys.exit(1)

def main():
    for r in (P, M):
        if not (ROOT / r).exists(): fail(f'missing {r}')
    p = json.loads((ROOT / P).read_text()); m = json.loads((ROOT / M).read_text())
    if p.get('public_sync_tag') != TAG: fail('tag mismatch')
    if p.get('delivery_mode') != 'manual_author_dm_only': fail('delivery_mode mismatch')
    for k in ('automated_send','email_send','dm_send','public_form_link_creation','pii_collected_in_repo'):
        if p.get(k) is not False: fail(f'{k} must be false')
    if p.get('db_writes') != 0: fail('db_writes must be 0')
    secs = {s.get('id') for s in p.get('packet_sections', [])}
    if not REQUIRED_SECTIONS.issubset(secs): fail(f'missing sections: {REQUIRED_SECTIONS - secs}')
    for ph in ('tester_alias','deeplink_url','feedback_form_link','bug_report_link','author_contact'):
        if ph not in p.get('placeholders', {}): fail(f'missing placeholder {ph}')
    if m.get('public_sync_tag') != TAG: fail('marker.tag mismatch')
    if m.get('automated_send') is not False: fail('marker.automated_send must be false')
    print(f'{PREFIX}: PASS')

if __name__ == '__main__': main()
