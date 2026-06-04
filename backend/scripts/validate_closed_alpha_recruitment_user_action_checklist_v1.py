#!/usr/bin/env python3
"""validate_closed_alpha_recruitment_user_action_checklist_v1"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path('/app')
PREFIX = 'PROJECT-CLOSED-ALPHA-RECRUITMENT-USER-ACTION-CHECKLIST'
TAG = 'PUBLIC_SYNC_TAG_v76_MEGA_RELEASE_ACCELERATION_25_MANUAL_KICKOFF_FEEDBACK_STORE_BETA_READINESS'
P = 'data/design/qa/closed_alpha_recruitment_user_action_checklist_v1.json'
M = 'data/design/qa/closed_alpha_recruitment_user_action_checklist_marker_v1.json'
FORBIDDEN = {'public_form_link','social_media_broadcast','automated_email_blast','in_app_invite_system','persistent_pii_in_repo','persistent_account_creation_in_app','automated_dm_send'}

def fail(msg): print(f'{PREFIX}: FAIL {msg}'); sys.exit(1)

def main():
    for r in (P, M):
        if not (ROOT / r).exists(): fail(f'missing {r}')
    p = json.loads((ROOT / P).read_text()); m = json.loads((ROOT / M).read_text())
    if p.get('public_sync_tag') != TAG: fail('tag mismatch')
    actions = p.get('author_actions_required', [])
    if len(actions) < 7: fail('actions must be >= 7')
    for a in actions:
        if a.get('automatable') is not False: fail(f'step {a.get("step")} must be non-automatable')
    fb = set(p.get('forbidden_during_kickoff', []))
    if not FORBIDDEN.issubset(fb): fail(f'forbidden missing: {FORBIDDEN - fb}')
    pii = p.get('pii_policy', {})
    if pii.get('alias_only') is not True: fail('alias_only must be true')
    if p.get('db_writes') != 0: fail('db_writes must be 0')
    if m.get('all_steps_non_automatable') is not True: fail('marker.all_steps_non_automatable must be true')
    print(f'{PREFIX}: PASS')

if __name__ == '__main__': main()
