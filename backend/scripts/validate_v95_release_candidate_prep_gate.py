#!/usr/bin/env python3
"""v95 — Validator: Release Candidate Prep Gate."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'release_candidate', 'v95_release_candidate_prep_gate_v1.json')
if not os.path.isfile(p):
    print('FAIL — file missing:', p); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
gates = d.get('gates') or {}
required = ['battle_engine','reward_safety','live_guild','formation','readonly_endpoints',
            'mode_playability','live_announcements','mobile_qa','performance','known_issues','store_readiness']
for k in required:
    if k not in gates:
        print(f'FAIL — gate missing: {k}'); sys.exit(1)
    if gates[k] not in ('READY', 'CONDITIONAL', 'BLOCKED'):
        print(f'FAIL — gate {k} invalid: {gates[k]}'); sys.exit(1)
if gates.get('battle_engine') != 'READY':
    print(f'FAIL — battle_engine must be READY in v95: {gates.get("battle_engine")}'); sys.exit(1)
if gates.get('readonly_endpoints') != 'READY':
    print('FAIL — readonly_endpoints must be READY'); sys.exit(1)
print(f"PASS — v95 release candidate prep gate (battle_engine={gates['battle_engine']}, endpoints={gates['readonly_endpoints']}, formation={gates['formation']})")
sys.exit(0)
