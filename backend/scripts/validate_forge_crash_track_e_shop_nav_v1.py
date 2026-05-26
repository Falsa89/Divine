#!/usr/bin/env python3
# FORGE_CRASH Track E — shop navigation buttons safe.
import json, sys
from pathlib import Path
J = Path('/app/data/design/soul_forge/forge_crash_track_e_shop_nav_buttons_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
SHOP = Path('/app/frontend/app/shop.tsx')
ITEM = Path('/app/frontend/app/item-shop.tsx')
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_E_SOUL_SHOP_NAVIGATION_BUTTONS_READY_SAFE'
    t = F.read_text()
    # New nav buttons present
    assert 'shop_navRow' in t, 'shop nav row style missing'
    assert 'shop_navBtn' in t, 'shop nav button style missing'
    assert 'shop_navBtnSecondary' in t, 'shop nav secondary button style missing'
    assert 'Apri Tesoreria' in t, 'Apri Tesoreria label missing'
    assert 'Vai al Negozio' in t, 'Vai al Negozio label missing'
    assert 'Apri Negozio Oggetti' in t, 'item-shop nav label missing'
    assert 'IN PREP' in t, 'In Preparazione disabled label missing'
    # Routes targeted are safe locked routes
    assert "router.push('/treasury')" in t
    assert "router.push('/shop')" in t
    assert "router.push('/item-shop')" in t
    # Lock guards on target screens are intact (no live buy enabled by this pack)
    st = SHOP.read_text()
    assert 'SHOP_LOCKED_V2 = true' in st, 'shop.tsx is not locked anymore!'
    it = ITEM.read_text()
    assert 'ITEM_SHOP_LOCKED_V2 = true' in it, 'item-shop.tsx is not locked anymore!'
    assert d['no_live_buy_enabled'] is True
    assert d['no_routing_to_legacy_economy_buy'] is True
    print('[PASS] FORGE_CRASH Track E shop nav buttons safe')
    return 0
if __name__ == '__main__': sys.exit(main())
