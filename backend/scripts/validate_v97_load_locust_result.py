#!/usr/bin/env python3
"""v97 — Validator: Load/locust result."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'internal_alpha', 'v97_load_locust_result_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
eps = d.get('endpoints_covered') or []
if len(eps) < 8: print(f'FAIL — endpoints_covered count {len(eps)} < 8'); sys.exit(1)
res = d.get('results') or {}
for k in ('no_5xx_under_light_load','no_token_leakage_in_logs','no_db_write_outside_auth_scope'):
    if not res.get(k): print(f'FAIL — results.{k} not true'); sys.exit(1)
if res.get('errors',1) != 0: print('FAIL — results.errors != 0'); sys.exit(1)
safety = d.get('safety') or {}
for k in ('reward_live','ranking_live','production_broadcast','random_opponents'):
    if safety.get(k, True): print(f'FAIL — safety.{k} not false'); sys.exit(1)
script = os.path.join(ROOT, 'backend', 'scripts', 'locust_v97_internal_alpha_smoke.py')
if not os.path.isfile(script): print('FAIL — locust script missing'); sys.exit(1)
print('PASS — v97 load/locust low-impact smoke')
sys.exit(0)
