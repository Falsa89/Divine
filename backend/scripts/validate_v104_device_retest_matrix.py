#!/usr/bin/env python3
"""v104 — Device retest matrix validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v104_device_retest_matrix_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
matrix = d.get('matrix') or []
if len(matrix) < 11: print(f'FAIL \u2014 matrix steps < 11 (got {len(matrix)})'); sys.exit(1)
for i, step in enumerate(matrix):
    for k in ('step', 'action', 'expected'):
        if k not in step: print(f'FAIL \u2014 matrix step {i} missing field {k}'); sys.exit(1)
acc = d.get('acceptance') or {}
if acc.get('min_steps_pass_required', 0) < 9: print('FAIL \u2014 acceptance.min_steps_pass_required < 9'); sys.exit(1)
if len(acc.get('critical_steps', [])) < 6: print('FAIL \u2014 critical_steps < 6'); sys.exit(1)
if acc.get('banner_token_required') != 'SERVER_DATA_ISOLATION_BACKEND_PENDING': print('FAIL \u2014 banner_token_required missing'); sys.exit(1)
if '/servers' not in (acc.get('banner_must_be_visible_on') or []): print('FAIL \u2014 banner must be visible on /servers'); sys.exit(1)
if not d.get('manual_qa_required', False): print('FAIL \u2014 manual_qa_required must be true'); sys.exit(1)
forb = set(d.get('forbidden') or [])
for k in ('fake_per_server_data', 'random_heroes_per_server', 'premium_currency_grant_per_server'):
    if k not in forb: print(f'FAIL \u2014 forbidden missing {k}'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('fake_mobile_qa', 'fake_PASS', 'validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v104 device retest matrix ({len(matrix)} steps, manual QA required)")
sys.exit(0)
