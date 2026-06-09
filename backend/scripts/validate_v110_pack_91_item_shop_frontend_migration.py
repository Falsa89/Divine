#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_91_inventory_frontend_consumer_and_smoke/v110_pack_91_item_shop_frontend_migration_v1.json')))
assert d.get('passes_server_id_query') is True
assert d.get('handles_server_id_required_blocker') is True
assert d.get('handles_player_server_profile_required_blocker') is True
assert d.get('no_account_wide_fallback') is True
assert d.get('no_silent_s1') is True
# Static check of the file content
fp = os.path.join(R, d['file'])
assert os.path.exists(fp)
src = open(fp).read()
assert '/api/item-shop/buy?' in src and 'server_id=' in src, src[:200]
assert 'SERVER_ID_REQUIRED' in src
assert 'PLAYER_SERVER_PROFILE_REQUIRED' in src
assert 'selected_server_id' in src
print('[v110 PACK_91_ITEM_SHOP_FRONTEND_MIGRATION] OK server_id_in_query blockers_handled no_silent_s1')
