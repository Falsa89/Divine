#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_91_inventory_frontend_consumer_and_smoke/v110_pack_91_selected_server_source_adoption_v1.json')))
assert d.get('canonical_resolver') == 'frontend/src/hooks/useServerScope.ts'
assert d.get('silent_s1_fallback') is False
assert d.get('adoption_complete') is True
assert d.get('item_shop_uses_resolver') is True
assert d.get('inventory_uses_resolver') is True
resolver_path = os.path.join(R, d['canonical_resolver'])
assert os.path.exists(resolver_path)
print('[v110 PACK_91_SELECTED_SERVER_SOURCE_ADOPTION] OK canonical_resolver=useServerScope no_silent_s1 adoption_complete')
