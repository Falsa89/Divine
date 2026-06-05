#!/usr/bin/env python3
"""v103 — Device retest matrix validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','server_profile','v103_device_retest_matrix_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
matrix = d.get('matrix') or []
if len(matrix) < 10: print(f'FAIL \u2014 matrix steps < 10 (got {len(matrix)})'); sys.exit(1)
for i, step in enumerate(matrix):
    if 'action' not in step or 'expected' not in step: print(f'FAIL \u2014 matrix step {i} incomplete'); sys.exit(1)
acc = d.get('acceptance') or {}
if acc.get('min_steps_pass_required', 0) < 8: print('FAIL \u2014 acceptance.min_steps_pass_required < 8'); sys.exit(1)
if len(acc.get('critical_steps', [])) < 4: print('FAIL \u2014 critical_steps < 4'); sys.exit(1)
if not d.get('manual_qa_required', False): print('FAIL \u2014 manual_qa_required must be true'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('fake_mobile_qa','fake_PASS'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v103 device retest matrix ({len(matrix)} steps, manual QA required)")
sys.exit(0)
