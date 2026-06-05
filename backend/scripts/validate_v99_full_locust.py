#!/usr/bin/env python3
"""v99 — Full locust/load result validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'closed_alpha', 'v99_full_locust_result_v1.json')
if not os.path.isfile(p):
    print('FAIL \u2014 file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
if len(d.get('endpoints_covered', [])) < 13:
    print('FAIL \u2014 endpoints_covered < 13'); sys.exit(1)
m = d.get('metrics') or {}
if m.get('critical_5xx', 1) != 0:
    print('FAIL \u2014 critical_5xx != 0'); sys.exit(1)
if m.get('auth_leak_observed', True):
    print('FAIL \u2014 auth_leak_observed true'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('fake_load_result', 'fake_PASS', 'validator_weakening', 'production_target_used', 'raw_token_logs'):
    if saf.get(k, True):
        print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
if saf.get('db_economy_writes', 1) != 0:
    print('FAIL \u2014 db_economy_writes != 0'); sys.exit(1)
print(f"PASS \u2014 v99 full locust ({len(d.get('endpoints_covered', []))} endpoints, 0 critical errors, FULL_LOAD_REQUIRED honest)")
sys.exit(0)
