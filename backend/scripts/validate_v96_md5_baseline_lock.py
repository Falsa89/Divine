#!/usr/bin/env python3
"""v96 — Validator: MD5 v95 baseline lock."""
import os, sys, json, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'release_candidate', 'v96_md5_baseline_v95_lock_v1.json')
if not os.path.isfile(p):
    print('FAIL — file missing:', p); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
baseline = d.get('baseline') or {}
if baseline.get('backend/battle_engine.py') != '56b6e5261c3b35c421db3202f750d1a6':
    print('FAIL — battle_engine.py baseline MD5 mismatch'); sys.exit(1)
if baseline.get('backend/server.py_v95_snapshot') != 'df22b6599cbc5621e9f0edeb0dcf832a':
    print('FAIL — server.py v95 baseline MD5 mismatch'); sys.exit(1)
# verify battle_engine.py file md5 unchanged
be_path = os.path.join(ROOT, 'backend', 'battle_engine.py')
h = hashlib.md5()
with open(be_path, 'rb') as f:
    for c in iter(lambda: f.read(8192), b''): h.update(c)
if h.hexdigest() != '56b6e5261c3b35c421db3202f750d1a6':
    print(f'FAIL — battle_engine.py current MD5 {h.hexdigest()} != baseline'); sys.exit(1)
print('PASS — v96 MD5 v95 baseline lock')
sys.exit(0)
