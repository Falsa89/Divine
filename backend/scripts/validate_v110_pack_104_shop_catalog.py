#!/usr/bin/env python3
"""Pack 104 — Shop strict catalog server-side: no premium, capped, deterministic."""
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend'))
from data.shop_strict_catalog_v1 import SHOP_STRICT_CATALOG_V1, CATALOG_VERSION, get_item

assert CATALOG_VERSION.startswith('shop_strict_catalog_v1')
FORBIDDEN = {'gems','premium_pull','standard_pull','stamina','experience'}
ALLOWED = {'gold','honor','guild_points','mission_coins','dimension_frags','prana','soul_seals','star_dust'}

for sid, shop in SHOP_STRICT_CATALOG_V1.items():
    assert sid == shop['shop_id']
    assert isinstance(shop['items'], list) and len(shop['items']) >= 1
    for it in shop['items']:
        for k, v in it['cost'].items():
            assert k in ALLOWED and k not in FORBIDDEN, f'forbidden cost key: {it["id"]}.{k}'
            assert 0 < v <= 5000
        for k, v in it['grant'].items():
            assert k in ALLOWED and k not in FORBIDDEN, f'forbidden grant key: {it["id"]}.{k}'
            assert 0 < v <= 1000
        assert it['daily_purchase_limit'] >= 1

# get_item lookup test (deterministic).
it = get_item('honor_exchange_shop','honor_to_mission_coins_pack_small')
assert it and it['cost'] == {'honor': 20} and it['grant'] == {'mission_coins': 30}
it2 = get_item('honor_exchange_shop','nope')
assert it2 is None

print('[v110 PACK_104_SHOP_CATALOG] OK deterministic no_premium soft_only capped lookup_works')
