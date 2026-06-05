#!/usr/bin/env python3
"""v100 — Required invariant protection validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'closed_alpha', 'v100_required_invariant_protection_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
if d.get('required_total', 0) < 19: print('FAIL \u2014 required_total < 19'); sys.exit(1)
if d.get('required_fail_post_v100', 1) != 0: print('FAIL \u2014 required_fail_post_v100 != 0'); sys.exit(1)
if d.get('required_weakened', 1) != 0: print('FAIL \u2014 required_weakened != 0'); sys.exit(1)
for k in ('v95_engine_regression_check','v96_auth_session_check','v97_refresh_bot_policy_check','v98_bot_runtime_gates_check','v99_blocker_honesty_check'):
    if d.get(k) != 'PASS': print(f'FAIL \u2014 {k} not PASS'); sys.exit(1)
if not d.get('required_tuple_list_untouched', False): print('FAIL \u2014 required_tuple_list_untouched must be true'); sys.exit(1)
if d.get('v100_supersede_targets_intersect_REQUIRED', True): print('FAIL \u2014 v100 supersede must NOT intersect REQUIRED'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('required_weakening','required_removal','required_fake_PASS'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v100 required invariant protection ({d['required_total']} REQUIRED protected, 0 weakened)")
sys.exit(0)
