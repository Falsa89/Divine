#!/usr/bin/env python3
"""validate_closed_alpha_feedback_intake_template_v1"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path('/app')
PREFIX = 'PROJECT-CLOSED-ALPHA-FEEDBACK-INTAKE-TEMPLATE'
TAG = 'PUBLIC_SYNC_TAG_v76_MEGA_RELEASE_ACCELERATION_25_MANUAL_KICKOFF_FEEDBACK_STORE_BETA_READINESS'
P = 'data/design/qa/closed_alpha_feedback_intake_template_v1.json'
M = 'data/design/qa/closed_alpha_feedback_intake_template_marker_v1.json'
REQUIRED = {'tester_alias','device','os_version','flow_tested','completion_status','clarity_1_5','interest_1_5','pace_1_5','copy_quality_1_5','would_recommend_1_5'}

def fail(msg): print(f'{PREFIX}: FAIL {msg}'); sys.exit(1)

def main():
    for r in (P, M):
        if not (ROOT / r).exists(): fail(f'missing {r}')
    p = json.loads((ROOT / P).read_text()); m = json.loads((ROOT / M).read_text())
    if p.get('public_sync_tag') != TAG: fail('tag mismatch')
    if p.get('intake_storage') != 'external_shared_doc': fail('intake_storage mismatch')
    if p.get('in_app_persistence') is not False: fail('in_app_persistence must be false')
    if p.get('db_writes') != 0: fail('db_writes must be 0')
    fields = {f.get('id') for f in p.get('fields', [])}
    if not REQUIRED.issubset(fields): fail(f'missing fields: {REQUIRED - fields}')
    pii = p.get('pii_policy', {})
    if pii.get('alias_only') is not True: fail('alias_only must be true')
    if m.get('in_app_persistence') is not False: fail('marker.in_app_persistence must be false')
    print(f'{PREFIX}: PASS')

if __name__ == '__main__': main()
