#!/usr/bin/env python3
"""v103 — Auth context unification robust bridge validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','auth','v103_auth_context_unification_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
if d.get('unification_strategy') != 'BRIDGE_LOGOUT_ROBUST': print('FAIL \u2014 strategy not BRIDGE_LOGOUT_ROBUST'); sys.exit(1)
bridge = d.get('v103_bridge_implementation') or {}
if len(bridge.get('actions', [])) < 4: print('FAIL \u2014 bridge actions < 4'); sys.exit(1)
if d.get('full_unification_status') != 'BRIDGE_LOGOUT_ROBUST_FULL_DEFERRED': print('FAIL \u2014 full_unification_status wrong'); sys.exit(1)
if len(d.get('current_safety_guarantees', [])) < 3: print('FAIL \u2014 current_safety_guarantees < 3'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('token_raw_logs','provider_secrets','unexpected_token_loss','fake_PASS'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v103 auth context unification (strategy=BRIDGE_LOGOUT_ROBUST)")
sys.exit(0)
