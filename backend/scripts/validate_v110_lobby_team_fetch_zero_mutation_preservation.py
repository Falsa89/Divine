#!/usr/bin/env python3
# Pack 80 — Track H: zero mutation / economy preservation.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_80_lobby_fetch/v110_pack_80_lobby_fetch_summary_v1.json')
d = json.load(open(S))
z = d.get('zero_mutation_economy_preservation', {})
assert z.get('db_writes') == 0
for k in ('reward_grant','progress_advance','ledger_writes','premium_currency_grant','gacha_mutation','shop_mutation','vip_mutation','battle_pass_mutation'):
    assert z.get(k) is False, f'{k} must be false'
print('[v110 LOBBY_TEAM_FETCH_ZERO_MUTATION_PRESERVATION] OK db_writes=0 no_reward_grant no_progress_advance no_economy_mutation')
