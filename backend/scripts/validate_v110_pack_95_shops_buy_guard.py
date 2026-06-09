#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_95_reward_ledger_story_write_legacy_guards/v110_pack_95_shops_buy_guard_v1.json')))
assert d.get('endpoint') == '/api/shops/buy'
assert d.get('server_id_aware') is True
assert d.get('blocker_when_server_id') == 'SHOPS_BUY_SERVER_SCOPE_DEFERRED'
src = open(os.path.join(R, 'backend/routes/soul_forge.py')).read()
assert 'SHOPS_BUY_SERVER_SCOPE_DEFERRED' in src
assert '_slc_pack_95_shops_buy_quarantine' in src
print('[v110 PACK_95_SHOPS_BUY_GUARD] OK blocker_when_server_id legacy_unchanged')
