#!/usr/bin/env python3
"""v95 — Validator: Inline Mirror Removal Result."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'playability_completion', 'v95_inline_mirror_removal_result_v1.json')
if not os.path.isfile(p):
    print('FAIL — file missing:', p); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
if not d.get('applied_runtime'):
    print('FAIL — applied_runtime false'); sys.exit(1)
if d.get('verdict') != 'INLINE_MIRROR_REMOVAL_RUNTIME_APPLIED_WITH_EXPLICIT_FALLBACK':
    print('FAIL — verdict mismatch:', d.get('verdict')); sys.exit(1)
for entry in d.get('files', []):
    fpath = os.path.join(ROOT, entry.get('file', ''))
    if not os.path.isfile(fpath):
        print('FAIL — missing frontend file:', fpath); sys.exit(1)
    with open(fpath, 'r', encoding='utf-8') as fh:
        src = fh.read()
    if 'endpoint_fetch_failed_fallback_local_readonly' not in src:
        print('FAIL — missing fallback label in', entry['file']); sys.exit(1)
    if 'v95' not in src:
        print('FAIL — missing v95 marker in', entry['file']); sys.exit(1)
print('PASS — v95 inline mirror removal applied with explicit fallback')
sys.exit(0)
