#!/usr/bin/env python3
"""v95 — Validator: Live Announcement Sandbox Runtime."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'live_announcements', 'v95_live_announcement_sandbox_runtime_result_v1.json')
if not os.path.isfile(p):
    print('FAIL — file missing:', p); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
sb = d.get('sandbox') or {}
for k in ('production_broadcast', 'push_notification_live', 'real_user_pii'):
    if sb.get(k, True):
        print(f'FAIL — sandbox.{k} not false'); sys.exit(1)
if not sb.get('alias_only') or sb.get('alias_namespace') != 'qa_alias_*':
    print('FAIL — alias-only / namespace invalid'); sys.exit(1)
anti = d.get('anti_spam') or {}
if anti.get('per_user_per_minute_max', 0) <= 0:
    print('FAIL — anti_spam.per_user_per_minute_max <= 0'); sys.exit(1)
bridge = d.get('event_bridge') or {}
for k in ('engine_events_generate_broadcast', 'reward_events_generate_broadcast', 'live_events_generate_broadcast'):
    if bridge.get(k, True):
        print(f'FAIL — event_bridge.{k} not false'); sys.exit(1)
print('PASS — v95 live announcement sandbox runtime')
sys.exit(0)
