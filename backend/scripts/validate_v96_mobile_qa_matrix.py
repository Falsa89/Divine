#!/usr/bin/env python3
"""v96 — Validator: Mobile QA matrix."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'release_candidate', 'v96_mobile_qa_matrix_v1.json')
if not os.path.isfile(p):
    print('FAIL — file missing:', p); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
m = d.get('matrix') or {}
for k in ('android_physical_device', 'ios_physical_device', 'google_login_dev_build', 'apple_login_ios_only', 'session_restore', 'logout', 'formation_fetch', 'pre_battle_with_real_formation', 'smoke_15_modes', 'live_guild_qa_hub', 'live_announcements_qa', 'engine_v95_battle_smoke'):
    if k not in m:
        print(f'FAIL — matrix missing: {k}'); sys.exit(1)
modes = m.get('smoke_15_modes') or {}
if len(modes) < 15:
    print(f'FAIL — smoke_15_modes count {len(modes)} < 15'); sys.exit(1)
if d.get('safety', {}).get('db_writes') != 0:
    print('FAIL — safety.db_writes != 0'); sys.exit(1)
print(f"PASS — v96 mobile QA matrix ({len(modes)} modes)")
sys.exit(0)
