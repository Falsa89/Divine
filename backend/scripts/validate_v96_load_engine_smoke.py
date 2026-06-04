#!/usr/bin/env python3
"""v96 — Validator: Load/engine smoke."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'release_candidate', 'v96_load_and_engine_smoke_result_v1.json')
if not os.path.isfile(p):
    print('FAIL — file missing:', p); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
tests = d.get('low_impact_tests_executed') or []
if len(tests) < 8:
    print(f'FAIL — low_impact_tests count {len(tests)} < 8'); sys.exit(1)
for t in tests:
    if t.get('status') != 200:
        print(f"FAIL — test status != 200: {t}"); sys.exit(1)
eng = d.get('engine_smoke') or {}
if eng.get('result') != '21/21 PASS':
    print(f"FAIL — engine smoke result: {eng.get('result')}"); sys.exit(1)
safety = d.get('safety') or {}
for k in ('reward_live', 'ranking_live', 'production_broadcast'):
    if safety.get(k, True):
        print(f'FAIL — safety.{k} not false'); sys.exit(1)
print(f'PASS — v96 load/engine smoke ({len(tests)} endpoints)')
sys.exit(0)
