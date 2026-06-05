#!/usr/bin/env python3
"""v105 — Backend endpoint inventory validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'master_audit', 'v105_backend_endpoint_inventory_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
summ = d.get('summary') or {}
if summm := summ:
    if summ.get('routers_registered', 0) < 20: print('FAIL \u2014 routers_registered < 20'); sys.exit(1)
    if summ.get('unique_endpoints', 0) < 100: print('FAIL \u2014 unique_endpoints < 100'); sys.exit(1)
if len(d.get('routers') or []) < 20: print('FAIL \u2014 routers list < 20'); sys.exit(1)
if len(d.get('critical_endpoints') or []) < 10: print('FAIL \u2014 critical_endpoints < 10'); sys.exit(1)
if len(d.get('observations') or []) < 3: print('FAIL \u2014 observations < 3'); sys.exit(1)
saf = d.get('forbidden_scope_compliance') or {}
for k in ('db_writes','new_endpoints_added','reward_mutation','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 forbidden_scope.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v105 backend endpoint inventory ({summ.get('routers_registered')} routers, {summ.get('unique_endpoints')} endpoints)")
sys.exit(0)
