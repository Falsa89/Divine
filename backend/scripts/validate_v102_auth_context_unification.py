#!/usr/bin/env python3
"""v102 — AuthContext unification (bridge) validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','auth','v102_auth_context_unification_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
if 'legacy_context' not in d or 'v96_context' not in d: print('FAIL \u2014 contexts missing'); sys.exit(1)
if d.get('unification_strategy') not in ('BRIDGE_LOGOUT','FULL_UNIFICATION'): print('FAIL \u2014 invalid unification_strategy'); sys.exit(1)
bridge = d.get('v102_bridge_implementation') or {}
if not bridge.get('file'): print('FAIL \u2014 bridge.file missing'); sys.exit(1)
if d.get('full_unification_status') not in ('AUTH_CONTEXT_FULL_UNIFICATION_DEFERRED','FULL_UNIFIED'): print('FAIL \u2014 invalid full_unification_status'); sys.exit(1)
guarantees = d.get('current_safety_guarantees') or []
if len(guarantees) < 3: print('FAIL \u2014 current_safety_guarantees < 3'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('token_raw_logs','provider_secrets','unexpected_token_loss','fake_PASS'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v102 auth context unification (strategy={d['unification_strategy']}, status={d['full_unification_status']})")
sys.exit(0)
