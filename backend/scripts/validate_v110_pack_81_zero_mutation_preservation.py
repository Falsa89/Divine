#!/usr/bin/env python3
# Pack 81 - Track 11: zero mutation/economy preservation.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_81_user_heroes_server_scope/v110_pack_81_user_heroes_server_scope_summary_v1.json')
d = json.load(open(S))
z = d.get('zero_mutation_economy_preservation', {})
assert z.get('db_writes') == 0
for k in ('reward_grant','progress_advance','ledger_writes','premium_currency_grant','gacha_mutation','shop_mutation','vip_mutation','battle_pass_mutation'):
    assert z.get(k) is False, f'{k} must be false'
# Static: il route handler NON deve contenere write su user_heroes/PSP/economia
server_py = open(os.path.join(R, 'backend/server.py')).read()
# Estrai SOLO il corpo di get_user_heroes fino al prossimo def/async def/@app
start = server_py.index('async def get_user_heroes(')
rest = server_py[start:]
# trova la fine: prima occorrenza di "\n@" oppure "\nasync def " oppure "\ndef " dopo il primo carattere
end_candidates = []
for marker in ('\n@app.', '\n@router.', '\nasync def ', '\ndef '):
    idx = rest.find(marker, 100)  # skip first 100 chars to bypass the function's own def line
    if idx > 0:
        end_candidates.append(idx)
end = min(end_candidates) if end_candidates else len(rest)
fn_body = rest[:end]
for forbidden in ('insert_one', 'update_one', 'delete_one', 'replace_one', 'update_many', 'insert_many', 'delete_many'):
    assert forbidden not in fn_body, f'get_user_heroes contains forbidden DB write: {forbidden}'
print('[v110 PACK_81_ZERO_MUTATION_PRESERVATION] OK db_writes=0 no_economy_mutation route_handler_read_only')
