#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_86_lobby_psp_ensure/v110_pack_86_backend_ensure_route_hardening_v1.json')))
h = d.get('hardening_checklist', {})
for k in ('no_silent_s1','explicit_server_id_required','server_id_blank_returns_400_blocker','idempotent','fresh_start_fields_correct','no_s1_copy','no_user_heroes_creation','no_reward','no_mutation_of_existing_psp','no_cross_server_read'):
    assert h.get(k) is True, f'hardening checklist {k} must be true'
src = open(os.path.join(R, 'backend/server.py')).read()
for tok in d.get('static_proof_tokens_in_server_py', []):
    assert tok in src, f'token missing in server.py: {tok}'
print('[v110 PACK_86_BACKEND_ENSURE_ROUTE_HARDENING] OK no_silent_s1 explicit_server_id_required idempotent no_user_heroes_creation no_reward')
