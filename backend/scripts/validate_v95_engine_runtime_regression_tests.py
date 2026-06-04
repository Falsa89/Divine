#!/usr/bin/env python3
"""v95 — Validator: Engine Runtime Regression Tests result.

Verifica che il test runner abbia prodotto data/design/battle_engine/v95_engine_runtime_apply_test_result_v1.json
con verdict == PASS e 0 failed.
"""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(ROOT, 'data', 'design', 'battle_engine', 'v95_engine_runtime_apply_test_result_v1.json')
if not os.path.isfile(path):
    print('FAIL — engine runtime regression result missing:', path)
    sys.exit(1)
with open(path, 'r', encoding='utf-8') as f:
    d = json.load(f)
if d.get('verdict') != 'PASS' or d.get('failed', 1) != 0:
    print('FAIL — engine runtime regression verdict:', d.get('verdict'), 'failed=', d.get('failed'))
    sys.exit(1)
print(f"PASS — v95 engine runtime regression: {d.get('passed')}/{d.get('total')}")
sys.exit(0)
