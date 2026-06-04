#!/usr/bin/env python3
"""v97 — Validator: Physical mobile QA matrix."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'internal_alpha', 'v97_physical_mobile_qa_matrix_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
m = d.get('matrix') or {}
for k in ('android_physical_device','ios_physical_device','login_guest_qa','session_restore','logout','logout_all','delete_account_request','refresh_token_rotation','formation_fetch_authenticated','battle_engine_smoke','15_modes_smoke','live_guild_qa_hub','live_announcements_qa','war_event_avatar_previews','guild_war_sandbox','contextual_bot_chat_demo'):
    if k not in m: print(f'FAIL — matrix missing: {k}'); sys.exit(1)
for pd in ('android_physical_device','ios_physical_device'):
    if m[pd].get('status') != 'MANUAL_QA_REQUIRED': print(f'FAIL — {pd} must be MANUAL_QA_REQUIRED (no fake)'); sys.exit(1)
modes = m['15_modes_smoke']
if len(modes) < 15: print('FAIL — fewer than 15 modes'); sys.exit(1)
print(f'PASS — v97 physical mobile QA matrix ({len(modes)} modes, physical=MANUAL)')
sys.exit(0)
