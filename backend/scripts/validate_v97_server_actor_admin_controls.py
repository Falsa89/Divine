#!/usr/bin/env python3
"""v97 — Validator: Server actor admin controls + kill switches."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_actors', 'v97_server_actor_admin_controls_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
fields = d.get('admin_visibility_fields') or []
for k in ('is_bot','synthetic_server_actor','bot_archetype','bot_power_band_percentile','event_participation_status','chat_rate_limit_status'):
    if k not in fields: print(f'FAIL — admin visibility missing: {k}'); sys.exit(1)
ks = d.get('kill_switches') or {}
for k in ('disable_all_bots','disable_bot_chat','disable_bot_live_event_fill','disable_bot_ranking_visibility','cap_bot_power_percentile'):
    if k not in ks: print(f'FAIL — kill switch missing: {k}'); sys.exit(1)
safety = d.get('admin_safety_rules') or {}
for k in ('admin_panel_authenticated_only','audit_log_required','admin_can_distinguish_bots_from_real_players'):
    if not safety.get(k): print(f'FAIL — admin_safety.{k}'); sys.exit(1)
if safety.get('no_fake_users_presented_as_real', False) is not True: print('FAIL — no_fake_users_presented_as_real'); sys.exit(1)
print(f'PASS — v97 server actor admin controls ({len(ks)} kill switches)')
sys.exit(0)
