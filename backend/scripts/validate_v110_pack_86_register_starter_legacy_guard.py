#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_86_lobby_psp_ensure/v110_pack_86_register_starter_legacy_guard_v1.json')))
assert d.get('file_modified') == 'backend/server.py'
assert d.get('route') == 'POST /api/register'
beh = d.get('default_behavior_post_pack_86', {})
assert beh.get('starter_user_heroes_created') == 0
assert beh.get('global_roster_grant') is False
assert beh.get('premium_grant') is False
assert beh.get('reward_grant') is False
resp = beh.get('response_signals', {})
assert resp.get('server_onboarding_required') is True
assert resp.get('starter_flow_required') is True
assert resp.get('starter_legacy_created_in_register') == 0
flag = d.get('dev_only_flag', {})
assert flag.get('name') == 'REGISTER_LEGACY_STARTER_HEROES_ENABLED'
assert flag.get('default') == 'false'
assert d.get('starter_flow_approved_in_this_pack') is False
assert d.get('starter_heroes_created_in_this_pack') is False
# Verifica statica nel server.py: NESSUNA scrittura starter user_heroes per default
src = open(os.path.join(R, 'backend/server.py')).read()
start = src.index('@app.post("/api/register")')
end = src.index('@app.post("/api/login")')
register_block = src[start:end]
assert 'REGISTER_LEGACY_STARTER_HEROES_ENABLED' in register_block
assert 'starter_legacy_enabled' in register_block
assert 'server_onboarding_required' in register_block
assert 'starter_flow_required' in register_block
assert '_slc_pack_86_register_starter_legacy_guard' in register_block
# La insert_one user_heroes deve essere SOLO dentro l'if starter_legacy_enabled
# (cioe' non eseguita per default)
insert_idx = register_block.find('db.user_heroes.insert_one')
if insert_idx >= 0:
    # Insert presente: deve essere preceduto da if starter_legacy_enabled
    pre = register_block[:insert_idx]
    assert 'if starter_legacy_enabled' in pre, '/api/register: user_heroes insert MUST be gated by starter_legacy_enabled flag (default off)'
print('[v110 PACK_86_REGISTER_STARTER_LEGACY_GUARD] OK register_no_default_starter_creation dev_only_flag_default_off server_onboarding_required=true starter_flow_required=true')
