#!/usr/bin/env python3
"""v107A — /api/battle/launch endpoint validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'battle_launch', 'v107a_battle_launch_endpoint_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
if d.get('endpoint') != 'POST /api/battle/launch': print('FAIL \u2014 endpoint wrong'); sys.exit(1)
rf = os.path.join(ROOT, d.get('router_file',''))
if not os.path.isfile(rf): print(f'FAIL \u2014 router file missing: {rf}'); sys.exit(1)
content = open(rf, 'r', encoding='utf-8').read()
for token in ('PREVIEW_ECHO_NON_AUTHORITATIVE','BATTLE_LAUNCH_AUTHORITATIVE_ENABLED','REWARD_LIVE_ENABLED','PROGRESS_LIVE_ENABLED','SERVER_SCOPED_RUNTIME_ENABLED','idempotency_key_required_for_live_gated_or_live','db_writes_performed'):
    if token not in content: print(f'FAIL \u2014 router missing token: {token}'); sys.exit(1)
# Verify server.py registers it
srv = open(os.path.join(ROOT, 'backend', 'server.py'), 'r', encoding='utf-8').read()
if 'v107a_battle_launch_router' not in srv: print('FAIL \u2014 server.py missing router include'); sys.exit(1)
flags = d.get('feature_flags_default') or {}
for k in ('BATTLE_LAUNCH_AUTHORITATIVE_ENABLED','REWARD_LIVE_ENABLED','PROGRESS_LIVE_ENABLED','SERVER_SCOPED_RUNTIME_ENABLED'):
    if flags.get(k, True): print(f'FAIL \u2014 default flag {k} must be false'); sys.exit(1)
if d.get('db_writes_performed', -1) != 0: print('FAIL \u2014 db_writes_performed must be 0'); sys.exit(1)
if d.get('reward_granted', True): print('FAIL \u2014 reward_granted must be false'); sys.exit(1)
if d.get('progress_written', True): print('FAIL \u2014 progress_written must be false'); sys.exit(1)
if d.get('server_id_used_as_backend_filter', True): print('FAIL \u2014 server_id_used_as_backend_filter must be false'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('no_db_writes','no_reward_grant','no_progress_write','no_currency_mutation'):
    if not saf.get(k, False): print(f'FAIL \u2014 safety.{k} must be true'); sys.exit(1)
for k in ('battle_engine_runtime_modified','combat_tsx_modified','fake_PASS','validator_weakening','hiding_preview_state'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print('PASS \u2014 v107A /api/battle/launch endpoint (preview echo, 0 db writes, all flags off)')
sys.exit(0)
