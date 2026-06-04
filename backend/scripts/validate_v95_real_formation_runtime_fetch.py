#!/usr/bin/env python3
"""v95 — Validator: Real Formation Runtime Fetch.

Il real formation fetch via /api/team/get-formation NON è esposto: il risultato
dichiara CONDITIONAL / BLOCKER_FOR_RELEASE_CANDIDATE con chain dichiarata
e UI source label visibile.
"""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'playability_completion', 'v95_real_formation_runtime_fetch_result_v1.json')
if not os.path.isfile(p):
    print('FAIL — file missing:', p); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
required_chain = ['saved_formation', 'local_cached_formation', 'safe_fallback_formation']
if d.get('chain_implemented') != required_chain:
    print('FAIL — chain mismatch:', d.get('chain_implemented')); sys.exit(1)
if d.get('verdict') not in ('READY', 'CONDITIONAL'):
    print('FAIL — verdict invalid:', d.get('verdict')); sys.exit(1)
if d.get('verdict') == 'CONDITIONAL' and d.get('release_candidate_flag') != 'BLOCKER_FOR_RELEASE_CANDIDATE':
    print('FAIL — CONDITIONAL requires BLOCKER_FOR_RELEASE_CANDIDATE flag'); sys.exit(1)
if not d.get('ui_source_label_visible'):
    print('FAIL — ui_source_label_visible false'); sys.exit(1)
# Verifica UI label
ui = os.path.join(ROOT, 'frontend', 'app', 'pre-battle-lobby.tsx')
with open(ui, 'r', encoding='utf-8') as f:
    src = f.read()
if 'safe_fallback_formation' not in src or 'fallback_used' not in src:
    print('FAIL — UI label safe_fallback_formation/fallback_used missing'); sys.exit(1)
print(f"PASS — v95 real formation runtime fetch verdict={d.get('verdict')} flag={d.get('release_candidate_flag','-')}")
sys.exit(0)
