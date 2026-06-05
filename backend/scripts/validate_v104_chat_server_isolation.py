#!/usr/bin/env python3
"""v104 — Chat server isolation validator (declared pending)."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v104_chat_server_isolation_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
cs = d.get('current_state') or {}
if cs.get('chat_scoped_by_server_id', True): print('FAIL \u2014 current_state.chat_scoped_by_server_id must be false (honest)'); sys.exit(1)
if not cs.get('observed_duplication_across_S1_S2', False): print('FAIL \u2014 current_state.observed_duplication_across_S1_S2 must be true'); sys.exit(1)
contract = d.get('contract_when_implemented') or {}
if contract.get('channel_key_format') != '{server_id}:{channel_name}': print('FAIL \u2014 channel_key_format wrong'); sys.exit(1)
if not contract.get('server_id_required_in_send_payload', False): print('FAIL \u2014 contract.server_id_required_in_send_payload must be true'); sys.exit(1)
if d.get('isolation_status') != 'DECLARED_PENDING': print('FAIL \u2014 isolation_status must be DECLARED_PENDING'); sys.exit(1)
fx = d.get('acceptance_fixture') or {}
if len(fx) < 4: print('FAIL \u2014 acceptance_fixture must have >=4 steps'); sys.exit(1)
ui = d.get('ui_obligation_until_chat_implemented') or {}
if ui.get('banner_text') != 'SERVER_DATA_ISOLATION_BACKEND_PENDING': print('FAIL \u2014 banner_text token missing'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('fake_per_server_chat_data', 'fake_PASS', 'validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print('PASS \u2014 v104 chat server isolation (DECLARED_PENDING, contract documented)')
sys.exit(0)
