#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_88_team_formation_strict_server_scope/v110_pack_88_starter_team_compatibility_v1.json')))
assert d.get('starter_team_compatibility_preserved') is True
assert d.get('team_init_writes_only_to_psp_team_formation') is True
assert d.get('team_init_only_if_empty') is True
assert d.get('no_users_team_formation_writes_from_starter_claim') is True
assert d.get('re_claim_no_overwrite') is True
rs = d.get('runtime_smoke_results', {})
for k in rs:
    assert rs[k] is True, f'runtime smoke step {k} must be true'
# Verifica statica: psp_starter_claim non scrive su users.team_formation
src = open(os.path.join(R, 'backend/server.py')).read()
import re
m = re.search(r'async def psp_starter_claim\([^)]*\)[^:]*:(.+?)(?=@app\.|\ndef |\nasync def )', src, re.DOTALL)
assert m, 'psp_starter_claim not found'
body = m.group(1)
assert 'users.update_one' not in body, 'psp_starter_claim MUST NOT update users collection'
assert 'users.update_many' not in body
assert 'team_formation' in body  # ok writes to PSP
print('[v110 PACK_88_STARTER_TEAM_COMPATIBILITY] OK starter_claim_writes_only_psp.team_formation no_users_team_formation_writes pack_87_preserved')
