#!/usr/bin/env python3
"""v96 — Validator: Release Candidate Final Gate."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'release_candidate', 'v96_release_candidate_final_gate_v1.json')
if not os.path.isfile(p):
    print('FAIL — file missing:', p); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
gates = d.get('gates') or {}
required = ('auth_account', 'engine', 'formation', 'modes', 'rewards', 'live_guild', 'announcements', 'mobile_qa', 'performance', 'optional_fail_baseline', 'store_readiness', 'art_audio_readiness', 'compliance_privacy', 'known_issues')
for k in required:
    if k not in gates:
        print(f'FAIL — gate missing: {k}'); sys.exit(1)
    for tier in ('internal_alpha', 'closed_alpha', 'commercial_release'):
        if tier not in gates[k]:
            print(f'FAIL — gate {k} missing tier {tier}'); sys.exit(1)
ov = d.get('overall_verdict') or {}
if not ov.get('READY_FOR_INTERNAL_ALPHA', False):
    print('FAIL — not READY_FOR_INTERNAL_ALPHA'); sys.exit(1)
if ov.get('BLOCKED_FOR_RELEASE_CANDIDATE', True):
    print('FAIL — BLOCKED_FOR_RELEASE_CANDIDATE not false'); sys.exit(1)
safety = d.get('safety') or {}
for k in ('reward_live', 'ranking_live', 'production_broadcast', 'push_notification_live', 'monetization_active'):
    if safety.get(k, True):
        print(f'FAIL — safety.{k} not false'); sys.exit(1)
print('PASS — v96 release candidate final gate (READY_FOR_INTERNAL_ALPHA)')
sys.exit(0)
